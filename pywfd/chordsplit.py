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


def number_to_chord(name_num, pitch_num, is_input):
    if is_input:
        name_num -= 1
        pitch_num += 1

    return chord_name_pitch[pitch_num] + chord_name[name_num]


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
        intime = int((time - (self.bpm_offset / 1000)) // (self.splittime))
        chord = self._split(intime)
        if chord == "":
            for i in reversed(range(intime)):
                chord = self._split(i)
                if chord == "N.C." or chord != "":
                    break
        return chord

    def _split(self, time):
        enable_chord = self.chord[time][0]
        input_chord = self.chord[time][4]
        input_on_chord = self.chord[time][5]
        auto_chord = self.chord[time][8]
        auto_on_chord = self.chord[time][9]

        result_chord = ""
        if enable_chord:
            if input_chord > 1:
                result_chord = number_to_chord(
                    input_chord // 12, input_chord %
                    12, is_input=True)
                if input_on_chord:
                    result_chord += "/" + number_to_chord(
                        (input_on_chord // 12), (input_on_chord % 12) - 1, is_input=False
                    )
            elif input_chord == 0:
                result_chord = "N.C."
            else:
                result_chord = number_to_chord(
                    auto_chord // 12, auto_chord %
                    12, is_input=False)
                if auto_on_chord:
                    result_chord += "/" + number_to_chord(
                        (auto_on_chord // 12), (auto_on_chord % 12) - 1, is_input=False
                    )

        return result_chord

        def splitframe(self, y, frame):
            pass
