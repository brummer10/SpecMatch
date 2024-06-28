#! /usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
#import scipy.io.wavfile
import soundfile as sf

wav_format_only = True
class SndFile(object):
    def __init__(self, name):
       # self.samplerate, self.data = scipy.io.wavfile.read(name, True)
        self.data, self.samplerate = sf.read(name)
        self.nframes = len(self.data)
        self.offset = 0
        if len(self.data.shape) == 1:
            self.channels = 1
        else:
            self.channels = self.data.shape[1]
    def seek(self, n):
        self.offset = n
    def read_frames(self, n):
        if self.data.dtype == np.int32:
            f = 2**23 - 1
        elif self.data.dtype == np.int16:
            f = 2**15 - 1
        else :
            f = 1
        return np.array(self.data[self.offset:n], dtype=np.float64) / f
    def read(self, channel, n):
        a = self.read_frames(n)
        if self.channels > 1 and channel >= -1:
            if channel < 0:
                a = np.sum(a, axis=1)
            else:
                a = self.data[:n, channel]
        if len(a.shape) == 1:
            a = a.reshape((len(a), 1))
        return a
def open_sndfile(name):
    return SndFile(name)
def read_sndfile(f, channel=-1, n=None):
    return f.read(channel, n)
def write_sndfile(data, name, rate, enc):
    if enc == "pcm16":
        tp = np.int16
        f = 2**15 - 1
    elif enc == "pcm24":
        tp = np.int32
        f = 2**23 - 1
    else:
        assert False
    m = np.amax(data)
    if m > 1:
        f /= m
    #return scipy.io.wavfile.write(name, int(rate), np.array(data * f, dtype=tp))
    return sf.write(name, np.array(data * f, dtype=tp), int(rate))
