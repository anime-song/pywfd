# pywfd

## 概要
wavetoneの独自フォーマットであるwfdをpythonで使える形にします。

現在使用可能な物は以下の通りです。

- 音声スペクトル(stereo) *1
- 音声スペクトル(L-R) *1
- 音声スペクトル(L+R) *1
- 音声スペクトル(L) *1
- 音声スペクトル(R) *1
- コード検出結果
- キーラベル

使用不可能なもの

- 4/4拍子以外
- BPMが途中で変更される場合

## インストール
```sh
$ pip install pywfd
```
※ 最新バージョンのみ正常に動作します。

## 基本的な使い方

### WFDファイル読み込み
```python
>>> import pywfd
>>> wfd_data = pywfd.load("./test.wfd")
```
### スペクトルステレオ(音声スペクトル)
```python
>>> import pywfd
>>> wfd_data = pywfd.load("./test.wfd")
>>> wfd_data.spectrumStereo
>>> # wfd_data.spectrumLRM
>>> # wfd_data.spectrumStereo = []
```

### コードラベル
```python
>>> import pywfd
>>> from pywfd import chord_label
>>> wfd_data = pywfd.load("./test.wfd")
>>> chord_time = wfd_data.chords.getChordLabel(ax=0.01) # axは解析する時間の頻度(秒)
>>> label = chord_label(chord_time) # 文字列に変換
"""
0.0:0.07:N.C.
0.07:0.26000000000000006:N.C.
0.26000000000000006:0.45000000000000023:N.C.
0.45000000000000023:1.0100000000000007:DM7
"""
```

### キーラベル
```python
>>> import pywfd
>>> wfd_data = pywfd.load("./test.wfd")
>>> key_label = wfd_data.rhythmkey.keyLabel()
>>> key_label
[[1.08, 16.34, 'Bb']]
```

### WFDファイル書き込み
```python
>>> import pywfd
>>> bins_100 = pywfd.load("./test_bins_100.wfd")
>>> bins_50 = pywfd.load("./test_bins_50.wfd")
>>> bins_50.chords_raw = bins_100.chords_raw
>>> pywfd.write("test.wfd", bins_50)
```


