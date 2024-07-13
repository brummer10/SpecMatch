# SpecMatch

A little Python 3 program to compare the spectrum of two sound files and
generate a (smoothed) impulse response file (IR) from the spectral difference.

<p align="center">
    <img src="https://github.com/brummer10/SpecMatch/blob/main/SpecMatch.png?raw=true" />
</p>


## Dependencies

* [Python 3]
* [PyGObject]
* [NumPy]
* [matplotlib]
* [pydub]
* [SciPy]
* [soundfile]
* [resampy]


## Installation


### User installation (using pipx)

To install SpecMatch from [PyPI] for your user account, it is recommend to use
[pipx]:

    pipx install specmatch

This will install the `specmatch` package and all dependencies into an isolated
Python environment and a `specmatch` command into `~/.local/bin`. Make sure
this directory is included in your `PATH`.

To uninstall the package and its pipx environment again, run:

    pipx uninstall specmatch


### System-wide installation (using pip)

To install SpecMatch system-wide instead run:

    sudo pip install specmatch

**Warning:** This by-passes your distribution's package management and can
interfere with your Python system installation by overwriting Python packages
installed in your system with newer and potentially incompatible versions.
Therefor this method is *not recommended* and should only by used if you are
aware of and accept the risks involved. On some distributions, you may also
need to add the `--break-system-packages` option for this method to work at
all.

To uninstall the package, run:

    sudo pip uninstall specmatch


### Building from source (for packagers)

To build a wheel package, download and unpack the source distribution or clone
the Git repository and change into the source directory. Make sure you have the
Python [build] and [installer] packages installed and run:

    python3 -m build --wheel

This will create a temporary Python environment, install the build dependencies
into it and build the wheel. If you want the build to use the system-installed
packages instead, use the `--no-isolation` option. In this case you also need
to make sure the Python package [hatchling] is installed, which is used as
a package building backend.

To install the wheel package, run:

    python3 -m installer ./dist/specmatch-*.whl

You can use the `--destdir` option to set the root of the installation
destination to something other than `/`.


## Running

When installed system-wide, SpecMatch can be started from your desktop
environment's menu. Alternatively, it can be started with the command
`specmatch` from the command line.

<p align="center">
    <img src="https://github.com/brummer10/SpecMatch/blob/main/desktop/specmatch.svg" width="150" />
</p>


### Without installation

SpecMatch can be used without installation directly from the source tree. Just
go to the source folder and run:

    python3 -m specmatch

When you run SpecMatch this way, you need to ensure that all dependencies are
already available in your current Python environment.


## Usage

SpecMatch works with project files (extension `.specmatch`). When first
started, a file selection window will appear were you need to choose a project
name. After that the SpecMatch Window will appear. On subsequent launches the
last selected project will be opened automatically. You can use the "Change
File" button to select another project file or create a new one (changes in
projects will be auto-saved).

Click on "Destination Sound". This is the sound file you want to match, and
select a file. For stereo sounds, you can select one of the channels (or the
sum) or produce a stereo IR.

Use "Source File" to select a other sound file. This is the sound you want to
match to the destination.

Both files can have different sizes, it won't matter, since the program only
compares the frequency spectra of the Files.

Now you can do a frequency plot of the source and the destination file.
The plot also shows the differences and the resulting smoothed IR file.
You can show a time plot as well.

To generate the IR file you set the normalisation level (default -25 dBFS),
select the resulting IR file size (default 3500 samples) and select the noise
level, i.e. the level below which the signal will be treated as noise (default
-60 dB). Additionally it is possible to set the maximum magnitude difference,
meaning the level below the maximum magnitude, where the minimum magnitude gets
clipped (default -100dB).

You can generate a mono or a stereo IR-File.

When you press "Generate IR" a file browser will pop up and lets you choose the
name and path where to save the generated IR file.


## Author and License

SpecMatch was created by *Hermann Meyer*  and is released under the MIT
License. Please see the file [LICENSE.md](./LICENSE.md) for details.


[build]: https://pypi.org/project/build/
[hatchling]: https://pypi.org/project/hatchling/
[installer]: https://pypi.org/project/installer/
[matplotlib]: https://pypi.org/project/matplotlib/
[NumPy]: https://pypi.org/project/numpy/
[pipx]: https://pypi.org/project/pipx/
[pydub]: https://pypi.org/project/pydub/
[PyGObject]: https://pypi.org/project/pygobject/
[PyPI]: https://pypi.org/
[Python 3]: https://python.org/
[resampy]: https://pypi.org/project/resampy/
[SciPy]: https://pypi.org/project/scipy/
[soundfile]: https://pypi.org/project/soundfile/
