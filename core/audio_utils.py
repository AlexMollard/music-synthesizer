import numpy as np
from pydub.generators import Sine, Square, Triangle, Sawtooth
from pydub import AudioSegment
import simpleaudio as sa
import time

def generate_instrument_tone(frequency, instrument, duration_ms, volume):
    """Generate a tone with enhanced instrument characteristics"""
    base_volume = -12
    volume_adjustment = -20 * (1.0 - volume)
    volume_db = base_volume + volume_adjustment

    def create_generator(wave_type, freq):
        if wave_type == 'sine':
            return Sine(freq)
        elif wave_type == 'square':
            return Square(freq)
        elif wave_type == 'triangle':
            return Triangle(freq)
        elif wave_type == 'sawtooth':
            return Sawtooth(freq)
        elif wave_type == 'noise':
            return None
        else:
            return Sine(freq)

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

            if hasattr(instrument, 'detune_cents') and i > 0:
                detune_factor = 2 ** (instrument.detune_cents / 1200)
                detuned_freq = frequency * detune_factor
                detuned = Sine(detuned_freq).to_audio_segment(duration=duration_ms).apply_gain(mix_volume - 3)
                segment = segment.overlay(detuned)

            segments.append(segment)

        if segments:
            audio = mix_audio(*segments)
        else:
            generator = Sine(frequency)
            audio = generator.to_audio_segment(duration=duration_ms).apply_gain(volume_db)
    else:
        wave_type = getattr(instrument, 'wave_type', 'sine')
        if isinstance(wave_type, list):
            wave_type = wave_type[0]

        generator = create_generator(wave_type, frequency)
        audio = generator.to_audio_segment(duration=duration_ms).apply_gain(volume_db)

    # Apply instrument-specific effects
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
        noise = AudioSegment.silent(duration=duration_ms)

        for freq in instrument.resonance_freq:
            t = np.linspace(0, duration_ms/1000, int(44100 * duration_ms/1000))
            decay = np.exp(-5 * t)
            wave = np.sin(2 * np.pi * freq * t) * decay
            noise_factor = np.random.rand(len(wave)) * decay * 0.3
            wave += noise_factor
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
        duration = min(duration_ms, 60)
        t = np.linspace(0, duration/1000, int(44100 * duration/1000))
        decay = np.exp(-50 * t)
        wave = np.sin(2 * np.pi * 2500 * t) * decay
        click_duration = int(44100 * 0.005)
        click = np.random.rand(click_duration) * 0.5
        wave[:click_duration] += click
        samples = np.int16(wave * 32767)
        return AudioSegment(
            samples.tobytes(),
            frame_rate=44100,
            sample_width=2,
            channels=1
        ).apply_gain(volume_db)


def generate_piano_tone(frequency, duration_ms, volume_db, instrument):
    """Generate enhanced piano tone with realistic harmonics"""
    harmonics = []
    for i, strength in enumerate(instrument.harmonics):
        harmonic_freq = frequency * (i + 1)
        volume_adjustment = 20 * np.log10(strength)
        harmonic = Sine(harmonic_freq).to_audio_segment(duration=duration_ms)
        harmonic = harmonic.apply_gain(volume_db + volume_adjustment)
        harmonics.append(harmonic)

    if frequency > 500:
        inharmonic_freq = frequency * 2.002
        inharmonic = Sine(inharmonic_freq).to_audio_segment(duration=duration_ms)
        inharmonic = inharmonic.apply_gain(volume_db - 12)
        harmonics.append(inharmonic)

    return mix_audio(*harmonics)


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

    mixed = normalized_segments[0]
    if len(normalized_segments) > 1:
        gain_reduction = -3 * np.log2(len(normalized_segments))

        for segment in normalized_segments[1:]:
            mixed = mixed.overlay(segment)
            mixed = mixed.apply_gain(gain_reduction)

    return mixed


def apply_body_resonance(audio):
    """Simulate acoustic guitar body resonance"""
    resonance_freqs = [100, 200, 400]
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))

    resonance = np.zeros_like(samples, dtype=float)
    for freq in resonance_freqs:
        decay = np.exp(-3 * t)
        resonance += np.sin(2 * np.pi * freq * t) * decay * 0.1

    enhanced_samples = samples + (resonance * 32767).astype(np.int16)
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )


def apply_string_resonance(audio, frequency):
    """Add sympathetic string resonance for piano"""
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))

    harmonics = [1.0, 2.0, 3.0, 4.0, 5.0]
    resonance = np.zeros_like(samples, dtype=float)

    for harmonic in harmonics:
        harmonic_freq = frequency * harmonic
        decay_rate = 3 + (harmonic * 2)
        amplitude = 1.0 / harmonic
        detune_factor = 1.0 + (np.random.uniform(-0.0001, 0.0001) * harmonic)
        decay = np.exp(-decay_rate * t)
        resonance += amplitude * np.sin(2 * np.pi * harmonic_freq * detune_factor * t) * decay

    resonance = resonance / np.max(np.abs(resonance))
    resonance *= 0.1
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)

    if frequency > 200:
        noise = np.random.normal(0, 0.01, len(samples))
        noise_decay = np.exp(-10 * t)
        high_freq = noise * noise_decay * 32767 * 0.02
        enhanced_samples = enhanced_samples + high_freq.astype(np.int16)

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
    attack_duration = min(int(0.05 * sample_rate), len(samples))
    t_attack = np.linspace(0, 1, attack_duration)
    bright_attack = np.zeros_like(samples, dtype=float)

    for freq in [5000, 7000, 9000]:
        phase = np.random.uniform(0, 2 * np.pi)
        bright_attack[:attack_duration] += np.sin(2 * np.pi * freq * t_attack + phase)

    attack_env = np.exp(-10 * t_attack)
    bright_attack[:attack_duration] *= attack_env
    bright_attack = bright_attack / np.max(np.abs(bright_attack))
    bright_attack *= 0.3

    noise_duration = int(0.01 * sample_rate)
    noise = np.random.normal(0, 1, noise_duration)
    noise_env = np.exp(-20 * np.linspace(0, 1, noise_duration))
    bright_attack[:noise_duration] += noise * noise_env * 0.2

    enhanced_samples = samples + (bright_attack * 32767).astype(np.int16)
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )


def play_with_loop(melody, stop_event=None, skip_event=None):
    """Play audio with looping using simpleaudio"""
    raw_data = np.array(melody.get_array_of_samples())
    sample_rate = melody.frame_rate
    channels = melody.channels
    sample_width = melody.sample_width

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