# SpecMatch 

![SpechMatch](https://github.com/brummer10/SpecMatch/blob/main/SpecMatch.png?raw=true)

A little python3 script to compare the spectrum of two sound-snippets and generate a
Impulse Response File from the different.

## Installing:
----------------
Dependencies:
 - python3 gi, os, json, argparse, numpy, matplotlib, pydub, scipy, soundfile

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
first start a file selection window will appear enter a project name.
On subsequent launches the last selected project will be opened
automatically. You can use the "Change File" button to select another
project file or create a new one (changes in projects will be
auto-saved).

Click on "Destination Sound", this is the Sound you want to match, and select a file.
The sound snipped should not be much longer than 10 seconds. 
For stereo sounds, you can select one of the channels (or
the sum) or produce a stereo IR.

Use "Source File" to select a other Sound snippet,
this is the Sound you wont to match the destignation, for comparison.

Now you could do a Frequency Plot to see the differences in the Frequency domain.
You could as well do a Time Plot.

For the generated IR-File you could set the normalise level (default -25 dBFS), 
select the size (default 3500 samples)
and you could select the Noise Level, that means below the selected level,
the signal will be threaded as Noise (default -60 dB).

You could select if you wish to generate a mono or a stereo IR-File, then you could 
go to Generate IR. 
Select were you wont to save it, and give a name for it.  
