import numpy as np
from pydub import AudioSegment

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