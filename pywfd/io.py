from pandas import DataFrame
import numpy as np
import struct
import os.path
import sys

from pywfd import label as lb
from pywfd import chordsplit as cp


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
        header_offset, index_offset, data_offset = wfd_data.loader.getInfo()
        result = {}
        for k, v in header_offset.items():
            result[v[0]] = [wfd_data.loader.headerA(k, "DATATYPE", "VALUE"), v[1]]

        for k, v in index_offset.items():
            for v_list in v:
                result[v_list[0]] = [wfd_data.loader.indexA(
                    k, "DATATYPE", v_list[2]), v_list[1]]

        for k, v in data_offset.items():
            result[v[0]] = [wfd_data.get_raw_data(k), v[1]]
        return result

    def write(self, file, wfd_data):
        write_data = self.parse_wfd(wfd_data)

        with open(file, 'wb') as f:
            for offset, value in write_data.items():
                f.seek(offset)
                if type(value[0]) is np.int64:
                    value[0] = int(value[0])

                    f.write(value[0].to_bytes(
                            struct.calcsize(value[1]), byteorder=sys.byteorder))
                elif type(value[0]) is np.ndarray:
                    value[0] = bytearray(value[0])
                    f.write(value[0])


class WFDLoader(Loader):
    def __init__(self):
        super().__init__()
        self.headers = DataFrame([
            [lb.FILETYPE, 0, 0],
            [lb.RESERVE_SPACE1, 1, 0],
            [lb.RESERVE_SPACE2, 2, 0],
            [lb.BLOCK_PER_SEMITONE, 3, 0],
            [lb.MIN_NOTE, 4, 0],
            [lb.RANGE_OF_SCALE, 5, 0],
            [lb.BLOCK_PER_SECOND, 6, 0],
            [lb.RESERVE_SPACE3, 7, 0],
            [lb.TIME_ALL_BLOCK, 8, 0],
            [lb.BITS_OF_GRAPH, 9, 0],
            [lb.BEAT_DISPLAY_FLAG, 10, 0],
            [lb.TEMPO, 11, 0],
            [lb.OFFSET, 12, 0],
            [lb.BEAT, 13, 0]],
            columns=["DATATYPE", "DATANUM", "VALUE"])
        self.indexes = DataFrame([
            [lb.DATASIZE, -1, 0, "I", -1],
            [lb._, 0, 0, "H", 0],
            [lb.TEMPO_RESULT, 2, 0, "I", 0],
            [lb.EXTEND_INFO, 4, 0, "I", 0],
            [lb.LABEL_LIST, 6, 0, "I", 0],
            [lb.SPECTRUM_STEREO, 7, 0, "H", 0],
            [lb.SPECTRUM_LR_M, 8, 0, "H", 0],
            [lb.SPECTRUM_LR_P, 9, 0, "H", 0],
            [lb.SPECTRUM_L, 10, 0, "H", 0],
            [lb.SPECTRUM_R, 11, 0, "H", 0],
            [lb.TEMPO_MAP, 12, 0, "I", 0],
            [lb.CHORD_RESULT, 14, 0, "B", 0],
            [lb.RHYTHM_KEYMAP, 15, 0, "I", 0],
            [lb.NOTE_LIST, 16, 0, "I", 0],
            [lb.TEMPO_VOLUME, 17, 0, "I", 0],
            [lb.FREQUENCY, 18, 0, "I", 0],
            [lb.TRACK_SETTING, 19, 0, "I", 0]],
            columns=["DATATYPE", "DATANUM", "DATASIZE", "DATAFORMAT", "INDEX"])
        self.wfd_data = {}

        self.header_offset = {}
        self.index_offset = {}
        self.data_offset = {}

        self.header_format = "I"
        self.index_format = "I"

    @property
    def __indexes__(self):
        return self.indexes

    @property
    def headerlen(self):
        return len(self.headers.index)

    @property
    def indexeslen(self):
        return len(self.indexes.index)

    def open(self, filepath):
        _, ext = os.path.splitext(filepath)
        if ext.lower() != ".wfd":
            raise ValueError("wfdファイルではありません")

        self._buffer = open(filepath, 'rb').read()
        
    def getInfo(self):
        return self.header_offset, self.index_offset, self.data_offset

    def readHeader(self):
        """Headerを読み込みます"""
        
        for i in range(self.headerlen):
            self.header_offset[self.headerA(
                i, "DATANUM", "DATATYPE")] = [self.offset, self.header_format]
            data = self.unpack(
                self.buffer, self.header_format, 1, self.offset)
            self.headers.loc[(self.headers["DATANUM"] == i), "VALUE"] = data[0]

        return self.headers

    def readIndex(self):
        """Indexを読み込みます"""
        if self.offset >= (struct.calcsize(self.header_format) * self.headerlen):
            counter = 1
            for i in self.indexes["DATANUM"]:
                if i == -1:
                    offset = self.offset
                    data = self.unpack(
                        self.buffer, self.index_format, 1, self.offset)
                    self.indexes.loc[(self.indexes["DATANUM"] == -1), "DATASIZE"] = data[0]
                    self.index_offset[self.indexA(-1,
                                                  "DATANUM",
                                                  "DATATYPE")] = [[offset,
                                                                  self.index_format, "DATASIZE"]]
                else:
                    if self.indexA(-1, "DATANUM", "DATASIZE") < counter:
                        continue
                    
                    datanumber_offset = self.offset
                    datanumber = self.unpack(self.buffer, self.index_format, 1, self.offset)[0]

                    datasize_offset = self.offset
                    datasize = self.unpack(self.buffer, self.index_format, 1, self.offset)[0]

                    self.index_offset[self.indexA(datanumber, "DATANUM", "DATATYPE")] = [[
                        datanumber_offset, self.index_format, "DATANUM"], [
                        datasize_offset, self.index_format, "DATASIZE"]]

                    self.indexes.loc[(self.indexes["DATANUM"] == datanumber), "DATASIZE"] = datasize
                    self.indexes.loc[(self.indexes["DATANUM"] == datanumber), "INDEX"] = counter
                    
                    counter += 1
                    
            self.indexes.sort_values("INDEX", inplace=True)
        return self.indexes

    def readData(self):
        """データを読み込みます"""
        bps = self.headerA(lb.BLOCK_PER_SEMITONE, "DATATYPE", "VALUE")
        range_scale = self.headerA(lb.RANGE_OF_SCALE, "DATATYPE", "VALUE")
        time_all_block = self.headerA(lb.TIME_ALL_BLOCK, "DATATYPE", "VALUE")
        freq_all_block = bps * range_scale

        data = {}

        for dtype in self.indexes["DATATYPE"]:
            if self.indexA(dtype, "DATATYPE", "INDEX") <= 0:
                data[dtype] = []
                continue
            
            self.data_offset[dtype] = [self.offset, self.indexA(dtype, "DATATYPE", "DATAFORMAT")]
            datasize = self.indexA(dtype, "DATATYPE", "DATASIZE")
            dataformat = self.indexA(dtype, "DATATYPE", "DATAFORMAT")
                
            data[dtype] = self.unpack(self.buffer, dataformat, int(datasize / struct.calcsize(dataformat)), self.offset)

        result_data = {}
        for k, v in data.items():
            if len(v) == (time_all_block * freq_all_block):
                result_data[k] = np.array(self.__spectrumData(v, time_all_block, freq_all_block), dtype="float32").T
            elif k == lb.CHORD_RESULT:
                result_data[k] = np.array(list(cp.splitindex(v, 48))[:-1])
            else:
                result_data[k] = v
        self.wfd_data = result_data
        self.raw_data = data
        return result_data

    def __spectrumData(self, x, time_all_block, freq_all_block):
        """正規化とリシェイプを行います"""
        data = np.array(x / 65535.0, dtype="float32")
        return np.reshape(data, (time_all_block, freq_all_block))

    def headerA(self, x_key, x="DATATYPE", y="VALUE"):
        return self.headers.loc[(self.headers[x] == x_key), y].values[0]

    def headerB(self, x, y):
        self.headers.loc[(self.headers["DATATYPE"] == x), "VALUE"] = y

    def indexA(self, x_key, x, y):
        return self.indexes.loc[(self.indexes[x] == x_key), y].values[0]
