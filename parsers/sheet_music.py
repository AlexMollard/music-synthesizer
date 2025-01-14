import json
from typing import List, Union, Dict, Tuple
from pydub import AudioSegment

from core.notes import Note, Chord
from core.audio_utils import generate_instrument_tone, mix_audio
from effects.envelope import apply_enhanced_envelope
from core.constants import NOTE_FREQUENCIES
from core.instruments import Instrument

import concurrent.futures
import threading
import time

def process_track(track_info: Tuple[int, List, int, int, Dict[str, int]]) -> Tuple[int, AudioSegment]:
    """Process a single track in a separate thread"""
    track_idx, track, total_duration, track_note_count, note_counts = track_info
    
    print(f"[Track {track_idx + 1}] Starting: {track[0].instrument.name}")
    track_audio = AudioSegment.silent(duration=total_duration)
    current_position = 0
    track_progress = 0
    
    for item in track:
        if isinstance(item, Note):
            if item.pitch == "REST":
                current_position += item.duration_ms
                track_progress += 1
                continue
            
            frequency = NOTE_FREQUENCIES.get(item.pitch, 0)
            if frequency > 0:
                note_audio = generate_instrument_tone(
                    frequency,
                    item.instrument,
                    item.duration_ms,
                    item.volume
                )
                note_audio = apply_enhanced_envelope(note_audio, item.instrument)
                
                # Pan different tracks slightly for width
                if track_idx % 2 == 0:
                    note_audio = note_audio.pan(0.2)
                else:
                    note_audio = note_audio.pan(-0.2)
                
                track_audio = track_audio.overlay(note_audio, position=current_position)
            
            current_position += item.duration_ms
            track_progress += 1
            
        elif isinstance(item, Chord):
            chord_notes = []
            for note in item.notes:
                frequency = NOTE_FREQUENCIES.get(note.pitch, 0)
                if frequency > 0:
                    note_audio = generate_instrument_tone(
                        frequency,
                        note.instrument,
                        note.duration_ms,
                        note.volume
                    )
                    note_audio = apply_enhanced_envelope(note_audio, note.instrument)
                    chord_notes.append(note_audio)
                track_progress += 1
            
            if chord_notes:
                chord_audio = mix_audio(*chord_notes)
                if track_idx % 2 == 0:
                    chord_audio = chord_audio.pan(0.2)
                else:
                    chord_audio = chord_audio.pan(-0.2)
                track_audio = track_audio.overlay(chord_audio, position=current_position)
            
            current_position += max(note.duration_ms for note in item.notes)
        
        # Update progress
        track_percentage = (track_progress / track_note_count) * 100
        print(f"[Track {track_idx + 1}] Progress: {track_percentage:.1f}%")
    
    print(f"[Track {track_idx + 1}] Completed")
    return track_idx, track_audio

def parse_sheet_music(sheet_music):
    """Multithreaded sheet music parser with enhanced mixing and effects"""
    print("Analyzing sheet music structure...")
    
    # set the terminal title
    print("\033]0;Sheet Music Parser\007", end="")

    # Calculate total duration and count notes
    total_duration = 0
    note_counts = {}  # Track note counts per track
    total_notes = 0
    
    for track_idx, track in enumerate(sheet_music):
        track_duration = 0
        track_note_count = 0
        for item in track:
            if isinstance(item, Note):
                track_duration += item.duration_ms
                track_note_count += 1
            elif isinstance(item, Chord):
                duration = max(note.duration_ms for note in item.notes)
                track_duration += duration
                track_note_count += len(item.notes)
        total_duration = max(total_duration, track_duration)
        note_counts[track_idx] = track_note_count
        total_notes += track_note_count
    
    print(f"Total duration: {total_duration/1000:.1f} seconds")
    print(f"Total notes: {total_notes}\n")
    
    # Prepare track information for parallel processing
    track_infos = [
        (idx, track, total_duration, note_counts[idx], note_counts)
        for idx, track in enumerate(sheet_music)
    ]
    
    # Process tracks in parallel
    processed_tracks = {}
    max_workers = min(len(sheet_music), 4)  # Limit max threads
    
    print(f"Processing {len(sheet_music)} tracks using {max_workers} threads...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all track processing tasks
        future_to_track = {
            executor.submit(process_track, track_info): track_info[0]
            for track_info in track_infos
        }
        
        # Monitor for Ctrl+C
        while True:
            try:
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_track):
                    track_idx, track_audio = future.result()
                    processed_tracks[track_idx] = track_audio
                break
            except KeyboardInterrupt:
                print("\nCtrl+C detected. Cancelling...")
                executor.shutdown(wait=False, cancel_futures=True)
                return None
    
    print("\nAll tracks processed!")
    
    # Final mix
    print("Performing final mix...")
    final_audio = AudioSegment.silent(duration=total_duration)
    
    # Mix tracks in order
    for track_idx in range(len(sheet_music)):
        print(f"Mixing track {track_idx + 1}/{len(sheet_music)} "
              f"({((track_idx + 1)/len(sheet_music))*100:.1f}%)")
        final_audio = final_audio.overlay(processed_tracks[track_idx])
    
    print("Audio generation complete!")
    return final_audio


def load_sheet_music_from_json(json_path: str, instruments: Dict[str, 'Instrument']) -> List[List[Union['Note', 'Chord']]]:
    """
    Load and parse sheet music from a JSON file with metadata and sections support.
    Now properly handles repeated sections by duplicating the notes.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Sheet music file not found: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {json_path}")

    if not isinstance(data, dict):
        raise ValueError("Invalid JSON structure")

    # Extract metadata
    metadata = data.get('metadata', {'loops': 1, 'tempo': 120})
    num_loops = metadata.get('loops', 1)

    # Handle old format (no sections)
    if 'tracks' in data:
        sheet_music = []
        for track_data in data['tracks']:
            if 'instrument' not in track_data or 'notes' not in track_data:
                raise ValueError("Each track must specify 'instrument' and 'notes'")

            instrument_name = track_data['instrument']
            if instrument_name not in instruments:
                raise ValueError(f"Unknown instrument: {instrument_name}")

            instrument = instruments[instrument_name]
            track = []

            # Duplicate notes for each loop
            for _ in range(num_loops):
                for note_data in track_data['notes']:
                    if isinstance(note_data, dict):
                        if note_data.get('type') == 'chord':
                            if 'notes' not in note_data:
                                raise ValueError("Chord must contain 'notes' array")
                            chord_notes = []
                            for chord_note in note_data['notes']:
                                chord_notes.append(parse_note(chord_note, instrument))
                            track.append(Chord(chord_notes))
                        else:
                            track.append(parse_note(note_data, instrument))
                    else:
                        raise ValueError("Invalid note data format")

            sheet_music.append(track)

        return sheet_music

    # New format with sections
    if 'sections' not in data:
        raise ValueError("JSON must contain either 'tracks' or 'sections' array")

    sheet_music = []

    # First, process each section and create track templates
    section_tracks = []
    for section in data['sections']:
        if 'tracks' not in section:
            continue

        tracks_in_section = []
        for track_data in section['tracks']:
            if 'instrument' not in track_data or 'notes' not in track_data:
                continue

            instrument_name = track_data['instrument']
            if instrument_name not in instruments:
                continue

            instrument = instruments[instrument_name]
            track = []

            for note_data in track_data['notes']:
                if isinstance(note_data, dict):
                    if note_data.get('type') == 'chord':
                        if 'notes' in note_data:
                            chord_notes = []
                            for chord_note in note_data['notes']:
                                chord_notes.append(parse_note(chord_note, instrument))
                            track.append(Chord(chord_notes))
                    else:
                        track.append(parse_note(note_data, instrument))

            tracks_in_section.append(track)

        if tracks_in_section:
            section_tracks.append({
                'tracks': tracks_in_section,
                'repeat': section.get('repeat', False)
            })

    # Now create the final sheet music with proper repeats
    final_tracks = [[] for _ in range(len(section_tracks[0]['tracks']))]

    # For each section
    for section_data in section_tracks:
        repeat_count = num_loops if section_data['repeat'] else 1

        # For each repeat of the section
        for _ in range(repeat_count):
            # For each track in the section
            for track_idx, track in enumerate(section_data['tracks']):
                # Add all notes from this track
                final_tracks[track_idx].extend(track)

    return final_tracks

def parse_note(note_data: dict, instrument: 'Instrument') -> 'Note':
    """Parse a single note from JSON data"""
    required_fields = ['pitch', 'duration']
    for field in required_fields:
        if field not in note_data:
            raise ValueError(f"Note missing required field: {field}")

    pitch = note_data['pitch']
    duration = note_data['duration']
    volume = note_data.get('volume', 0.7)  # Default volume if not specified

    return Note(pitch, duration, instrument, volume)