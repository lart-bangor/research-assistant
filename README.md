# Lart Research Client App

An app to collect survey-type data for research on regional and minority languages. Developed by the Language Attitudes Research Team at Bangor University.

## Contributing

### Set up your development environment

#### Git cloning the source code

If you haven't yet, you'll first need to install [git](https://git-scm.com/). You can easily check whether git is installed by typing `git --help` in a terminal window. If you get the git help, you don't have to install it.

When you have git installed, make a directory where you want to house the source code for the project (e.g. `/home/users/jane.doe/dev/lart-rc`) and open it in a terminal.

Inside the terminal, and inside the project directory you just set up, then type the command `git clone https://github.com/lart-bangor/lart-research-client.git`. You may be prompted for your [GitHub](https://github.org/) username and password, or maybe not.

This should download a copy of the entire sourcecode and some ancillary project files into the project directory.

#### Setting up python

This project requires [Python](https://python.org) version 3.10.x. If you are on Windows and either have Python installed already or aren't quite sure, try opening a terminal and typing `py -0`. If this prints out a list which includes `-3.10-64` or `-3.10-32` you're good to go, otherwise you'll need to download and install Python 3.10 (we recommend you install it system-wide and with the py-launcher option). If you're on a different system, try running `python --version` from the terminal. If you get a nothing or a version number below 3.10 please find instructions online on how to install Python 3.10 for your system.

Once you have Python 3.10 set up, you'll need to install [pipenv](https://pipenv.pypa.io/en/latest/), which is the tool we're using to manage project dependencies and virtual environments. At the terminal, just type `pip install pipenv` (or if that doesn't work, try `pip3 install pipenv`).

#### Setting up the virtual environment and dependencies

Now head back to the project directory in a terminal. If you type `dir` on Windows or `ls -l` on Linux and MacOS you should see a list of files including `manage.py` and `setup.cfg` and a folder named `lart_research_client`. If you don't you're in the wrong directory somewhere and need to go to the same directory where you exectured `git clone` earlier.

Now, inside the project directory, run `pipenv install --dev`. This will instruct pipenv to create a virtual environment and then install all the project's dependencies, including all the other development dependencies it has (within python, at least).

#### Giving it a test spin

To check that everything is working, inside the project directory, first run `pipenv shell` to activate the virtual environment.

Now try running `py -m lart_research_client` (on Windows) or `python -m lart_research_client` (on Linux and MacOS). Hopefully you'll see the app pop up (or at least get a useful error message!).

#### The project management utility: manage.py

The project includes its own little script to simplify many common project management tasks. From inside the project directory, you can run the following commands:
```sh
python manage.py run        # runs the app from the source files
python manage.py debug      # runs the app in debug mode
python manage.py clean      # cleans up your project directory
python manage.py build      # builds an executable with PyInstaller
```
