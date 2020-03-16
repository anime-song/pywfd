from pywfd import chord
from pywfd import rhythm
from pywfd import io
from pywfd import label as lb
import numpy as np


class WFDData:
    def __init__(self, loader):
        self._loader = loader
        self._loader.readHeader()
        self._loader.readIndex()
        self._loader.readData()

        self.tempo = self._loader.headers[self._loader.headerA(
            lb.TEMPO, method="DATATYPE")].value
        self.block_per_semitone = self._loader.headers[self._loader.headerA(
            lb.BLOCK_PER_SEMITONE, method="DATATYPE")].value
        self.min_note = self._loader.headers[self._loader.headerA(
            lb.MIN_NOTE, method="DATATYPE")].value
        self.range_of_scale = self._loader.headers[self._loader.headerA(
            lb.RANGE_OF_SCALE, method="DATATYPE")].value
        self.block_per_second = self._loader.headers[self._loader.headerA(
            lb.BLOCK_PER_SECOND, method="DATATYPE")].value
        self.time_all_block = self._loader.headers[self._loader.headerA(
            lb.TIME_ALL_BLOCK, method="DATATYPE")].value
        self.beat_offset = self._loader.headers[self._loader.headerA(lb.OFFSET, method="DATATYPE")].value
        self.beat = self._loader.headers[self._loader.headerA(
            lb.BEAT, method="DATATYPE")].value

        self.label_list = lb.Label(self.getdata(lb.LABEL_LIST))
        self._rhythmkey = rhythm.RhythmKey(
            self.getdata(
                lb.RHYTHM_KEYMAP),
            chord=self.getdata(
                lb.CHORD_RESULT))

        self._tempomap = rhythm.TempoMap(
            self.getdata(
                lb.TEMPO_MAP),
            rhythmkey=self.rhythmkey,
            beat_offset=self.beat_offset)

        self._chords = chord.ChordSplit(
            self.getdata(
                lb.CHORD_RESULT),
            rhythm=rhythm.Rhythm(self.tempomap, self.rhythmkey),
            label=self.label_list)

    @property
    def loader(self):
        return self._loader

    @property
    def spectrumStereo(self):
        """音声スペクトル(stereo)"""
        return self.getdata(lb.SPECTRUM_STEREO)

    @spectrumStereo.setter
    def spectrumStereo(self, spectrum):
        spectrum = np.array(spectrum).flatten()
        self.setdata(lb.SPECTRUM_STEREO, spectrum)

    @property
    def spectrumLRM(self):
        """音声スペクトル(L-R)"""
        return self.getdata(lb.SPECTRUM_LR_M)

    @spectrumLRM.setter
    def spectrumLRM(self, spectrum):
        spectrum = np.array(spectrum).flatten()
        self.setdata(lb.SPECTRUM_LR_M, spectrum)

    @property
    def spectrumLRP(self):
        """音声スペクトル(L+R)"""
        return self.getdata(lb.SPECTRUM_LR_P)

    @spectrumLRP.setter
    def spectrumLRP(self, spectrum):
        spectrum = np.array(spectrum).flatten()
        self.setdata(lb.SPECTRUM_LR_P, spectrum)

    @property
    def spectrumL(self):
        """音声スペクトル(L)"""
        return self.getdata(lb.SPECTRUM_L)

    @spectrumL.setter
    def spectrumL(self, spectrum):
        spectrum = np.array(spectrum).flatten()
        self.setdata(lb.SPECTRUM_L, spectrum)

    @property
    def spectrumR(self):
        """	音声スペクトル(R)"""
        return self.getdata(lb.SPECTRUM_R)

    @spectrumR.setter
    def spectrumR(self, spectrum):
        spectrum = np.array(spectrum).flatten()
        self.setdata(lb.SPECTRUM_R, spectrum)

    @property
    def chords(self):
        return self._chords

    @chords.setter
    def chords(self, chords):
        verify = np.array(self.chords_raw)
        chords = np.concatenate((verify[:16], np.array(chords).flatten(), verify[-48:])).astype("uint8")
        self.setdata(lb.CHORD_RESULT, chords)
        label = np.array(self.chords.label.to_array()).astype("uint32")
        self.setdata(lb.LABEL_LIST, label)
        self._loader.shift_offset(lb.LABEL_LIST, int(len(label) * 4))

    @property
    def rhythmkey(self):
        return self._rhythmkey

    @property
    def tempomap(self):
        return self._tempomap

    @property
    def chords_raw(self):
        return self.get_raw_data(lb.CHORD_RESULT)

    @chords_raw.setter
    def chords_raw(self, chords):
        self.setdata(lb.CHORD_RESULT, chords)

    def setdata(self, key, data):
        self._loader.raw_data[key] = data

    def getdata(self, key):
        return self._loader.wfd_data[key]

    def get_raw_data(self, key):
        return self._loader.raw_data[key]


class WFD:
    def __init__(self):
        self._loader = io.WFDLoader()

    def load(self, filepath):
        self._loader.open(filepath)
        self.wfd_data = WFDData(self._loader)
        return self.wfd_data


def load(file):
    wfd = WFD()

    data = wfd.load(file)

    return data


def write(file, data):
    io.WFDWriter().write(file, data)
