import numpy as np
from pydub import AudioSegment

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

    # Add subtle high-frequency content for higher notes
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
    attack_duration = min(int(0.05 * sample_rate), len(samples))
    t_attack = np.linspace(0, 1, attack_duration)
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