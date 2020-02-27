tones = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


class RhythmKey:
    def __init__(self, rhythm_key_map, bpm, bpm_offset, chord):
        self.rhythm_key_map = rhythm_key_map
        self.bpm = bpm
        self.bpm_offset = bpm_offset / 1000
        self.measure = 4
        self.beat_time = (60 / self.bpm) * self.measure
        self.music_len = self.bpm_offset + (len(chord) * (1 / ((self.bpm / 60) * 2)))

    def keyLabel(self):
        times = []

        intime = 0.0
        inkey = ""

        if len(self.rhythm_key_map) < 2:
            times.append([self.bpm_offset, self.music_len, tones[self.rhythm_key_map[-1][-1]]])
            return times

        for i, frame in enumerate(self.rhythm_key_map):
            intime_ = (self.beat_time * frame[0]) + self.bpm_offset
            inkey_ = frame[-1]
            if i == 0:
                inkey = inkey_
                intime = intime_
                continue

            if intime != intime_ and inkey != inkey_:
                times.append([intime, intime_, tones[inkey]])
                inkey = inkey_
                intime = intime_

        times.append([intime, self.music_len, tones[inkey]])

        return times
