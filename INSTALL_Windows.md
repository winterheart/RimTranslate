# Installation for Windows

Installing dependencies for Windows is little bit complicated so here quick walktrough.

First, you need to install Python itself. Due lack binary support for 3.5 from lxml you need to install Python 3.4.x (you can find it [here](https://www.python.org/downloads/windows/)). You can install either 32- or 64-bit. Just remember that choice since you will need to install accorging binary lxml. During installing you may check option "Add python to PATH variable" for ease of use later (you need to restart system for apply).

After that download latest lxml **EXE**-file from [here](https://pypi.python.org/pypi/lxml/3.6.0) (at time of writing, latest version of lxml don't have precompiled binary). Make sure that you choosed correct python version (should be 3.4) and architecture (win32 or amd64). Installation is simple - just run it. Installator will detects automatically Python version and installs lxml to right place.

One thing that left is polib library. Since it not require any external dependencies, included PIP packet manager can handle with it. Launch command-line console (PowerShell or cmd.exe) and just type `python -m pip install polib`.

Now you ready for actual work.
