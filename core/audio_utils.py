import numpy as np
from pydub.generators import Sine, Square, Triangle, Sawtooth
from pydub import AudioSegment
import simpleaudio as sa
import time

def generate_instrument_tone(frequency, instrument, duration_ms, volume):
    """Generate a tone with enhanced instrument characteristics"""
    # if the instrument is none, return a silent audio segment with the duration
    if instrument.name == 'none':
        return AudioSegment.silent(duration=duration_ms)

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
    """Generate enhanced percussion with more realistic characteristics"""
    if instrument.name == 'bongos':
        # Create multiband resonance for more realistic bongo sound
        noise = AudioSegment.silent(duration=duration_ms)
        sample_rate = 44100
        t = np.linspace(0, duration_ms/1000, int(sample_rate * duration_ms/1000))
        
        # Main membrane resonance
        for freq in instrument.resonance_freq:
            # Non-linear decay for more natural sound
            decay = np.exp(-8 * t) * (1 + np.sin(2 * np.pi * 2 * t)) * 0.5
            wave = np.sin(2 * np.pi * freq * t) * decay
            
            # Add overtones
            for overtone in [2.1, 3.2, 4.7]:  # Non-integer overtones for realism
                overtone_freq = freq * overtone
                overtone_amp = 1.0 / (overtone * 2)
                wave += np.sin(2 * np.pi * overtone_freq * t) * decay * overtone_amp
            
            # Add initial strike transient
            strike_duration = int(0.005 * sample_rate)
            strike = np.random.normal(0, 1, strike_duration) * np.exp(-100 * np.linspace(0, 1, strike_duration))
            wave[:strike_duration] += strike * 0.5
            
            # Add subtle noise throughout
            noise_factor = np.random.rand(len(wave)) * decay * 0.2
            wave += noise_factor
            
            samples = np.int16(wave * 32767)
            partial = AudioSegment(
                samples.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            noise = noise.overlay(partial)

        return noise.apply_gain(volume_db)

    elif instrument.name == 'claves':
        sample_rate = 44100
        duration = min(duration_ms, 80)  # Slightly longer for more resonance
        t = np.linspace(0, duration/1000, int(sample_rate * duration/1000))
        
        # Main resonant frequency with overtones
        wave = np.zeros_like(t)
        frequencies = [2500, 5200, 7800]  # Multiple resonant frequencies
        amplitudes = [1.0, 0.3, 0.1]      # Relative amplitudes
        decays = [50, 60, 70]             # Different decay rates
        
        for freq, amp, decay in zip(frequencies, amplitudes, decays):
            wave += amp * np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)
        
        # Add realistic wood impact
        click_duration = int(0.002 * sample_rate)  # Shorter, sharper click
        click = np.random.rand(click_duration)
        click_env = np.exp(-200 * np.linspace(0, 1, click_duration))
        wave[:click_duration] += click * click_env * 2.0
        
        # Add subtle wood resonance
        wood_freq = 1200
        wood_resonance = np.sin(2 * np.pi * wood_freq * t) * np.exp(-30 * t) * 0.1
        wave += wood_resonance
        
        samples = np.int16(wave * 32767)
        return AudioSegment(
            samples.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        ).apply_gain(volume_db)


def generate_piano_tone(frequency, duration_ms, volume_db, instrument):
    """Generate enhanced piano tone with realistic harmonics and string resonance"""
    harmonics = []
    
    # Main harmonics with more natural decay
    for i, strength in enumerate(instrument.harmonics):
        harmonic_freq = frequency * (i + 1)
        # Higher harmonics decay faster
        decay_factor = np.exp(-0.5 * i)  
        volume_adjustment = 20 * np.log10(strength * decay_factor)
        
        # Add slight detuning for more natural sound
        detune = 1.0 + (np.random.uniform(-0.0001, 0.0001) * (i + 1))
        harmonic_freq *= detune
        
        harmonic = Sine(harmonic_freq).to_audio_segment(duration=duration_ms)
        harmonic = harmonic.apply_gain(volume_db + volume_adjustment)
        
        # Add dynamic filtering based on velocity
        if volume > 0.7:  # Harder strikes have more high harmonics
            high_freq_boost = 3 * (volume - 0.7)
            harmonic = harmonic.apply_gain(high_freq_boost)
        
        harmonics.append(harmonic)

    # Add sympathetic resonance for higher notes
    if frequency > 500:
        # Multiple inharmonic frequencies for rich high notes
        inharmonic_freqs = [
            frequency * 2.002,  # Slight sharp
            frequency * 1.998,  # Slight flat
            frequency * 2.015   # Higher partial
        ]
        for inharm_freq in inharmonic_freqs:
            inharmonic = Sine(inharm_freq).to_audio_segment(duration=duration_ms)
            inharmonic = inharmonic.apply_gain(volume_db - 15)
            harmonics.append(inharmonic)

    mixed = mix_audio(*harmonics)
    
    # Add initial attack transient for more realism
    attack_duration = min(int(0.02 * 44100), len(mixed.get_array_of_samples()))
    attack_noise = np.random.normal(0, 0.1, attack_duration)
    attack_env = np.exp(-20 * np.linspace(0, 1, attack_duration))
    attack_samples = (attack_noise * attack_env * 32767).astype(np.int16)
    
    attack_segment = AudioSegment(
        attack_samples.tobytes(),
        frame_rate=44100,
        sample_width=2,
        channels=1
    ).apply_gain(volume_db)
    
    return mixed.overlay(attack_segment)


def mix_audio(*audio_segments):
    """Enhanced audio mixing with better dynamics and stereo field"""
    if not audio_segments:
        return AudioSegment.silent(duration=0)

    # Normalize lengths
    max_length = max(len(segment) for segment in audio_segments)
    normalized_segments = []

    for segment in audio_segments:
        if len(segment) < max_length:
            # Crossfade silence for smoother transitions
            fade_duration = min(100, len(segment))  # 100ms fade or shorter
            silence = AudioSegment.silent(duration=max_length - len(segment))
            if fade_duration > 0:
                segment = segment.fade_out(fade_duration)
                silence = silence.fade_in(fade_duration)
            normalized_segments.append(segment + silence)
        else:
            normalized_segments.append(segment)

    # Apply subtle stereo enhancement
    stereo_width = 0.3  # Adjust stereo width
    for i, segment in enumerate(normalized_segments):
        # Create subtle stereo positioning
        pan_position = ((i % 3) - 1) * stereo_width
        normalized_segments[i] = segment.pan(pan_position)

    # Mix with dynamic gain staging
    mixed = normalized_segments[0]
    if len(normalized_segments) > 1:
        # Calculate gain reduction based on number of tracks
        gain_reduction = -2 * np.log2(len(normalized_segments))
        
        for segment in normalized_segments[1:]:
            mixed = mixed.overlay(segment)
            mixed = mixed.apply_gain(gain_reduction)

        # Apply gentle compression for better cohesion
        samples = np.array(mixed.get_array_of_samples())
        peak = np.max(np.abs(samples))
        if peak > 0:
            ratio = 2.0  # Compression ratio
            threshold = 0.7  # Threshold relative to peak
            threshold_val = threshold * 32767
            
            # Avoid divide by zero by masking zero samples
            nonzero_mask = np.abs(samples) > 0
            gain_reduction = np.ones_like(samples, dtype=float)
            
            # Only process non-zero samples
            above_threshold = np.abs(samples) > threshold_val
            gain_reduction[above_threshold & nonzero_mask] = (
                (threshold_val + (np.abs(samples[above_threshold & nonzero_mask]) - threshold_val) / ratio) /
                np.abs(samples[above_threshold & nonzero_mask])
            )
            
            samples = (samples * gain_reduction).astype(np.int16)
            
            mixed = AudioSegment(
                samples.tobytes(),
                frame_rate=mixed.frame_rate,
                sample_width=mixed.sample_width,
                channels=mixed.channels
            )

    return mixed

def apply_body_resonance(audio):
    """Simulate acoustic instrument body resonance with more realistic characteristics"""
    # Define body resonance frequencies for different materials
    wood_resonances = [
        (100, 0.15, 3),   # Low wood resonance
        (200, 0.12, 4),   # Mid wood resonance
        (400, 0.08, 5),   # High wood resonance
        (800, 0.04, 6)    # Upper wood resonance
    ]
    
    # Air cavity resonances
    cavity_resonances = [
        (150, 0.1, 2),    # Main cavity mode
        (300, 0.05, 3)    # Secondary cavity mode
    ]
    
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))

    # Combined resonance
    resonance = np.zeros_like(samples, dtype=float)
    
    # Add wood resonances
    for freq, amp, decay_rate in wood_resonances:
        decay = np.exp(-decay_rate * t)
        # Add slight frequency modulation for more natural sound
        mod = 1 + 0.001 * np.sin(2 * np.pi * 3 * t)
        resonance += amp * np.sin(2 * np.pi * freq * t * mod) * decay

    # Add cavity resonances
    for freq, amp, decay_rate in cavity_resonances:
        decay = np.exp(-decay_rate * t)
        resonance += amp * np.sin(2 * np.pi * freq * t) * decay

    # Add some non-linear response
    resonance += 0.1 * resonance * resonance * np.sign(resonance)
    
    # Normalize and mix
    resonance = resonance / np.max(np.abs(resonance))
    enhanced_samples = samples + (resonance * 32767 * 0.2).astype(np.int16)
    
    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

def apply_string_resonance(audio, frequency):
    """Enhanced string resonance simulation with sympathetic vibrations"""
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    duration_s = len(samples) / sample_rate
    t = np.linspace(0, duration_s, len(samples))

    # More complex harmonic structure
    harmonics = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    resonance = np.zeros_like(samples, dtype=float)

    # Add main harmonics with natural variations
    for i, harmonic in enumerate(harmonics):
        harmonic_freq = frequency * harmonic
        # Progressive decay rates
        decay_rate = 3 + (harmonic * 2)
        # Decreasing amplitude for higher harmonics
        amplitude = 1.0 / (harmonic ** 1.5)
        
        # Add slight detuning for more natural sound
        detune_factor = 1.0 + (np.random.uniform(-0.0002, 0.0002) * harmonic)
        
        # Add slight pitch variation over time
        pitch_mod = 1 + 0.0001 * np.sin(2 * np.pi * 0.5 * t)
        
        decay = np.exp(-decay_rate * t)
        resonance += amplitude * np.sin(
            2 * np.pi * harmonic_freq * detune_factor * pitch_mod * t
        ) * decay

    # Add longitudinal modes for high frequencies
    if frequency > 200:
        long_modes = [1.5, 2.5, 3.5]  # Non-integer modes
        for mode in long_modes:
            mode_freq = frequency * mode
            decay = np.exp(-8 * t)
            amplitude = 0.05 / mode
            resonance += amplitude * np.sin(2 * np.pi * mode_freq * t) * decay

    # Normalize and add subtle compression
    resonance = resonance / np.max(np.abs(resonance))
    resonance = np.tanh(resonance * 1.5) * 0.15  # Soft clipping for warmth
    enhanced_samples = samples + (resonance * 32767).astype(np.int16)

    # Add subtle noise component for high frequencies
    if frequency > 200:
        noise = np.random.normal(0, 0.005, len(samples))
        noise_decay = np.exp(-15 * t)
        high_freq = noise * noise_decay * 32767 * 0.02
        enhanced_samples = enhanced_samples + high_freq.astype(np.int16)

    return AudioSegment(
        enhanced_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )


def apply_bright_attack(audio):
    """Optimized attack brightness for xylophone"""
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    
    # Reduce attack duration for faster processing
    attack_duration = min(int(0.03 * sample_rate), len(samples))
    t_attack = np.linspace(0, 1, attack_duration)
    bright_attack = np.zeros(attack_duration, dtype=float)

    # Use fewer frequencies and combine them more efficiently
    phase = np.random.uniform(0, 2 * np.pi)
    bright_attack += np.sin(2 * np.pi * 7000 * t_attack + phase)
    
    # Simplified envelope
    attack_env = np.exp(-12 * t_attack)
    bright_attack *= attack_env

    # Normalize and scale in one step
    max_val = np.max(np.abs(bright_attack))
    if max_val > 0:
        bright_attack *= (0.3 / max_val)

    # Add shorter noise burst
    noise_duration = int(0.01 * sample_rate)  # 10ms noise burst
    noise = np.random.normal(0, 0.2, noise_duration)
    noise *= np.exp(-25 * np.linspace(0, 1, noise_duration))
    
    # Combine with original audio more efficiently
    result_samples = samples.copy()
    result_samples[:attack_duration] += (bright_attack * 32767).astype(np.int16)
    if noise_duration > 0:
        result_samples[:noise_duration] += (noise * 32767).astype(np.int16)

    return AudioSegment(
        result_samples.tobytes(),
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

def convert_wav_to_mp3(wav_file, mp3_file):
    """Convert WAV file to MP3 using pydub"""
    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format='mp3')