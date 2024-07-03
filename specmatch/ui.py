#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
import os
import json
import argparse
from os.path import abspath, dirname, join

import gi
gi.require_version("Gtk", "3.0")

#pylint: disable=wrong-import-position
from gi.repository import Gtk
from gi.repository import GLib
from pydub import AudioSegment

import numpy as np
from numpy import fft

import matplotlib
if matplotlib.get_backend() != "GTK3Agg":
    matplotlib.use("GTK3Agg")
import matplotlib.pyplot as plt

try:
    from spectrum import CalcIR, fftfreq2, fft2spectrum, SmoothSpectrumSpline, clipdb
    from audiofiles import open_sndfile, write_sndfile, read_sndfile, wav_format_only
except ImportError:
    from specmatch.spectrum import CalcIR, fftfreq2, fft2spectrum, SmoothSpectrumSpline, clipdb
    from specmatch.audiofiles import open_sndfile, write_sndfile, read_sndfile, wav_format_only
#pylint: enable=wrong-import-position

current_dir = abspath(dirname(__file__))

class FileDialog(object):

    def __init__(self, set_file, get_file, nr, create, audio=True, data_dir=None):
        self.set_file = set_file
        self.get_file = get_file
        self.nr = nr
        self.create = create
        self.audio = audio
        self.data_dir = data_dir
        self.w = None

    def __call__(self, o=None):
        a = Gtk.FileChooserAction.SAVE if self.create else Gtk.FileChooserAction.OPEN
        self.w = Gtk.FileChooserDialog(
            action=a,
            buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        f = Gtk.FileFilter()
        if self.audio:
            if wav_format_only:
                f.add_pattern("*.wav")
                f.set_name("WAV Files")
            else:
                f.add_mime_type("audio/*")
                f.add_pattern("*.raw")
                f.set_name("Audio Files")
        else:
            self.w.set_current_folder(self.data_dir)
            f.add_pattern("*.specmatch")
            f.set_name("Project Files")
        self.w.add_filter(f)
        f = Gtk.FileFilter()
        f.set_name("All Files")
        self.w.add_filter(f)
        n = self.get_file(self.nr)
        if n:
            if n.endswith("/"):
                self.w.set_current_folder(n)
            else:
                self.w.set_filename(n)
        if self.w.run() == Gtk.ResponseType.OK:
            self.set_file(self.nr, self.w.get_filename())
        self.w.destroy()


class DisplayStatus(object):

    def __init__(self, widget):
        self.widget = widget
        self.stack = []
        self.default = ""

    def set_default(self, s):
        self.default = s
        if not self.stack:
            self.disp(s)

    def disp(self, s):
        self.widget.set_text(s)
        while Gtk.events_pending():
            Gtk.main_iteration()

    def __call__(self, s):
        if not self.stack:
            self.widget.get_toplevel().set_sensitive(False)
        self.stack.append(s)
        self.disp(s)

    def clear(self):
        if self.stack:
            self.stack.pop()
        if self.stack:
            s = self.stack[-1]
        else:
            self.widget.get_toplevel().set_sensitive(True)
            s = self.default
        self.disp(s)

def format_time(v):
    if v is None:
        return ""
    m = int(v / 60)
    return "%02d:%04.1f" % (m, v - m*60)

class SpecWindow(object):

    def __init__(self, args):
        self.data_dir = os.path.join(GLib.get_home_dir(), "SpecMatchData")
        self.fixed_samplerate = args.samplerate
        self.sound_outfile = args.soundfile
        self.orig_ir = args.orig_ir
        spec_file = args.specfile
        self.builder = Gtk.Builder()
        self.glade_file = join(current_dir, 'specmatch.glade')
        self.builder.add_from_file(self.glade_file)
        g = self.builder.get_object

        self.convolver_box = g("convolver_box")
        self.convolver_label = g("convolver_label")
        self.convolver_label.hide()
        self.convolver_box.hide()

        # files
        self.destination_sound = g("destination_sound")
        self.destination_sound_name = g("destination_sound_name")
        self.source_sound = g("source_sound")
        self.source_sound_name = g("source_sound_name")

        # other buttons
        self.display_time = g("display_time")
        self.display_time.connect("clicked", self.on_display_time)
        self.display_freq = g("display_freq")
        self.display_freq.connect("clicked", self.on_display_freq)
        self.generate_ir = g("generate_ir")
        self.generate_ir.connect("clicked", FileDialog(self.set_file, self.get_file, 3, True))
        g("close").connect("clicked", lambda o: self.window.destroy())
        self.recorder = None
        g("open").connect("clicked",FileDialog(
                self.set_file, self.get_file, 2, True, False, self.data_dir)
                )

        # entry elements
        self.ir_size = g("ir_size")
        self.ir_size.connect("value-changed", self.on_ir_size)
        self.ir_cut = g("ir_cut")
        self.ir_cut.connect("value-changed", self.on_ir_cut)
        self.ir_normalize = g("ir_normalize")
        self.ir_normalize.connect("value-changed", self.on_ir_normalize)
        self.ir_norm = self.ir_normalize.get_value()
        self.ir_magnitude = g("ir_magnitude")
        self.ir_magnitude.connect("value-changed", self.on_ir_magnitude)
        self.range_from_input = g("range_from")
        self.range_to_input = g("range_to")
        self.channel_left = g("left")
        self.channel_right = g("right")
        self.channel_sum = g("sum")
        self.channel_stereo = g("stereo")
        self.channel_sum.set_active(True)
        self.channel_left.connect("toggled", self.on_channel, 0)
        self.channel_right.connect("toggled", self.on_channel, 1)
        self.channel_sum.connect("toggled", self.on_channel, -1)
        self.channel_stereo.connect("toggled", self.on_channel, -2)
        self.jconv_stereo = g("jconv_stereo")
        self.jconv_stereo.connect("toggled", self.on_convolver_toggled)
        self.channelbox = g("channelbox")
        self.channel_label = g("channel_label")
        self.display_smooth = g("display_smooth")

        # other
        self.window = g("SpecMatch")
        self.window.connect("destroy", self.on_destroy)
        self.status = g("status")
        self.status_display = g("status")

        self.spec_filename = None
        self.destination_sound_filename = None
        self.source_sound_filename = None
        self.destination_sound_name.set_text("---")
        self.source_sound_name.set_text("---")
        self.destination_sound.connect("clicked", FileDialog(
                self.set_file, self.get_file, 0, False)
                )
        self.source_sound.connect("clicked", FileDialog(
                self.set_file, self.get_file, 1, True)
                )

        self.calc = CalcIR(DisplayStatus(self.status_display), self.get_sample_rate(), self.orig_ir)

        fn = self.load_global_settings()
        if not spec_file:
            spec_file = fn
        if spec_file:
            self.load_startvalues(spec_file)
        else:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            FileDialog(self.set_file, self.get_file, 2, True, False, self.data_dir)()
            if self.spec_filename is None:
                raise SystemExit(0)
        self.set_button_status()

        self.window.show()

    def get_sample_rate(self):
        return self.fixed_samplerate

    def load_global_settings(self):
        g = self.builder.get_object
        try:
            with open(os.path.join(self.data_dir, "specmatch.js")) as fp:
                d = json.load(fp)
        except (IOError, ValueError, TypeError):
            d = {}
        g("plot_ir").set_active(d.get("plot_ir", True))
        g("plot_orig").set_active(d.get("plot_orig", True))
        g("plot_rec").set_active(d.get("plot_rec", True))
        g("plot_diff").set_active(d.get("plot_diff", True))
        self.display_smooth.set_active(d.get("display_smooth", True))
        g("log").set_active(d.get("log", True))
        g("lin").set_active(d.get("lin", False))
        g("display_expander").set_expanded(d.get("display_expander", False))
        return d.get("spec_filename")

    def save_global_settings(self):
        g = self.builder.get_object
        d = dict(spec_filename = os.path.abspath(self.spec_filename),
                 display_expander = g("display_expander").get_expanded(),
                 plot_ir = g("plot_ir").get_active(),
                 plot_orig = g("plot_orig").get_active(),
                 plot_rec = g("plot_rec").get_active(),
                 plot_diff = g("plot_diff").get_active(),
                 display_smooth = self.display_smooth.get_active(),
                 log = g("log").get_active(),
                 lin = g("lin").get_active(),
                 )
        with open(os.path.join(self.data_dir, "specmatch.js"),"w") as fp:
            json.dump(d, fp, indent=2, sort_keys=True)

    def change_file(self, spec_file):
        if self.spec_filename:
            self.save_specfile()
        self.load_startvalues(spec_file)

    def load_startvalues(self, spec_file):
        if os.path.splitext(spec_file)[1] != ".specmatch":
            spec_file += ".specmatch"
        initial = not self.spec_filename
        self.spec_filename = spec_file
        g = self.builder.get_object
        self.calc.status.set_default("File: %s" % spec_file)
        self.window.set_title(
            "SpecMatch: %s" % os.path.splitext(os.path.split(spec_file)[1])[0])
        d = {}
        try:
            with open(spec_file) as fp:
                d = json.load(fp)
        except IOError as e:
            if e.errno != 2: # no such file
                raise
            if not initial:
                return
        except ValueError:
            print ("bad spec.. skipping")
            if not initial:
                return
        def set_file(nr, n):
            try:
                n = d[n]
            except KeyError:
                return
            if n is not None:
                self.set_file(nr, n)

        set_file(0, "destination_sound_filename")
        set_file(1, "source_sound_filename")
        sz = d.get("ir_size",0)
        if sz:
            self.ir_size.set_value(sz)
        self.ir_cut.set_value(d.get("ir_cutoff", -60))
        self.ir_normalize.set_value(d.get("ir_normalize", -25))
        self.ir_magnitude.set_value(d.get("ir_magnitude", -100))
        r = d.get("original_range", (None,None))
        self.calc.original_mode = d.get("original_mode",-1)
        { 0: self.channel_left,
          1: self.channel_right,
         -1: self.channel_sum,
         -2: self.channel_stereo,
         }[self.calc.original_mode].set_active(True)

    def save_specfile(self):
        g = self.builder.get_object
        d = dict(destination_sound_filename = self.destination_sound_filename,
                 source_sound_filename = self.source_sound_filename,
                 ir_size = self.calc.sz,
                 ir_cutoff = self.calc.cutoff,
                 ir_normalize = self.ir_norm,
                 ir_magnitude = self.calc.magnitude,
                 original_range = self.calc.original_range,
                 original_mode = self.calc.original_mode,
                 )
        with open(self.spec_filename,"w") as fp:
            json.dump(d, fp, indent=2, sort_keys=True)

    def on_destroy(self, o):
        self.save_specfile()
        self.save_global_settings()
        Gtk.main_quit()

    def on_ir_size(self, o):
        self.calc.sz = self.ir_size.get_value_as_int()

    def on_convolver_toggled(self, o):
        self.calc.a2 = None

    def on_ir_cut(self, o):
        self.calc.cutoff = self.ir_cut.get_value()

    def on_ir_normalize(self, o):
        self.ir_norm = self.ir_normalize.get_value()

    def on_ir_magnitude(self, o):
        self.calc.magnitude = self.ir_magnitude.get_value()

    def on_channel(self, o, mode):
        self.calc.original_mode = mode
        self.convolver_box.set_sensitive(mode != -2)

    def match_target_amplitude(self,sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    def set_file(self, nr, name):
        if nr == 0:
            f = open_sndfile(name, self.fixed_samplerate)
            rate = self.get_sample_rate()
            if rate != f.samplerate:
                raise ValueError("%s: rate mismatch (%d / %d)" % (name, f.samplerate, rate))
            self.destination_sound_filename = name
            self.destination_sound_name.set_text(name)
            self.calc.destination_sound_file = f
            self.calc.invalidate_ir()
        elif nr == 1:
            if os.path.exists(name):
                f = open_sndfile(name, self.fixed_samplerate)
                rate = self.get_sample_rate()
                if rate != f.samplerate:
                    raise ValueError("%s: rate mismatch (%d / %d)" % (name, f.samplerate, rate))
                a = f.read_frames(f.nframes)
                channel = self.calc.original_mode
                if f.channels > 1 and channel >= -1:
                    if channel < 0:
                        a = np.sum(a, axis=1)
                    else:
                        a = a[:, channel]
                if len(a.shape) == 1:
                    a = a.reshape((len(a), 1))
                self.calc.source_sound = a
                self.ir_size.set_range(0, len(a))
                self.ir_size.set_increments(1, 10)
                if self.ir_size.get_value_as_int() == 0:
                    self.ir_size.set_value(min(3500, len(a)))
            self.source_sound_filename = name
            self.source_sound_name.set_text(name)
            self.calc.invalidate_ir()
            #self.set_file(0, self.destination_sound_filename)
        elif nr == 2:
            self.change_file(name)
            return
        elif nr == 3:
            if not os.path.splitext(name)[1]:
                name += ".wav"
            write_sndfile(self.calc.ir, name, self.get_sample_rate(), "pcm24")
            _sound = AudioSegment.from_file(name)
            sound = self.match_target_amplitude(_sound, self.ir_norm)
            if not self.channel_stereo.get_active():
                sound = sound.set_channels(1)
            else:
                sound = sound.set_channels(2)
            sound.export(name, format="wav")
            return
        self.set_button_status()

    def get_file(self, nr):
        if nr == 0:
            return self.destination_sound_filename
        elif nr == 1:
            return self.source_sound_filename
        elif nr == 2:
            return self.spec_filename
        elif nr == 3:
            return os.path.join(self.data_dir, "IR", "")

    def set_button_status(self):
        orig_fn = self.destination_sound_filename is not None and os.path.exists(
                self.destination_sound_filename
                )
        rec_fn = self.source_sound_filename is not None and os.path.exists(
                self.source_sound_filename
                )
        gen = orig_fn and self.calc.destination_sound_file.channels == 2
        for p in self.channel_label, self.channelbox, self.convolver_label, self.convolver_box:
            p.set_visible(gen)
        gen = orig_fn and rec_fn
        for p in self.generate_ir, self.display_time, self.display_freq, self.ir_size:
            p.set_sensitive(gen)

    @staticmethod
    def plot_fft(ax, f, rate, **kw):
        y = fft2spectrum(f)
        x = abs(fft.fftfreq(len(f), 1.0/rate)[:len(y)])
        i = np.searchsorted(x, 20) # index for first freq >= 20 Hz
        label = kw.pop("label", None)
        l = ax.semilogx(x[i:], y[i:], **kw)
        if label is not None:
            l[0].set_label(label)

    def plot_orig_ir(self, ax, rate, **kw):
        if 'label' not in kw:
            kw['label'] = os.path.splitext(os.path.split(self.orig_ir)[1])[0]
        a = read_sndfile(open_sndfile(self.orig_ir, self.fixed_samplerate))
        n = max(2**14, len(a))
        self.plot_fft(ax, fft.fft(a, n, axis=0), rate, **kw)

    def diff_plot(self, valid, ax, x, fd, fmt, color, label=None):
        idx = self.calc.ir_smoother.get_indexlist(x, 0, valid)
        if len(idx) == len(x):
            return
        if len(idx) > 0:
            x = x.copy()
            x[idx] = "nan"
            fd = fd.copy()
            fd[idx] = "nan"
        l = ax.semilogx(x, fd, fmt, color=color)
        if label is not None:
            l[0].set_label(label)

    def on_display_freq(self, o):
        self.calc.status("generating plot")
        g = self.builder.get_object
        plot_ir = g("plot_ir").get_active()
        plot_orig = g("plot_orig").get_active()
        plot_rec = g("plot_rec").get_active()
        plot_diff = g("plot_diff").get_active()
        display_smooth = self.display_smooth.get_active()
        self.calc.invalidate_ir()
        rate = self.get_sample_rate()
        if plot_ir or plot_diff:
            n = max(2**16, len(self.calc.ir))
            ir_fft = fft.fft(self.calc.ir, n, axis=0)
        freq = fftfreq2(len(self.calc.f1), 1.0/rate)
        if display_smooth:
            x = np.logspace(np.log10(20), np.log10(rate/2), 1000)
        else:
            x = freq
        if plot_orig or (plot_diff and not self.orig_ir):
            f1 = fft2spectrum(self.calc.f1)
            if display_smooth:
                f1 = SmoothSpectrumSpline(freq, f1, rate)(x)
        if plot_rec or (plot_diff and not self.orig_ir):
            f2 = fft2spectrum(self.calc.f2)
            if display_smooth:
                f2 = SmoothSpectrumSpline(freq, f2, rate)(x)
        fig = plt.figure("Spec - IR Frequency Domain")
        fig.set_facecolor('0.22')
        fig.clear()
        ax = fig.add_subplot(111)
        if plot_orig:
            ax.semilogx(x, f1, color='green')[0].set_label("Destination")
        if plot_rec:
            ax.semilogx(x, f2, color='blue')[0].set_label("Source")
        if plot_diff:
            if self.orig_ir:
                self.plot_orig_ir(ax, rate, linestyle='--', color='red')
            else:
                fd = f1-f2
                self.diff_plot(True, ax, x, fd, ':', "red")
                self.diff_plot(False, ax, x, fd, '--', "red", "Difference")
        if plot_ir:
            self.plot_fft(ax, ir_fft, rate, color='black',
                    label="IR [%d frames]" % len(self.calc.ir)
                    )
        ax.legend(loc='best')
        ax.get_xaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        #ax.set_axis_bgcolor('0.66')
        ax.xaxis.label.set_color('0.77')
        ax.tick_params(axis='x', colors='0.77')
        ax.yaxis.label.set_color('0.77')
        ax.tick_params(axis='y', colors='0.77')
        self.calc.status.clear()
        plt.grid()
        plt.xlabel('Hz')
        #plt.ylabel('dB')

    def on_display_time(self, o):
        self.calc.status("generating plot")
        self.calc.invalidate_ir()
        f = self.calc.ir
        x = np.arange(len(f))/self.get_sample_rate()
        fig = plt.figure("Spec - IR Time Domain")
        fig.set_facecolor('0.22')
        fig.clear()
        ax = fig.add_subplot(111)
        f = f / np.amax(abs(f))
        if self.builder.get_object("log").get_active():
            l = ax.plot(x, 20*np.log10(abs(clipdb(f,-100))))
        else:
            l = ax.plot(x, f)
        if len(l) == 1:
            l[0].set_label("IR [%d frames]" % len(f))
        else:
            l[0].set_label("IR left")
            l[1].set_label("IR right")
        ax.legend(loc='best')
        #ax.set_axis_bgcolor('0.66')
        ax.xaxis.label.set_color('0.77')
        ax.tick_params(axis='x', colors='0.77')
        ax.yaxis.label.set_color('0.77')
        ax.tick_params(axis='y', colors='0.77')
        self.calc.status.clear()
        plt.grid()


def main():
    parser = argparse.ArgumentParser(
        description='Calculate an IR to match a spectrum')
    parser.add_argument("specfile", nargs="?", help="project file")
    parser.add_argument("orig_ir", nargs="?", help="debug: IR to reproduce")
    parser.add_argument("--samplerate", metavar="SR", type=float, default=48000.0,
                        help="set samplerate (when --no-jack), default: %(default)s")
    parser.add_argument("--soundfile", metavar="name",
                        help="debug: writeout input file convoluted with calculated IR")
    args = parser.parse_args()
    matplotlib.interactive(True)
    SpecWindow(args)
    Gtk.main()
