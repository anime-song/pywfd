from pywfd import const

class RhythmKey:
    def __init__(self, rhythm_key_map, chord):
        self.raw_rhythm_key_map = rhythm_key_map
        self.rhythm_key_map = self._convert_rhythm_key_map(
            self.raw_rhythm_key_map, chord)
        self.chord = chord
    
    def _convert_rhythm_key_map(self, raw_rhythm_key_map, chord):
        """
            拍子と調のデータをコンバートする。

        """
        rhythm_key_map = []

        for i in range(len(raw_rhythm_key_map)):
            if len(raw_rhythm_key_map) > 1 and (i + 1) != len(raw_rhythm_key_map):
                # 時間の分割単位 (コードの時間単位に依存)
                # 単位の個数を求める (4/4拍子なら 小節数に8を掛ける)
                loop = int(raw_rhythm_key_map[i + 1][0] - raw_rhythm_key_map[i][0]) * raw_rhythm_key_map[i][1] * 2
            else:
                # 時間の分割単位 (コードの時間単位に依存)
                # 残りの個数 (最後までの個数)
                loop = int(len(chord) - len(rhythm_key_map))

            rmp = raw_rhythm_key_map[i][1:]

            # 最大値（調なし）に値を制限
            if raw_rhythm_key_map[i][-1] > const.KEYLENGTH:
                rmp[-1] = const.KEYLENGTH
            
            # すべてに代入
            for j in range(loop):
                rhythm_key_map.append(rmp)

        return rhythm_key_map


class TempoMap:

    def __init__(self, tempomap, rhythmkey, beat_offset):
        self.raw_tempomap = tempomap
        self.rhythm_key_map = rhythmkey.rhythm_key_map

        self.beat_offset = beat_offset

        self.tempomap = self._convert_tempomap(self.raw_tempomap)

    def _getUnitNumber(self, index):
        pos = 0
        for i in range(index):
            measure = self.rhythm_key_map[pos][0]
            pos += measure * 2

            if pos > len(self.rhythm_key_map):
                break

        return pos

    def _convert_tempomap(self, raw_tempomap):
        tempomap = []

        # テンポは 10000 で割る
        currentTempo = raw_tempomap[0][1] / const.TEMPO_DIVIDE
        current_pos = 1

        for i in range(len(self.rhythm_key_map)):
            # テンポマップに現在のテンポを挿入する
            tempomap.append(currentTempo)
            
            if len(raw_tempomap) > 1:
                # 2番目の位置の数値で割ることで小節番号がわかる
                M_NUM = int(raw_tempomap[current_pos][0] / raw_tempomap[1][0])

                # 小節番号の中に現在位置があったら
                if self._getUnitNumber(M_NUM) == (i + 1):
                    # 現在のテンポを取得
                    tmpTempo = raw_tempomap[current_pos][1] / const.TEMPO_DIVIDE
                    if currentTempo != tmpTempo:
                        currentTempo = tmpTempo
                        if (current_pos + 1) < len(raw_tempomap):
                            current_pos += 1

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
