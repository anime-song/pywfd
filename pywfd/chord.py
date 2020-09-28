import os
import dlchord
import itertools
from dlchord import Chord
from pywfd import label as lb
from pywfd import const


def ToMajor(key):
    if key == const.KEYLENGTH:
        return -1
    if key > 11:
        return key - 12
    return key

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

    pitch %= len(const.CHORD_TONE)
    name %= len(const.CHORD_QUALITY)

    return const.CHORD_TONE[pitch] + const.CHORD_QUALITY[name]


def chord_to_array(chord, tension=True):
    chord_array = [0] * 48
    if chord == '':
        return chord_array

    chord_array[0] = 1

    if chord == "N.C.":
        return chord_array

    chord_num = 11

    try:
        chord = Chord(chord)
    except ValueError:
        return chord_array

    quality = chord.quality.quality

    if tension:
        if chord.bass == chord.root:
            if "b9" in quality:
                if "m" in quality:
                    chord = Chord(Chord(const.TONES[chord.root] + "7").transpose(3).chord + "/" + const.TONES[chord.root])
                else:
                    chord = Chord(Chord(const.TONES[chord.root] + "dim7").transpose(4).chord + "/" + const.TONES[chord.root])
            elif "9" in quality and "add" not in quality and "sus" not in quality and "#9" not in quality:
                if "m" in quality and "M" not in quality:
                    chord = Chord(Chord(const.TONES[chord.root] + "M7").transpose(3).chord + "/" + const.TONES[chord.root])
                elif "M" in quality:
                    chord = Chord(Chord(const.TONES[chord.root] + "m7").transpose(4).chord + "/" + const.TONES[chord.root])
                else:
                    chord = Chord(Chord(const.TONES[chord.root] + "m7-5").transpose(4).chord + "/" + const.TONES[chord.root])
            elif "11" in quality:
                if "m" in quality:
                    chord = Chord(Chord(const.TONES[chord.root] + "add9").transpose(3).chord + "/" + const.TONES[chord.root])

    quality = chord.quality.quality
    chord_num += chord.root

    sorted_quality = sorted(const.CHORD_QUALITY.items(), key=lambda x: len(x[1]), reverse=True)
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


def is_wavetone_chord(chord):
    tension = ["9", "13", "11", "M7-5", "aug7", "augM7"]
    if any([t in chord for t in tension]) and "add9" not in chord:
        return False
    else:
        return True


def getIndexNearestTime(times, time):
    near = -1
    index = 0
    for i, t in enumerate(times):
        if abs(t[0] - time) < near or near == -1:
            near = abs(t[0] - time)
            index = i

    return index


class ChordSplit:
    def __init__(self, chord, rhythm, label):
        self._raw_chord = chord
        self.rhythm = rhythm
        self.label = label
        self._chord = self._raw_chord_to_chord(self._raw_chord)
        self.tempo = self.rhythm.tempo(0)
        self.beat_offset = self.rhythm.beat_offset / 1000

    @property
    def raw_chord(self):
        return self._raw_chord

    @property
    def chord(self):
        return self._chord

    def _raw_chord_to_chord(self, raw_chord, advanced=False):
        chord = []
        for i in range(len(raw_chord)):
            parse_chord = self._split(i)
            if parse_chord != "" and parse_chord != "N.C.":
                key = ToMajor(self.rhythm.musickey(i))
                if key == -1:
                    key = 0
                parse_chord = dlchord.Chord(parse_chord).modify(const.KEY_TONES[key], advanced=advanced).chord
            chord.append(parse_chord)

        return chord

    def chordLabel(self, advanced=False, allow_label=True):
        """[summary]
        
        Returns:
            {x: [start_time, end_time, chord]}
        """
        s_time = 0.0 + self.beat_offset
        e_time = 0.0
        times = []

        chord = ""
        now_chord = ""
        for i, now_chord in enumerate(self.chord):

            if now_chord != '' and now_chord != "N.C.":
                key = ToMajor(self.rhythm.musickey(i))
                if key == -1:
                    key = 0
                now_chord = dlchord.Chord(now_chord).modify(const.KEY_TONES[key], advanced=advanced).chord

            if i == 0:
                chord = now_chord

            if (chord != now_chord and now_chord != '') or i == len(self.chord) - 1:
                s_time = round(s_time, 4)
                e_time = round(self.rhythm.time(i), 4)
                times.append([s_time, e_time, chord])
                chord = now_chord
                s_time = e_time

        if allow_label:
            for label in self.label.label_list:
                label_value = label.getLabel()
                if label_value[:1] == "!":
                    label_time = label.getTime() / 1000
                    index = getIndexNearestTime(times, label_time)
                    times[index][-1] = label_value[1:]

        return times

    def sectionLabel(self):
        times = []
        labels = []
        for label in self.label.label_list:
            label_value = label.getLabel()
            if label_value[:2].lower() == "s!":
                label_time = label.getTime() / 1000
                labels.append([label_time, label_value[2:]])

        if labels:
            label_len = len(labels)
            for i in range(label_len):
                if len(labels) < i + 2:
                    times.append([labels[i][0], round(self.rhythm.length, 4), labels[i][-1]])
                else:
                    times.append([labels[i][0], labels[i + 1][0], labels[i][-1]])

        return times

    def bpmLabel(self):
        times = []
        labels = []
        for label in self.label.label_list:
            label_value = label.getLabel()
            if label_value[:2].lower() == "b!":
                label_time = label.getTime() / 1000
                labels.append([label_time, label_value[2:]])

        if labels:
            label_len = len(labels)
            for i in range(label_len):
                if len(labels) < i + 2:
                    times.append([labels[i][0], round(self.rhythm.length, 4), labels[i][-1]])
                else:
                    times.append([labels[i][0], labels[i + 1][0], labels[i][-1]])

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
                times.append([s_time, e_time, const.KEY_TONES[key]])
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
            label[0][0] += abs(min_time - label[0][0])
        
        for i in range(len(self.chord)):
            if len(label) <= offset:
                break
            
            duration = abs(self.rhythm.time(i) - self.rhythm.time(i + 1))

            dist = abs(self.rhythm.time(i) - label[offset][0])
            if dist < duration and dist <= abs(self.rhythm.time(i + 1) - label[offset][0]):
                chordlist.append(chord_to_array(label[offset][-1]))
                if not is_wavetone_chord(label[offset][-1]):
                    c_label = lb.LabelSplit()
                    c_label.setTime(int(self.rhythm.time(i) * 1000))
                    c_label.setLabel("!" + label[offset][-1])
                    self.label.append(c_label)
                offset += 1
            else:
                if i == 0:
                    chordlist.append(chord_to_array("N.C."))
                else:
                    chordlist.append(chord_to_array(''))

        return chordlist

    def to_chordpro(self, indent=4, form=True, advanced=False):
        chordtext = ""
        measure = -1
        time = 0
        measure_count = 0

        for i, chord in enumerate(self.chord, start=1):
            if form:
                try:
                    key = ToMajor(self.rhythm.musickey(i - 1))
                    if key != -1:
                        chord = dlchord.Chord(chord).modify(const.KEY_TONES[key], advanced=advanced)
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
