chord_name = {
    0: "",
    1: "m",
    2: "dim7",
    3: "aug",
    4: "6",
    5: "7",
    6: "M7",
    7: "add9",
    8: "m6",
    9: "m7",
    10: "mM7",
    11: "sus4",
    12: "7sus4",
    13: "m7-5"}
chord_name_pitch = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B"}


def splitindex(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


def number_to_chord(chord_num, is_input=False, on_chord=False):
    name = chord_num // 12
    if on_chord:
        pitch = (chord_num % 12) - 1
    else:
        pitch = chord_num % 12
    if is_input:
        pitch += 1
        pitch %= 12

    return chord_name_pitch[pitch] + chord_name[name]


def chord_label(chord_time):
    result_text = ""

    for times in chord_time:
        result_text += str(times.start_time) + ":" + str(times.end_time) + ":" + times.chord + "\n"

    return result_text


class ChordLabel:
    def __init__(self, start_time, end_time, chord):
        self._start_time = start_time
        self._end_time = end_time
        self._chord = chord

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def chord(self):
        return self._chord


class ChordSplit:
    def __init__(self, chord, bpm, bpm_offset):
        self._chord = chord
        self._bpm = bpm
        self._bpm_offset = bpm_offset
        self._val = 1 / ((self._bpm / 60) * 2)

    @property
    def bpm(self):
        return self._bpm

    @property
    def bpm_offset(self):
        return self._bpm_offset

    @property
    def chord(self):
        return self._chord

    @property
    def splittime(self):
        return self._val

    def frame(self, time):
        intime = int((time - (self.bpm_offset / 1000)) // self.splittime)
        if intime < 0:
            intime = 0

        chord = self._split(intime)
        if chord == "":
            for i in reversed(range(intime)):
                chord = self._split(i)
                if chord == "N.C." or chord != "":
                    break
        return chord

    def chord_time(self, ax=0.01):
        """[summary]
        
        Args:
            ax (float, optional): 解析する頻度(秒). Defaults to 0.04.
        
        Returns:
            {x: [start_time, end_time, chord]}
        """
        music_len = int((self.bpm_offset / 1000) + (len(self.chord) * self.splittime))
        time = int(self.bpm_offset / 1000)
        result_chord = []
        result_times = []

        chord_ = ""
        count = 0
        for i in range(int(music_len / ax)):
            n_chord = self.frame(time)
            if n_chord != chord_:
                result_times.append(time)
                if len(result_times) == 2:
                    result_chord.append(ChordLabel(result_times[0], result_times[1], chord_))
                    result_times = [time]
                    count += 1
                chord_ = n_chord
            time += ax

        return result_chord

    def _split(self, time):
        enable_chord = self.chord[time][0]
        input_chord = self.chord[time][4]
        input_on_chord = self.chord[time][5]
        auto_chord = self.chord[time][8]
        auto_on_chord = self.chord[time][9]

        result_chord = ""
        # コードが存在していたら
        if enable_chord:
            # コード入力の場合
            if input_chord > 1:
                result_chord = number_to_chord(input_chord, is_input=True)
                if input_on_chord:
                    result_chord += "/" + \
                        number_to_chord(input_on_chord, on_chord=True)
            # N.C.の場合
            elif input_chord == 0:
                result_chord = "N.C."

            # 自動認識の場合
            else:
                result_chord = number_to_chord(auto_chord)
                if auto_on_chord:
                    result_chord += "/" + number_to_chord(auto_on_chord, on_chord=True)

        return result_chord
