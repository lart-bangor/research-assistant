# Lart Research Client App

An app to collect survey-type data for research on regional and minority languages. Developed by the Language Attitudes Research Team at Bangor University.

## Contributing

### 1 Set up your development environment

#### 1.1 Git cloning the source code

If you haven't yet, you'll first need to install [git](https://git-scm.com/). You can easily check whether git is installed by typing `git --help` in a terminal window. If you get the git help, you don't have to install it.

When you have git installed, make a directory where you want to house the source code for the project (e.g. `/home/users/jane.doe/dev/lart-rc`) and open it in a terminal.

Inside the terminal, and inside the project directory you just set up, then type the command `git clone https://github.com/lart-bangor/lart-research-client.git`. You may be prompted for your [GitHub](https://github.org/) username and password, or maybe not.

This should download a copy of the entire sourcecode and some ancillary project files into the project directory.

#### 1.2 Setting up python

This project requires [Python](https://python.org) version 3.10.x. If you are on Windows and either have Python installed already or aren't quite sure, try opening a terminal and typing `py -0`. If this prints out a list which includes `-3.10-64` or `-3.10-32` you're good to go, otherwise you'll need to download and install Python 3.10 (we recommend you install it system-wide and with the py-launcher option). If you're on a different system, try running `python --version` from the terminal. If you get a nothing or a version number below 3.10 please find instructions online on how to install Python 3.10 for your system.

Once you have Python 3.10 set up, you'll need to install [pipenv](https://pipenv.pypa.io/en/latest/), which is the tool we're using to manage project dependencies and virtual environments. At the terminal, just type `pip install pipenv` (or if that doesn't work, try `pip3 install pipenv`).

#### 1.3 Setting up the virtual environment and dependencies

Now head back to the project directory in a terminal. If you type `dir` on Windows or `ls -l` on Linux and MacOS you should see a list of files including `manage.py` and `setup.cfg` and a folder named `lart_research_client`. If you don't you're in the wrong directory somewhere and need to go to the same directory where you exectured `git clone` earlier.

Now, inside the project directory, run `pipenv install --dev`. This will instruct pipenv to create a virtual environment and then install all the project's dependencies, including all the other development dependencies it has (within python, at least).

#### 1.4 Giving it a test spin

To check that everything is working, inside the project directory, first run `pipenv shell` to activate the virtual environment.

Now try running `py -m lart_research_client` (on Windows) or `python -m lart_research_client` (on Linux and MacOS). Hopefully you'll see the app pop up (or at least get a useful error message!).

#### 1.5 Running the app during development

The best and easiest way to run the app while working on the code is to use the `manage.py` utility (see also section 3 below). Make sure to always activate the pipenv shell first (just run `pipenv shell` inside the folder containing `manage.py`).

To just run the app from the current source code "as normal", run `python manage.py run`. The app will run, behave, and close pretty much as it would when installed eventually.

For debugging, you might want to try running `python manage.py debug` instead. This will run the app from the source code, but instead of ending the process when an error occurs or the app process ends, it will leave you with an interactive python interpreter at the end, so you can import and inspect all the python modules and see what their state was when the error occured (you can also force this with a breakpoint or by force-quitting execution, e.g. with Ctrl+X which raises a KeyboardInterrupt). Depending on your configuration, debug mode might also print out many more information and error messages on the terminal.

### 2 Set up your build environment

#### 2.1 PyInstaller

The app is built into a installable package using [PyInstaller](https://pyinstaller.org/). This will already have been installed if you followed the step with `pipenv install --dev` above. If you get an error saying PyInstaller couldn't be found, try re-running that command (remember to do this inside the directory which itself contains the `manage.py`, `Pipfile`, `lart_research_client`, etc.).

#### 2.2 Inno Setup (Windows)

The executable installer for Windows is built using [Inno Setup](https://jrsoftware.org/isinfo.php), and this needs to be installed on your system or the build process will fail. Download Inno Setup from [https://jrsoftware.org/isdl.php] and install it on your system.

Once you have installed Inno Setup, you have to make sure its available on the system path. The best way to do this is to open up a terminal window (Windows+R, then type `cmd` and press Enter). Now type `iscc` and press enter. If this shows some text starting with something like "Inno Setup 6 Command-Line Compiler" and then some instruction, you're good to go. If it doesn't, you have to add the directory containing `ISCC.exe` (the folder where you installed Inno Setup) to the path environment variable. This might be `C:/Program Files/Inno Setup 6` or `C:/Program Files (x86)/Inno Setup 6`, but do double check. Either type "environment variables" in the Start search box, or go to Settings -> System -> Advanced system settings, then on the bottom of the dialog box click on `Environment Variables...`. Highlight the variable called `Path` in the top half of the dialogue window, click on `Edit` and add the path where Inno Setup is installed, e.g. `C:/Program Files (x86)/Inno Setup 6`. Click `OK` and close all the dialogue windows. Start a new terminal window (it won't work in one opened before you modified the path) and try running the `iscc` command again - it should work now, meaning you're ready to build the app on windows.

#### 2.3 Building the app and installer

Building is super simple, just go to the folder containing the `manage.py`, make sure you're running in pipenv shell (if you're not sure, just run `pipenv shell` again), then run `py manage.py build`. The folder `./build` will contain all the build artifacts and direct outputs from PyInstaller, and the `./dist` folder will contain a ZIP file and (on Windows) an executable (.exe) file which can be used to install the app.

### 3 The project management utility: manage.py

The project includes its own little script to simplify many common project management tasks. From inside the project directory, you can run the following commands:
```sh
python manage.py -h         # show the available commands
python manage.py run        # runs the app from the source files
python manage.py debug      # runs the app in debug mode
python manage.py clean      # cleans up your project directory
python manage.py build      # builds an executable with PyInstaller
python manage.py docs       # build the documentation
```
