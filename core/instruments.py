# Updated instrument parameters for better sound quality
INSTRUMENTS_PARAMS = {
    'electric_bass': {
        'wave_type': ['sine', 'triangle', 'sine'],
        'wave_mix': [0.5, 0.3, 0.2],
        'attack_ms': 25,
        'decay_ms': 200,
        'sustain_level': 0.6,
        'release_ms': 300,
        'octave_shift': -1,
        'detune_cents': 3,
        'harmonics': [1.0, 0.5, 0.25, 0.125],
        'body_resonance': True
    },
    'acoustic_guitar': {
        'wave_type': ['triangle', 'sine', 'sine', 'square'],
        'wave_mix': [0.45, 0.3, 0.2, 0.05],
        'attack_ms': 15,
        'decay_ms': 180,
        'sustain_level': 0.4,
        'release_ms': 250,
        'octave_shift': 0,
        'body_resonance': True,
        'harmonics': [1.0, 0.6, 0.3, 0.15],
        'detune_cents': 2
    },
    'piano': {
        'wave_type': ['complex'],
        'harmonics': [1.0, 0.6, 0.4, 0.25, 0.15, 0.1, 0.08],
        'attack_ms': 8,
        'decay_ms': 200,
        'sustain_level': 0.35,
        'release_ms': 300,
        'octave_shift': 0,
        'string_resonance': True,
        'resonance_freq': [220, 440, 880],
        'detune_cents': 1
    },
    'xylophone': {
        'wave_type': ['sine', 'triangle', 'sine'],
        'wave_mix': [0.5, 0.3, 0.2],
        'attack_ms': 3,
        'decay_ms': 300,
        'sustain_level': 0.15,
        'release_ms': 150,
        'octave_shift': 1,
        'bright_attack': True,
        'harmonics': [1.0, 0.7, 0.4, 0.2],
        'resonance_freq': [1200, 2400, 3600]
    },
    'bongos': {
        'wave_type': ['noise', 'sine', 'sine'],
        'wave_mix': [0.6, 0.25, 0.15],
        'resonance_freq': [180, 360, 540],
        'attack_ms': 3,
        'decay_ms': 200,
        'sustain_level': 0.08,
        'release_ms': 180,
        'filter_q': 3.5,
        'body_resonance': True
    },
    'claves': {
        'wave_type': ['sine', 'noise', 'sine'],
        'wave_mix': [0.7, 0.15, 0.15],
        'attack_ms': 2,
        'decay_ms': 80,
        'sustain_level': 0.04,
        'release_ms': 80,
        'octave_shift': 0,
        'click_emphasis': True,
        'resonance_freq': [2400, 4800],
        'filter_q': 4.0
    }
}

class Instrument:
    def __init__(self, name, attack_ms=10, decay_ms=10, sustain_level=0.7, release_ms=10):
        self.name = name
        self.attack_ms = attack_ms
        self.decay_ms = decay_ms
        self.sustain_level = sustain_level
        self.release_ms = release_ms

        # Define instrument-specific parameters
        self.params = INSTRUMENTS_PARAMS

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

# Define available instruments
AVAILABLE_INSTRUMENTS = {
    'bass': Instrument('electric_bass'),
    'guitar': Instrument('acoustic_guitar'),
    'piano': Instrument('piano'),
    'xylophone': Instrument('xylophone'),
    'bongos': Instrument('bongos'),
    'claves': Instrument('claves')
}