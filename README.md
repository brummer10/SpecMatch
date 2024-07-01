# SpecMatch 

<p align="center">
    <img src="https://github.com/brummer10/SpecMatch/blob/main/SpecMatch.png?raw=true" />
</p>

A little python3 script to compare the spectrum of two sound-files and generate a
(Smoothed) Impulse Response File from the Spectral difference.

## Installing:
----------------
Dependencies:
 - python3 PyGObject, os, numpy, matplotlib, pydub, scipy, soundfile, resampy

run 

`python3 setup.py  bdist_wheel`

or use the new python3-build

`python3 -m build --wheel`

to build a wheel package and install it with 

`sudo pip install ./dist/specmatch-0.9-py3-none-any.whl`

to uninstall it run

`sudo pip uninstall ./dist/specmatch-0.9-py3-none-any.whl`

## Running:
----------------

SpecMatch could be used without installing directly from the source tree, 
just go to the specmatch folder and run ./specmatch
You may need to make the file specmatch executable and ensure that all dependencies been solved.

When installed, it should be available from your desktop environment or the command
line as "specmatch".


<p align="center">
    <img src="https://github.com/brummer10/SpecMatch/blob/main/desktop/specmatch.svg" width="100" />
</p>

## Usage:

SpecMatch works with project-files (extension .specmatch). On the
first start a file selection window will appear were you need to enter a project name.
After that the SpecMatch Window will appear.
On subsequent launches the last selected project will be opened
automatically. You can use the "Change File" button to select another
project file or create a new one (changes in projects will be
auto-saved).

Click on "Destination Sound", this is the Sound File you want to match,
and select a file. For stereo sounds, you can select one of the channels (or
the sum) or produce a stereo IR.

Use "Source File" to select a other Sound File,
this is the Sound you wont to match the destination.

Both Files could have different size, no matter, as here we only compare the
Frequency Spectrum of the Files. 

Now you could do a Frequency Plot of the Source and the Destination File.
Additional the differences and the resulting Smoothed IR-File will be shown.
You could as well do a Time Plot.

To generated the IR-File you could set the normalise level (default -25 dBFS), 
select the resulting IR-File-size (default 3500 samples)
and you could select the Noise Level, that means the level below which
the signal will be threaded as Noise (default -60 dB).
Additional it's possible to set the maximum magnitude difference,
means the level below the maximum magnitude, 
were the minimum magnitude get clipped (default -100dB).

You could generate a mono or a stereo IR-File.

When you press "Generate IR" a File-browser will pop up and
let you choose were, and under which name, to save the IR-File.  
