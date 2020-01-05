# pywfd

## 概要
wavetoneの独自フォーマットであるwfdをpythonで使える形にします。

## インストール
```sh
$ pip install pywfd
```


## 基本的な使い方

### WFDファイル読み込み
```python
>>> from pywfd import WFD
>>> wfd = WFD()
>>> wfd_data = wfd.load("./test.wfd")
```
### スペクトルステレオ(音声スペクトル)
```python
>>> from pywfd import WFD
>>> wfd = WFD()
>>> wfd_data = wfd.load("./test.wfd")
>>> wfd_data.spectrumStereo
>>> # wfd_data.spectrumLRM
>>> # wfd_data.spectrumStereo = []
```

### コード
```python
>>> from pywfd import WFD
>>> wfd = WFD()
>>> wfd_data = wfd.load("./test.wfd")
>>> time = 1
>>> w.chordresult.frame(time)   # timeは音声位置の秒数です
"C"
```

### WFDファイル書き込み
```python
>>> from pywfd import WFD
>>> wfd = WFD()
>>> wfd_data = wfd.load("./test.wfd")
>>> # wfd_data.spectrumStereo = []
>>> wfd.write("test.wfd", wfd_data)
```


