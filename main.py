#!/usr/bin/env python3

# At the top of main.py

import sys
sys.path.append("..")

from parsers.sheet_music import load_sheet_music_from_json, parse_sheet_music


from core.notes import Note, Chord
from core.audio_utils import generate_instrument_tone, mix_audio, play_with_loop, convert_wav_to_mp3
from effects.envelope import apply_enhanced_envelope
from core.constants import NOTE_FREQUENCIES
from core.instruments import Instrument, AVAILABLE_INSTRUMENTS

import argparse
import threading
import keyboard
import os

def main():
    parser = argparse.ArgumentParser(description='Generate music from JSON sheet music')
    parser.add_argument('json_file', help='Path to the JSON sheet music file')
    parser.add_argument('--output', '-o', default='output.wav',
                       help='Output WAV file path (default: output.wav)')
    parser.add_argument('--play', '-p', action='store_true',
                       help='Play the music after generating')
    parser.add_argument('--loops', '-l', type=int,
                       help='Override number of loops specified in JSON')
    parser.add_argument('--list-instruments', '-i', action='store_true',
                       help='List available instruments and exit')
    args = parser.parse_args()

    try:
        # List instruments if requested
        if args.list_instruments:
            print("\nAvailable instruments:")
            for name in sorted(AVAILABLE_INSTRUMENTS.keys()):
                print(f"  - {name}")
            return 0

        # Load and parse sheet music
        print(f"\nLoading sheet music from {args.json_file}...")
        sheet_music = load_sheet_music_from_json(args.json_file, AVAILABLE_INSTRUMENTS)

        # Generate the audio
        print("Generating music...")
        melody = parse_sheet_music(sheet_music)

        # Export with high-quality settings
        print(f"Exporting to {args.output}...")
        melody.export(args.output, format="wav", parameters=["-ar", "44100", "-ab", "192k", "-ac", "2"])
        print("Successfully exported audio file")

        # convert the wav to a mp3
        print(f"Converting to {args.output.replace('.wav', '.mp3')}...")
        convert_wav_to_mp3(args.output, args.output.replace('.wav', '.mp3'))
        print("Successfully converted audio file")

        # remove the old wav file
        print(f"Removing {args.output}...")
        os.remove(args.output)
        print("Successfully removed audio file")

        if args.play:
            print("\nPlaying music...")
            print("Press 'q' to stop playback")
            print("Press 'n' to skip to next loop")
            print("Press 'Ctrl+C' to exit")

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
            except KeyboardInterrupt:
                print("\nPlayback interrupted by user")
            finally:
                keyboard.unhook_all()
                print("\nPlayback ended")

        return 0

    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())