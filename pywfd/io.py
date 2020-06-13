import numpy as np
import struct
import os.path
import sys

from pywfd import label as lb
from pywfd import chord as cp


class Writer:
    def __init__(self):
        pass
    
    def write(self, file, wfd_data):
        pass


class Loader:
    def __init__(self):
        self._buffer = None
        self.offset = 0
        self.offset_list = []

    @property
    def buffer(self):
        return self._buffer

    def open(self, filepath):
        self._buffer = open(filepath, 'rb').read()

    def unpack(self, buffer, format, count, offset, add_offset=True):
        self.offset_list.append(self.offset)
        data = np.frombuffer(buffer, dtype=format, count=count, offset=offset)
        self.offset += int(struct.calcsize(format) * count) if add_offset else 0

        return data


class WFDWriter(Writer):
    def __init__(self):
        super().__init__()

    def parse_wfd(self, wfd_data):
        header_offset, index_offset, data_offset = wfd_data.loader.info()
        result = {}
        for k, v in header_offset.items():
            header = wfd_data.loader.headers[wfd_data.loader.headerA(k, "DATATYPE")]
            result[v[0]] = [header.value, v[1]]

        for k, v in index_offset.items():
            for v_list in v:
                index = wfd_data.loader.indexes[wfd_data.loader.indexA(k, "DATATYPE")]
                result[v_list[0]] = [index.search(v_list[2]), v_list[1]]

        for k, v in data_offset.items():
            result[v[0]] = [wfd_data.get_raw_data(k), v[1]]
        return result

    def write(self, file, wfd_data):
        write_data = sorted(self.parse_wfd(wfd_data).items(), key=lambda x: x[0])
        with open(file, 'wb') as f:
            for offset, value in write_data:
                f.seek(offset)
                if type(value[0]) is np.ndarray:
                    value[0] = bytearray(value[0])
                    f.write(value[0])
                else:
                    value[0] = int(value[0])

                    f.write(
                        value[0].to_bytes(
                            struct.calcsize(
                                value[1]),
                            byteorder=sys.byteorder))


class WFDHeader:
    def __init__(self, datatype, datanum, value):
        self._datatype = datatype
        self._datanum = datanum
        self._value = value

    @property
    def datatype(self):
        return self._datatype

    @property
    def datanum(self):
        return self._datanum

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class WFDIndex:
    def __init__(self, datatype, datanum, datasize, dataformat, index):
        self._datatype = datatype
        self._datanum = datanum
        self._datasize = datasize
        self._dataformat = dataformat
        self._index = index

    @property
    def datatype(self):
        return self._datatype

    @property
    def datanum(self):
        return self._datanum

    @property
    def datasize(self):
        return self._datasize

    @datasize.setter
    def datasize(self, datasize):
        self._datasize = datasize

    @property
    def dataformat(self):
        return self._dataformat

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    def search(self, key):
        if key == "DATATYPE":
            return self._datatype
        elif key == "DATANUM":
            return self._datanum
        elif key == "DATASIZE":
            return self._datasize
        elif key == "DATAFORMAT":
            return self._dataformat
        elif key == "INDEX":
            return self._index

        
class WFDLoader(Loader):
    def __init__(self):
        super().__init__()
        self.headers = [
            WFDHeader(lb.FILETYPE, 0, 0),
            WFDHeader(lb.RESERVE_SPACE1, 1, 0),
            WFDHeader(lb.RESERVE_SPACE2, 2, 0),
            WFDHeader(lb.BLOCKS_PER_SEMITONE, 3, 0),
            WFDHeader(lb.MIN_NOTE, 4, 0),
            WFDHeader(lb.RANGE_OF_SCALE, 5, 0),
            WFDHeader(lb.BLOCKS_PER_SECOND, 6, 0),
            WFDHeader(lb.RESERVE_SPACE3, 7, 0),
            WFDHeader(lb.TIME_ALL_BLOCK, 8, 0),
            WFDHeader(lb.BITS_OF_GRAPH, 9, 0),
            WFDHeader(lb.BEAT_DISPLAY_FLAG, 10, 0),
            WFDHeader(lb.TEMPO, 11, 0),
            WFDHeader(lb.OFFSET, 12, 0),
            WFDHeader(lb.BEAT, 13, 0)
        ]
        self.indexes = [
            WFDIndex(lb.DATASIZE, -1, 0, "I", -1),
            WFDIndex(lb._, 0, 0, "H", 0),
            WFDIndex(lb.TEMPO_RESULT, 2, 0, "I", 0),
            WFDIndex(lb.EXTEND_INFO, 4, 0, "I", 0),
            WFDIndex(lb.LABEL_LIST, 6, 0, "I", 0),
            WFDIndex(lb.SPECTRUM_STEREO, 7, 0, "H", 0),
            WFDIndex(lb.SPECTRUM_LR_M, 8, 0, "H", 0),
            WFDIndex(lb.SPECTRUM_LR_P, 9, 0, "H", 0),
            WFDIndex(lb.SPECTRUM_L, 10, 0, "H", 0),
            WFDIndex(lb.SPECTRUM_R, 11, 0, "H", 0),
            WFDIndex(lb.TEMPO_MAP, 12, 0, "I", 0),
            WFDIndex(lb.CHORD_RESULT, 14, 0, "B", 0),
            WFDIndex(lb.RHYTHM_KEYMAP, 15, 0, "I", 0),
            WFDIndex(lb.NOTE_LIST, 16, 0, "I", 0),
            WFDIndex(lb.TEMPO_VOLUME, 17, 0, "I", 0),
            WFDIndex(lb.FREQUENCY, 18, 0, "I", 0),
            WFDIndex(lb.TRACK_SETTING, 19, 0, "I", 0)
        ]

        self.headers = sorted(self.headers, key=lambda x: x.datanum)
        self.indexes = sorted(self.indexes, key=lambda x: x.datanum)

        self.wfd_data = {}

        self.header_offset = {}
        self.index_offset = {}
        self.data_offset = {}

        self.header_format = "I"
        self.index_format = "I"

    @property
    def __indexes__(self):
        return self.indexes

    def open(self, filepath):
        _, ext = os.path.splitext(filepath)
        if ext.lower() != ".wfd":
            raise ValueError("wfdファイルではありません")

        self._buffer = open(filepath, 'rb').read()
        
    def info(self):
        return self.header_offset, self.index_offset, self.data_offset

    def shift_offset(self, datatype, shift_value):
        shift = self.data_offset[datatype][0]
        data = self.indexes[self.indexA(datatype, "DATATYPE")]
        datasize = data.datasize
        data.datasize = shift_value
        shift_value = abs(datasize - shift_value)
        data_offset = {}
        for dtype, value in self.data_offset.items():
            offset = value[0]
            if offset > shift:
                value[0] += shift_value
            data_offset[dtype] = value

        self.data_offset = data_offset

    def readHeader(self):
        """Headerを読み込みます"""
        
        for i in range(len(self.headers)):
            self.header_offset[self.headers[self.headerA(i)].datatype] = [self.offset, self.header_format]
            data = self.unpack(self.buffer, self.header_format, 1, self.offset)
            self.headers[self.headerA(i)].value = data[0]

        return self.headers

    def readIndex(self):
        """Indexを読み込みます"""
        if self.offset >= (struct.calcsize(self.header_format) * len(self.headers)):
            counter = 1
            start_index = self.indexA(-1)
            for i in range(len(self.indexes)):
                if self.indexes[i].datanum == -1:
                    offset = self.offset
                    data = self.unpack(self.buffer, self.index_format, 1, self.offset)
                    self.indexes[start_index].datasize = data[0]
                    self.index_offset[self.indexes[start_index].datatype] = [
                        [offset, self.index_format, "DATASIZE"]]
                else:
                    if self.indexes[start_index].datasize < counter:
                        continue
                    
                    datanumber_offset = self.offset
                    datanumber = self.unpack(self.buffer, self.index_format, 1, self.offset)[0]
                    datanumber = self.indexA(datanumber)

                    datasize_offset = self.offset
                    datasize = self.unpack(self.buffer, self.index_format, 1, self.offset)[0]

                    self.index_offset[self.indexes[datanumber].datatype] = [
                        [datanumber_offset, self.index_format, "DATANUM"],
                        [datasize_offset, self.index_format, "DATASIZE"]
                    ]

                    self.indexes[datanumber].datasize = datasize
                    self.indexes[datanumber].index = counter
                    
                    counter += 1
            
            self.indexes = sorted(self.indexes, key=lambda x: x.index)
        return self.indexes

    def readData(self):
        """データを読み込みます"""
        bps = self.headers[self.headerA(lb.BLOCKS_PER_SEMITONE, "DATATYPE")].value
        range_scale = self.headers[self.headerA(lb.RANGE_OF_SCALE, "DATATYPE")].value
        time_all_block = self.headers[self.headerA(lb.TIME_ALL_BLOCK, "DATATYPE")].value
        freq_all_block = bps * range_scale
        data = {}

        for i in range(len(self.indexes)):
            dtype = self.indexes[i]._datatype
            if self.indexes[i].index <= 0:
                data[dtype] = []
                continue

            self.data_offset[dtype] = [self.offset, self.indexes[i].dataformat]
            datasize = self.indexes[i].datasize
            dataformat = self.indexes[i].dataformat
                
            data[dtype] = self.unpack(self.buffer, dataformat, int(datasize / struct.calcsize(dataformat)), self.offset)

        result_data = {}
        for k, v in data.items():
            if len(v) == (time_all_block * freq_all_block):
                result_data[k] = np.array(self.__spectrumData(v, time_all_block, freq_all_block), dtype="float32").T
            elif k == lb.CHORD_RESULT:
                v = v[16:]
                result_data[k] = np.array(list(cp.splitindex(v, 48))[:-1])
            elif k == lb.RHYTHM_KEYMAP:
                result_data[k] = np.array(list(cp.splitindex(v, 3)))
            elif k == lb.TEMPO_MAP:
                result_data[k] = np.array(list(cp.splitindex(v, 2)))
            else:
                result_data[k] = v
        self.wfd_data = result_data
        self.raw_data = data
        return result_data

    def __spectrumData(self, x, time_all_block, freq_all_block):
        """正規化とリシェイプを行います"""
        data = np.array(x / 65535.0, dtype="float32")
        return np.reshape(data, (time_all_block, freq_all_block))

    def headerA(self, key, method="DATANUM"):
        for i in range(len(self.headers)):
            if method == "DATANUM":
                if self.headers[i].datanum == key:
                    return i
            elif method == "DATATYPE":
                if self.headers[i].datatype == key:
                    return i

    def indexA(self, key, method="DATANUM"):
        for i in range(len(self.indexes)):
            if method == "DATANUM":
                if self.indexes[i].datanum == key:
                    return i
            elif method == "DATATYPE":
                if self.indexes[i].datatype == key:
                    return i
