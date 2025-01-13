class Note:
    def __init__(self, pitch, duration_ms, instrument, volume=0.8):
        self.pitch = pitch
        self.duration_ms = duration_ms
        self.instrument = instrument
        self.volume = volume


class Chord:
    def __init__(self, notes):
        self.notes = notes