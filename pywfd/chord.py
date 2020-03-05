import os
import dlchord

chord_quality = {
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
chord_tone = {
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

tones = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "N"]


def splitindex(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


def number_to_chord(chord_num, is_input=False, on_chord=False):
    pitch = (chord_num % 12)
    name = 0

    if on_chord:
        pitch -= 1
    else:
        name = chord_num // 12

    if is_input:
        name = (chord_num - 11) // 12
        pitch += 1

    pitch %= 12
    name %= 14

    return chord_tone[pitch] + chord_quality[name]


def chord_to_array(chord):
    chord_array = [0] * 48
    if chord == '':
        return chord_array

    chord_array[0] = 1

    if chord == "N.C.":
        return chord_array

    chord_num = 11

    try:
        chord = dlchord.Chord(chord)
    except ValueError:
        return chord_array
    chord_num += chord.root

    quality = chord.quality.quality

    sorted_quality = sorted(chord_quality.items(), key=lambda x: len(x[1]), reverse=True)
    for idx, qua in sorted_quality:
        if qua[:3] in quality:
            chord_num += (12 * idx)
            break
    
    chord_array[4] = chord_num
    if chord.bass != chord.root:
        chord_array[5] = chord.bass + 1

    return chord_array


def chord_label(chord_time):
    result_text = ""

    for times in chord_time:
        result_text += str(times[0]) + ":" + str(times[1]) + ":" + times[2] + os.linesep

    return result_text


def label_to_chord(label, sep=':'):
    times = []

    for frame in label:
        if frame:
            sp = frame.strip().split(sep)
            if len(sp) == 2:
                chord = "N.C."
            else:
                chord = str(sp[2])
            
            times.append([float(sp[0]), float(sp[1]), chord])

    return times


class ChordSplit:
    def __init__(self, chord, rhythm):
        self._raw_chord = chord
        self._chord = self._raw_chord_to_chord(self._raw_chord)
        self.rhythm = rhythm
        self.tempo = self.rhythm.tempo(0)
        self.beat_offset = self.rhythm.beat_offset / 1000

    @property
    def raw_chord(self):
        return self._raw_chord

    @property
    def chord(self):
        return self._chord

    def _raw_chord_to_chord(self, raw_chord):
        chord = []
        for i in range(len(raw_chord)):
            chord.append(self._split(i))

        return chord

    def chordLabel(self):
        """[summary]
        
        Returns:
            {x: [start_time, end_time, chord]}
        """
        s_time = 0.0 + self.beat_offset
        e_time = 0.0
        times = []

        chord = ""
        now_chord = ""
        for i in range(len(self.chord)):
            now_chord = self.chord[i]

            if i == 0:
                chord = now_chord

            if chord != now_chord and now_chord != '' or i == (len(self.chord) - 1):
                e_time = self.rhythm.time(i)
                times.append([s_time, e_time, chord])
                chord = now_chord
                s_time = e_time

        return times

    def keyLabel(self):
        times = []

        s_time = 0.0 + self.beat_offset
        e_time = 0.0
        key = ""
        now_key = ""
        
        for i, frame in enumerate(self.rhythm.rhythmkey.rhythm_key_map):
            now_key = frame[-1]
            
            if i == 0:
                key = now_key

            if key != now_key or i == (len(self.rhythm.rhythmkey.rhythm_key_map) - 1):
                e_time = self.rhythm.time(i)
                times.append([s_time, e_time, tones[key]])
                key = now_key
                s_time = e_time

        return times

    def label_to_array(self, label):
        chordlist = []
        offset = 0

        min_time = self.rhythm.time(0)
        duration = abs(min_time - self.rhythm.time(1))

        for i in range(len(label)):
            if label[i][1] < min_time or abs(label[i][1] - min_time) < duration:
                offset += 1

        label = label[offset:]
        offset = 0

        if min_time - label[0][0] > duration:
            label[0][0] += (duration - (min_time - label[0][0]))

        for i in range(len(self.chord)):
            if len(label) <= offset:
                break

            duration = abs(self.rhythm.time(i) - self.rhythm.time(i + 1))

            dist = abs(self.rhythm.time(i) - label[offset][0])
            if dist < duration:
                if dist <= abs(self.rhythm.time(i + 1) - label[offset][0]):
                    chordlist.append(chord_to_array(label[offset][-1]))
                    offset += 1
                else:
                    chordlist.append(chord_to_array(''))
            else:
                chordlist.append(chord_to_array(''))

        return chordlist

    def to_chordpro(self, indent=4, form=True):
        chordtext = ""
        measure = -1
        time = 0
        measure_count = 0

        for i, chord in enumerate(self.chord, start=1):
            if form:
                try:
                    chord = dlchord.note_to_chord(dlchord.Chord(chord).getNotes())[0].chord
                except ValueError:
                    pass
                
            measure_num = self.rhythm.measure_number(i - 1)
            if measure != self.rhythm.measure(measure_num):
                measure = self.rhythm.measure(measure_num)
                time = i - 1

            if chord:
                chordtext += "[{}]-".format(chord)
            else:
                chordtext += "-"

            if (i - time) % (measure * 2) == 0:
                chordtext += "|"
                measure_count += 1

            elif (i - time) % measure == 0:
                chordtext += " "
            
            if measure_count % indent == 0 and measure_count != 0:
                measure_count = 0
                chordtext += os.linesep

        return chordtext

    def _split(self, time):
        enable_chord = self.raw_chord[time][0]
        input_chord = self.raw_chord[time][4]
        input_on_chord = self.raw_chord[time][5]
        auto_chord = self.raw_chord[time][8]

        result_chord = ""
        # コードが存在していたら
        if enable_chord:
            # コード入力の場合
            if input_chord > 10:
                result_chord = number_to_chord(input_chord, is_input=True)
                if input_on_chord:
                    result_chord += "/" + \
                        number_to_chord(input_on_chord, on_chord=True)
            # N.C.の場合
            elif input_chord == 0:
                result_chord = "N.C."

            # 自動認識の場合
            else:
                auto_chord = self.raw_chord[time][4 + (4 * input_chord)]
                result_chord = number_to_chord(auto_chord)
        
        return result_chord
