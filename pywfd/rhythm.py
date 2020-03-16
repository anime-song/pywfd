class RhythmKey:
    def __init__(self, rhythm_key_map, chord):
        self.raw_rhythm_key_map = rhythm_key_map
        self.rhythm_key_map = self._convert_rhythm_key_map(
            self.raw_rhythm_key_map, chord)
        self.chord = chord

    def _convert_rhythm_key_map(self, raw_rhythm_key_map, chord):
        rhythm_key_map = []

        for i in range(len(raw_rhythm_key_map)):
            if i == len(raw_rhythm_key_map) - 1:
                rmp = raw_rhythm_key_map[i][1:]
                if raw_rhythm_key_map[i][-1] > 12:
                    rmp[-1] = 12
                loop = int(len(chord) - len(rhythm_key_map))
                for j in range(loop):
                    rhythm_key_map.append(rmp)
                break

            loop = int(raw_rhythm_key_map[i + 1][0] - raw_rhythm_key_map[i][0]) * raw_rhythm_key_map[i][1] * 2
            rmp = raw_rhythm_key_map[i][1:]
            if raw_rhythm_key_map[i][-1] > 12:
                rmp[-1] = 12
            for j in range(loop):
                
                rhythm_key_map.append(rmp)

        return rhythm_key_map


class TempoMap:

    def __init__(self, tempomap, rhythmkey, beat_offset, k=960):
        self.raw_tempomap = tempomap
        self.rhythm_key_map = rhythmkey.rhythm_key_map

        self.beat_offset = beat_offset
        self.k = k

        self.tempomap = self._convert_tempomap(self.raw_tempomap)

    def _convert_tempomap(self, raw_tempomap):
        tempomap = []

        nowtempo = raw_tempomap[0][1] / 10000
        if len(raw_tempomap) > 1:
            now_time = 1
        else:
            now_time = 0

        for i in range(len(self.rhythm_key_map)):
            tempomap.append(nowtempo)
            
            if raw_tempomap[now_time][0] / self.k == i:
                nowtempo = raw_tempomap[now_time][1] / 10000
                if now_time < len(raw_tempomap) - 1:
                    now_time += 1

        return tempomap


class Rhythm:
    def __init__(self, tempomap, rhythmkey):
        self.tempomap = tempomap
        self.rhythmkey = rhythmkey
        self._length = self.time(len(self.tempomap.tempomap))

    @property
    def beat_offset(self):
        return self.tempomap.beat_offset

    @property
    def length(self):
        return self._length

    def time(self, index):
        times = 0.0

        for tempo in self.tempomap.tempomap[:index]:
            times += (1 / ((tempo / 60) * 2))

        return times + (self.beat_offset / 1000)

    def musickey(self, index):
        return self.rhythmkey.rhythm_key_map[index][1]

    def tempo(self, index):
        return self.tempomap.tempomap[index]

    def measure(self, index):
        return self.rhythmkey.rhythm_key_map[index][0]

    def measure_number(self, index):
        number = 0
        measure_sum = 0

        for i in range(len(self.rhythmkey.rhythm_key_map)):
            measure_sum += 1

            if measure_sum > index:
                break

            number += 1

        return number
