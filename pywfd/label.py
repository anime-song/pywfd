import numpy as np
DATASIZE = "datasize"
_ = "_"
TEMPO_RESULT = "tempo_result"
EXTEND_INFO = "extend_info"
LABEL_LIST = "label_list"
SPECTRUM_STEREO = "spectrum_stereo"
SPECTRUM_LR_M = "spectrum_LR_M"
SPECTRUM_LR_P = "spectrum_LR_P"
SPECTRUM_L = "spectrum_L"
SPECTRUM_R = "spectrum_R"
TEMPO_MAP = "tempo_map"
CHORD_RESULT = "chord_result"
RHYTHM_KEYMAP = "rhythm_keymap"
NOTE_LIST = "note_list"
TEMPO_VOLUME = "tempo_volume"
FREQUENCY = "frequency"
TRACK_SETTING = "track_setting"

FILETYPE = "filetype"
RESERVE_SPACE1 = "reserve_space1"
RESERVE_SPACE2 = "reserve_space2"
BLOCKS_PER_SEMITONE = "blocks_per_semitone"
MIN_NOTE = "min_note"
RANGE_OF_SCALE = "range_of_scale"
BLOCKS_PER_SECOND = "blocks_per_second"
RESERVE_SPACE3 = "reserve_space3"
TIME_ALL_BLOCK = "time_all_block"
BITS_OF_GRAPH = "bits_of_graph"
BEAT_DISPLAY_FLAG = "beat_display_flag"
TEMPO = "tempo"
OFFSET = "offset"
BEAT = "beat"


def splitindex(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


class Label:

    def __init__(self, label):
        self._raw_label = label
        self._label_list = []
        self._label_num = 0

        self._parse_label(self._raw_label)
            
    def _parse_label(self, label):
        self._label_num = label[0]

        for lab in splitindex(label[1:], 18):
            label = LabelSplit()
            label.parse(lab)
            self._label_list.append(label)

    def append(self, label):
        self._label_num += 1
        self._label_list.append(label)

    def to_array(self):
        result_array = []
        result_array.append(self._label_num)
        self._label_list = sorted(self._label_list, key=lambda x: x._time)

        for lab in self._label_list:
            result_array.extend(lab.encoded_label())

        return result_array


class LabelSplit:
    def __init__(self):
        self._char_label = np.zeros((64, ), dtype="uint32")
        self._time = 0

    def parse(self, raw_label):
        self._time = raw_label[0]
        encoded_text = ""
        
        for i, raw in enumerate(raw_label[2:]):
            encoded_text += format(int.from_bytes(raw, byteorder="big"), 'x')

        for i, byte in enumerate(splitindex(encoded_text, 2)):
            self._char_label[i] = int(byte, base=16)

    def setTime(self, time):
        self._time = time

    def setLabel(self, value):
        self._char_label = np.zeros((64, ), dtype="uint32")
        for i, v in enumerate(value):
            self._char_label[i] = ord(v)

    def encoded_label(self):
        encoded_text = int(self._time).to_bytes(8, 'little')

        for char in self._char_label:
            encoded_text += int(char).to_bytes(1, 'little')

        return np.frombuffer(encoded_text, dtype="I")
