# SpecMatch 

![SpechMatch](https://github.com/brummer10/SpecMatch/blob/main/SpecMatch.png?raw=true)

A little python3 script to compare the spectrum of two sound-files and generate a
Impulse Response File from the different.

## Installing:
----------------
Dependencies:
 - python3 gi, os, json, argparse, numpy, matplotlib, pydub, scipy, soundfile, resampy

Use "sudo ./install" to install under /usr/local (or
"sudo ./uninstall" to remove the installation).

For other target prefixes (like /usr) use
"sudo ./setup.py install --prefix=XXX" and consult the install script.
Undoing the installation needs to be done manually is this case.

SpecMatch could be used without installing directly from the source tree, 
just go to the specmatch folder and run ./specmatch
You may need to make the file specmatch executable to do so.

## Running:
----------------
It should be available from your desktop environment or the command
line as "specmatch".


## Usage:

SpecMatch works with project-files (extension .specmatch). On the
first start a file selection window will appear were you need to enter a project name.
After that the SpecMatch Window will appear.
On subsequent launches the last selected project will be opened
automatically. You can use the "Change File" button to select another
project file or create a new one (changes in projects will be
auto-saved).

Click on "Destination Sound", this is the Sound File you want to match,
and select a file.
For stereo sounds, you can select one of the channels (or
the sum) or produce a stereo IR.

Use "Source File" to select a other Sound File,
this is the Sound you wont to match the destignation, for comparison.

Both Files could have different size, no matter, as here we only compare the
Frequency Spectrum of the Files. 

Now you could do a Frequency Plot of the Source and the Destination File.
Additional the differences will be shown and the resulting Smoothed IR-File.
You could as well do a Time Plot.

To generated the IR-File you could set the normalise level (default -25 dBFS), 
select the resulting IR-File-size (default 3500 samples)
and you could select the Noise Level, that means the level below which
the signal will be threaded as Noise (default -60 dB).

You could select to generate a mono or a stereo IR-File.
When you press "Generate IR" a File-browser will pop up and
let you choose were, and under which name, to save the IR-File.  
