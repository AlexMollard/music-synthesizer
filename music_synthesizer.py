#  OLD SCRIPT

import numpy as np
from pydub.generators import Sine, Square, Triangle, Sawtooth
from pydub import AudioSegment
from pydub.playback import play
import keyboard
import threading

import simpleaudio as sa

import argparse
import threading
import keyboard
import sys
import json
from typing import List, Union, Dict
import time

# Note frequencies dictionary
NOTE_FREQUENCIES = {
    # Lower octave
    "C2": 65.41, "D2": 73.42, "E2": 82.41, "F2": 87.31, "G2": 98.00, "A2": 110.00, "B2": 123.47,
    "Bb2": 116.54, "Eb2": 77.78,
    
    # Bass octave
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94,
    "Bb3": 233.08, "Eb3": 155.56,
    
    # Middle octave
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "Bb4": 466.16, "Eb4": 311.13,
    
    # Higher octave
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "A5": 880.00, "B5": 987.77,
    "Bb5": 932.33, "Eb5": 622.25,
    
    "REST": 0
}

class Instrument:
    def __init__(self, name, attack_ms=10, decay_ms=10, sustain_level=0.7, release_ms=10):
        self.name = name
        self.attack_ms = attack_ms
        self.decay_ms = decay_ms
        self.sustain_level = sustain_level
        self.release_ms = release_ms
        
        # Define instrument-specific parameters
        self.params = {
            'electric_bass': {
                'wave_type': ['sawtooth', 'sine'],  # Multiple waveforms for richer sound
                'wave_mix': [0.7, 0.3],  # Mix ratios
                'attack_ms': 15,
                'decay_ms': 150,
                'sustain_level': 0.65,
                'release_ms': 200,
                'octave_shift': -1,
                'detune_cents': 5
            },
            'acoustic_guitar': {
                'wave_type': ['triangle', 'sine', 'square'],
                'wave_mix': [0.6, 0.3, 0.1],
                'attack_ms': 8,
                'decay_ms': 100,
                'sustain_level': 0.5,
                'release_ms': 150,
                'octave_shift': 0,
                'body_resonance': True
            },
            'piano': {
                'wave_type': ['complex'],
                'harmonics': [1.0, 0.5, 0.33, 0.25, 0.2, 0.15],
                'attack_ms': 5,
                'decay_ms': 150,
                'sustain_level': 0.4,
                'release_ms': 200,
                'octave_shift': 0,
                'string_resonance': True
            },
            'xylophone': {
                'wave_type': ['sine', 'triangle'],
                'wave_mix': [0.8, 0.2],
                'attack_ms': 2,
                'decay_ms': 250,
                'sustain_level': 0.2,
                'release_ms': 100,
                'octave_shift': 1,
                'bright_attack': True
            },
            'bongos': {
                'wave_type': ['noise'],
                'resonance_freq': [200, 400],
                'attack_ms': 2,
                'decay_ms': 150,
                'sustain_level': 0.1,
                'release_ms': 150,
                'filter_q': 2.5
            },
            'claves': {
                'wave_type': ['sine', 'noise'],
                'wave_mix': [0.9, 0.1],
                'attack_ms': 1,
                'decay_ms': 60,
                'sustain_level': 0.05,
                'release_ms': 60,
                'octave_shift': 0,
                'click_emphasis': True
            }
        }
        
        # Default attributes
        self.wave_type = 'sine'
        self.wave_mix = [1.0]
        self.octave_shift = 0
        self.detune_cents = 0
        self.body_resonance = False
        self.string_resonance = False
        self.bright_attack = False
        self.resonance_freq = [200]
        self.filter_q = 1.0
        self.harmonics = [1.0]
        
        # Update with instrument-specific parameters if available
        if name in self.params:
            params = self.params[name]
            for key, value in params.items():
                setattr(self, key, value)

class Note:
    def __init__(self, pitch, duration_ms, instrument, volume=0.8):
        self.pitch = pitch
        self.duration_ms = duration_ms
        self.instrument = instrument
        self.volume = volume

class Chord:
    def __init__(self, notes):
        self.notes = notes


def generate_instrument_tone(frequency, instrument, duration_ms, volume):
    """Generate a tone with enhanced instrument characteristics"""
    base_volume = -12  # Slightly lower base volume for better headroom
    volume_adjustment = -20 * (1.0 - volume)
    volume_db = base_volume + volume_adjustment
    
    def create_generator(wave_type, freq):
        """Helper function to create a generator based on wave type"""
        if wave_type == 'sine':
            return Sine(freq)
        elif wave_type == 'square':
            return Square(freq)
        elif wave_type == 'triangle':
            return Triangle(freq)
        elif wave_type == 'sawtooth':
            return Sawtooth(freq)
        elif wave_type == 'noise':
            return None  # Handle noise separately
        else:
            return Sine(freq)  # Default to sine
    
    # Handle percussion instruments
    if hasattr(instrument, 'wave_type') and (
        (isinstance(instrument.wave_type, list) and 'noise' in instrument.wave_type) or
        instrument.wave_type == 'noise'
    ):
        return generate_enhanced_percussion(instrument, duration_ms, volume_db)
    
    # Handle piano's complex tone
    if hasattr(instrument, 'wave_type') and instrument.wave_type == 'complex':
        return generate_piano_tone(frequency, duration_ms, volume_db, instrument)
    
    # Handle multi-waveform instruments
    if hasattr(instrument, 'wave_type') and isinstance(instrument.wave_type, list):
        segments = []
        for i, wave in enumerate(instrument.wave_type):
            generator = create_generator(wave, frequency)
            if generator is None:
                continue
                
            mix_volume = volume_db
            if hasattr(instrument, 'wave_mix') and len(instrument.wave_mix) > i:
                mix_volume += (20 * np.log10(instrument.wave_mix[i]))
                
            segment = generator.to_audio_segment(duration=duration_ms).apply_gain(mix_volume)
            
            # Apply detuning if specified
            if hasattr(instrument, 'detune_cents') and i > 0:
                detune_factor = 2 ** (instrument.detune_cents / 1200)
                detuned_freq = frequency * detune_factor
                detuned = Sine(detuned_freq).to_audio_segment(duration=duration_ms).apply_gain(mix_volume - 3)
                segment = segment.overlay(detuned)
                
            segments.append(segment)
        
        if segments:
            audio = mix_audio(*segments)
        else:
            # Fallback to simple sine wave if no valid segments
            generator = Sine(frequency)
            audio = generator.to_audio_segment(duration=duration_ms).apply_gain(volume_db)
    else:
        # Handle single waveform
        wave_type = getattr(instrument, 'wave_type', 'sine')
        if isinstance(wave_type, list):
            wave_type = wave_type[0]
        
        generator = create_generator(wave_type, frequency)
        audio = generator.to_audio_segment(duration=duration_ms).apply_gain(volume_db)
    
    # Apply additional instrument-specific processing
    if hasattr(instrument, 'body_resonance') and instrument.body_resonance:
        audio = apply_body_resonance(audio)
    if hasattr(instrument, 'string_resonance') and instrument.string_resonance:
        audio = apply_string_resonance(audio, frequency)
    if hasattr(instrument, 'bright_attack') and instrument.bright_attack:
        audio = apply_bright_attack(audio)
        
    return audio

def generate_enhanced_percussion(instrument, duration_ms, volume_db):
    """Generate enhanced percussion sounds with better realism"""
    if instrument.name == 'bongos':
        # Create layered percussion with multiple resonant frequencies
        noise = AudioSegment.silent(duration=duration_ms)
        
        # Generate filtered noise for each resonant frequency
        for freq in instrument.resonance_freq:
            # Create resonant filter effect
            t = np.linspace(0, duration_ms/1000, int(44100 * duration_ms/1000))
            decay = np.exp(-5 * t)  # Faster decay for transient
            wave = np.sin(2 * np.pi * freq * t) * decay
            
            # Add some noise for attack
            noise_factor = np.random.rand(len(wave)) * decay * 0.3
            wave += noise_factor
            
            # Convert to audio segment
            samples = np.int16(wave * 32767)
            partial = AudioSegment(
                samples.tobytes(),
                frame_rate=44100,
                sample_width=2,
                channels=1
            )
            
            noise = noise.overlay(partial)
            
        return noise.apply_gain(volume_db)
        
    elif instrument.name == 'claves':
        # Enhanced claves sound with click and resonance
        duration = min(duration_ms, 60)  # Keep it short
        t = np.linspace(0, duration/1000, int(44100 * duration/1000))
        
        # Sharp attack with quick decay
        decay = np.exp(-50 * t)
        wave = np.sin(2 * np.pi * 2500 * t) * decay
        
        # Add click
        click_duration = int(44100 * 0.005)  # 5ms click
        click = np.random.rand(click_duration) * 0.5
        wave[:click_duration] += click
        
        # Convert to audio segment
        samples = np.int16(wave * 32767)
        audio = AudioSegment(
            samples.tobytes(),
            frame_rate=44100,
            sample_width=2,
            channels=1
        )
        
        return audio.apply_gain(volume_db)

def generate_piano_tone(frequency, duration_ms, volume_db, instrument):
    """Generate enhanced piano tone with realistic harmonics"""
    harmonics = []
    for i, strength in enumerate(instrument.harmonics):
        harmonic_freq = frequency * (i + 1)
        volume_adjustment = 20 * np.log10(strength)
        harmonic = Sine(harmonic_freq).to_audio_segment(duration=duration_ms)
        harmonic = harmonic.apply_gain(volume_db + volume_adjustment)
        harmonics.append(harmonic)
        
    # Add subtle inharmonicity for higher notes
    if frequency > 500:
        inharmonic_freq = frequency * 2.002  # Slightly sharp second harmonic
        inharmonic = Sine(inharmonic_freq).to_audio_segment(duration=duration_ms)
        inharmonic = inharmonic.apply_gain(volume_db - 12)
        harmonics.append(inharmonic)
    
    return mix_audio(*harmonics)

def apply_enhanced_envelope(audio_segment, instrument):
    """Apply more sophisticated ADSR envelope with curves"""
    samples = np.array(audio_segment.get_array_of_samples())
    sample_rate = audio_segment.frame_rate
    
    # Convert times to samples
    attack_samples = int(instrument.attack_ms * sample_rate / 1000)
    decay_samples = int(instrument.decay_ms * sample_rate / 1000)
    release_samples = int(instrument.release_ms * sample_rate / 1000)
    
    total_samples = len(samples)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    # Ensure minimal envelope phases
    if sustain_samples < 0:
        attack_samples = int(total_samples * 0.1)
        decay_samples = int(total_samples * 0.2)
        release_samples = int(total_samples * 0.3)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    # Create envelope with curves
    envelope = np.ones(total_samples)
    
    # Attack phase (exponential curve)
    if attack_samples > 0:
        attack_curve = np.power(np.linspace(0, 1, attack_samples), 0.7)
        envelope[:attack_samples] = attack_curve
    
    # Decay phase (exponential curve)
    if decay_samples > 0:
        decay_end = attack_samples + decay_samples
        decay_curve = np.power(
            np.linspace(1, instrument.sustain_level, decay_samples), 0.5
        )
        envelope[attack_samples:decay_end] = decay_curve
    
    # Sustain phase (slight variation)
    sustain_end = decay_end + sustain_samples
    sustain_curve = np.linspace(
        instrument.sustain_level,
        instrument.sustain_level * 0.95,
        sustain_samples
    )
    envelope[decay_end:sustain_end] = sustain_curve
    
    # Release phase (exponential curve)
    if release_samples > 0:
        release_curve = np.power(
            np.linspace(sustain_curve[-1], 0, release_samples), 0.3
        )
        envelope[sustain_end:] = release_curve
    
    # Apply envelope with smoothing
    smoothed_envelope = np.convolve(envelope, np.ones(32)/32, mode='same')
    samples = samples * smoothed_envelope
    
    return AudioSegment(
        samples.astype(np.int16).tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def mix_audio(*audio_segments):
    """Enhanced audio mixing with better gain staging"""
    if not audio_segments:
        return AudioSegment.silent(duration=0)
    
    max_length = max(len(segment) for segment in audio_segments)
    normalized_segments = []
    
    for segment in audio_segments:
        if len(segment) < max_length:
            silence = AudioSegment.silent(duration=max_length - len(segment))
            normalized_segments.append(segment + silence)
        else:
            normalized_segments.append(segment)
    
    # Mix with gradual gain reduction based on number of segments
    mixed = normalized_segments[0]
    if len(normalized_segments) > 1:
        gain_reduction = -3 * np.log2(len(normalized_segments))  # Progressive reduction
        
        for segment in normalized_segments[1:]:
            mixed = mixed.overlay(segment)
            mixed = mixed.apply_gain(gain_reduction)
    
    return mixed

def apply_body_resonance(audio):
    """
    Simulate acoustic guitar body resonance by adding characteristic resonant frequencies
    and harmonic content typical of a guitar body cavity.
    """
    # Get audio data
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))
    
    # Define body resonance frequencies (typical for acoustic guitar)
    resonance_freqs = [100, 200, 400, 800]  # Hz
    resonance = np.zeros_like(samples, dtype=float)
    
    # Create resonant frequencies with different decay rates
    for freq in resonance_freqs:
        # Slower decay for lower frequencies
        decay_rate = 2 + (freq / 200)  # Higher frequencies decay faster
        decay = np.exp(-decay_rate * t)
        
        # Add some slight randomness to the resonance
        phase = np.random.uniform(0, 2 * np.pi)
        resonance += np.sin(2 * np.pi * freq * t + phase) * decay * (100/freq)
    
    # Normalize and scale resonance
    resonance = resonance / np.max(np.abs(resonance))
    resonance *= 0.15  # Adjust resonance intensity
    
    # Mix with original audio
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)
    
    # Create new audio segment
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_string_resonance(audio, frequency):
    """
    Add sympathetic string resonance for piano by simulating the behavior
    of other strings vibrating in response to the played note.
    """
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))
    
    # Calculate harmonically related frequencies
    harmonics = [1.0, 2.0, 3.0, 4.0, 5.0]  # Harmonic series
    resonance = np.zeros_like(samples, dtype=float)
    
    for harmonic in harmonics:
        harmonic_freq = frequency * harmonic
        
        # Higher harmonics have faster decay and lower amplitude
        decay_rate = 3 + (harmonic * 2)
        amplitude = 1.0 / harmonic
        
        # Add slight detuning for more natural sound
        detune_factor = 1.0 + (np.random.uniform(-0.0001, 0.0001) * harmonic)
        
        decay = np.exp(-decay_rate * t)
        resonance += amplitude * np.sin(2 * np.pi * harmonic_freq * detune_factor * t) * decay
    
    # Normalize and scale resonance
    resonance = resonance / np.max(np.abs(resonance))
    resonance *= 0.1  # Adjust resonance intensity
    
    # Mix with original audio
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)
    
    # Add subtle high-frequency content
    if frequency > 200:
        noise = np.random.normal(0, 0.01, len(samples))
        noise_decay = np.exp(-10 * t)  # Fast decay for noise
        high_freq = noise * noise_decay * 32767 * 0.02
        enhanced_samples = enhanced_samples + high_freq.astype(np.int16)
    
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_bright_attack(audio):
    """
    Enhance attack brightness for xylophone by adding high-frequency content
    and shaping the attack envelope.
    """
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    
    # Calculate attack portion (first 50ms)
    attack_duration = min(int(0.05 * sample_rate), len(samples))
    
    # Generate bright attack characteristics
    t_attack = np.linspace(0, 1, attack_duration)
    
    # Create high-frequency content for attack
    bright_attack = np.zeros_like(samples, dtype=float)
    
    # Add multiple high frequencies with different phases
    for freq in [5000, 7000, 9000]:
        phase = np.random.uniform(0, 2 * np.pi)
        bright_attack[:attack_duration] += np.sin(2 * np.pi * freq * t_attack + phase)
    
    # Shape attack envelope
    attack_env = np.exp(-10 * t_attack)  # Sharp decay
    bright_attack[:attack_duration] *= attack_env
    
    # Normalize and scale bright attack
    bright_attack = bright_attack / np.max(np.abs(bright_attack))
    bright_attack *= 0.3  # Adjust intensity
    
    # Add noise burst at the very beginning
    noise_duration = int(0.01 * sample_rate)  # 10ms noise burst
    noise = np.random.normal(0, 1, noise_duration)
    noise_env = np.exp(-20 * np.linspace(0, 1, noise_duration))
    bright_attack[:noise_duration] += noise * noise_env * 0.2
    
    # Mix with original audio
    enhanced_samples = samples + (bright_attack * 32767).astype(np.int16)
    
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_body_resonance(audio):
    """Simulate acoustic guitar body resonance"""
    # Create body resonance frequencies
    resonance_freqs = [100, 200, 400]  # Common body resonance frequencies
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))
    
    resonance = np.zeros_like(samples, dtype=float)
    for freq in resonance_freqs:
        decay = np.exp(-3 * t)  # Slower decay for resonance
        resonance += np.sin(2 * np.pi * freq * t) * decay * 0.1
    
    # Mix original audio with resonance
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)
    
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_string_resonance(audio, frequency):
    """Add sympathetic string resonance for piano"""
    # Calculate harmonically related frequencies
    harmonic_freqs = [frequency * i for i in range(2, 5)]
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))
    
    resonance = np.zeros_like(samples, dtype=float)
    for freq in harmonic_freqs:
        decay = np.exp(-5 * t)  # Faster decay for string resonance
        resonance += np.sin(2 * np.pi * freq * t) * decay * 0.05
    
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)
    
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_bright_attack(audio):
    """Enhance attack brightness for xylophone"""
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    
    # Add high-frequency content to the attack
    attack_duration = int(0.02 * sample_rate)  # 20ms attack
    attack_enhancement = np.random.rand(attack_duration) * 0.3
    if len(samples) > attack_duration:
        samples[:attack_duration] += (attack_enhancement * 32767).astype(np.int16)
    
    return AudioSegment(
        samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def parse_sheet_music(sheet_music):
    """Parse sheet music with enhanced mixing, effects, and section support"""
    # Calculate total duration accounting for all sections
    total_duration = 0
    for track in sheet_music:
        track_duration = 0
        for item in track:
            if isinstance(item, Note):
                track_duration += item.duration_ms
            elif isinstance(item, Chord):
                track_duration += max(note.duration_ms for note in item.notes)
        total_duration = max(total_duration, track_duration)
    
    # Process each track
    tracks = []
    for track_idx, track in enumerate(sheet_music):
        track_audio = AudioSegment.silent(duration=total_duration)
        current_position = 0
        
        for item in track:
            if isinstance(item, Note):
                if item.pitch == "REST":
                    current_position += item.duration_ms
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
                
                if chord_notes:
                    chord_audio = mix_audio(*chord_notes)
                    if track_idx % 2 == 0:
                        chord_audio = chord_audio.pan(0.2)
                    else:
                        chord_audio = chord_audio.pan(-0.2)
                    track_audio = track_audio.overlay(chord_audio, position=current_position)
                current_position += max(note.duration_ms for note in item.notes)
        
        tracks.append(track_audio)
    
    # Final mix with crossfading between sections
    final_audio = AudioSegment.silent(duration=total_duration)
    for track in tracks:
        final_audio = final_audio.overlay(track)
    
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

def play_with_loop(melody, stop_event=None, skip_event=None):
    """
    Play audio with looping using pydub's play function
    """

    # Convert to raw audio data
    raw_data = np.array(melody.get_array_of_samples())
    sample_rate = melody.frame_rate
    channels = melody.channels
    sample_width = melody.sample_width

    # Create a playback object
    play_obj = sa.play_buffer(
        raw_data,
        num_channels=channels,
        bytes_per_sample=sample_width,
        sample_rate=sample_rate
    )

    try:
        while True:
            if stop_event and stop_event.is_set():
                play_obj.stop()
                break

            if not play_obj.is_playing():
                # Start new playback when previous one finishes
                play_obj = sa.play_buffer(
                    raw_data,
                    num_channels=channels,
                    bytes_per_sample=sample_width,
                    sample_rate=sample_rate
                )

            if skip_event and skip_event.is_set():
                play_obj.stop()
                skip_event.clear()
                continue

            time.sleep(0.1)

    except KeyboardInterrupt:
        if play_obj.is_playing():
            play_obj.stop()
        raise

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Generate music from JSON sheet music')
    parser.add_argument('json_file', help='Path to the JSON sheet music file')
    parser.add_argument('--output', '-o', default='output.wav',
                       help='Output WAV file path (default: output.wav)')
    parser.add_argument('--play', '-p', action='store_true',
                       help='Play the music after generating')
    parser.add_argument('--loops', '-l', type=int,
                       help='Override number of loops specified in JSON')
    args = parser.parse_args()
    
    try:
        # Define instruments
        instruments = {
            'bass': Instrument('electric_bass'),
            'guitar': Instrument('acoustic_guitar'),
            'piano': Instrument('piano'),
            'xylophone': Instrument('xylophone'),
            'bongos': Instrument('bongos'),
            'claves': Instrument('claves')
        }
        
        # Load JSON data first to check for metadata
        with open(args.json_file, 'r') as f:
            json_data = json.load(f)
        
        # Override loops if specified in command line
        if args.loops is not None:
            if 'metadata' not in json_data:
                json_data['metadata'] = {}
            json_data['metadata']['loops'] = args.loops
        
        # Load and parse sheet music
        print(f"\nLoading sheet music from {args.json_file}...")
        sheet_music = load_sheet_music_from_json(args.json_file, instruments)
        
        # Generate the audio
        print("Generating music...")
        melody = parse_sheet_music(sheet_music)
        
        # Export with high-quality settings
        print(f"Exporting to {args.output}...")
        melody.export(args.output, format="wav", 
                     parameters=["-ar", "44100", "-ab", "192k", "-ac", "2"])
        print("Successfully exported audio file")
        
        if args.play:
            print("\nPlaying music...")
            print("Press 'q' to stop playback")
            print("Press 'n' to skip to next loop")
            
            stop_playback = threading.Event()
            skip_to_next = threading.Event()
            
            def on_press(key):
                if key.name == 'q':
                    print("\nStopping playback...")
                    stop_playback.set()
                elif key.name == 'n':
                    print("\nSkipping to next loop...")
                    skip_to_next.set()
            
            keyboard.on_press(on_press)
            
            try:
                play_with_loop(melody, stop_playback, skip_to_next)
            finally:
                keyboard.unhook_all()
                print("\nPlayback ended")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)