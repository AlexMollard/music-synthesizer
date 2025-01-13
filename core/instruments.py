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
                'wave_type': ['sawtooth', 'sine'],
                'wave_mix': [0.7, 0.3],
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

# Define available instruments
AVAILABLE_INSTRUMENTS = {
    'bass': Instrument('electric_bass'),
    'guitar': Instrument('acoustic_guitar'),
    'piano': Instrument('piano'),
    'xylophone': Instrument('xylophone'),
    'bongos': Instrument('bongos'),
    'claves': Instrument('claves')
}