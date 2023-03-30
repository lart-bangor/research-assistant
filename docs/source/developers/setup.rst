Setting up the development environment
======================================

This article will guide you through the setup of the development environment, aimed primarily at those with
relatively little previous experience of software development.

.. tip::

   If you're a seasoned developer, this guide will probably be a bit verbose for your taste, so if you know what you're
   doing you might just want to install any of the tools listed below (if you don't have them already), fork
   the repo, and run ``pipenv install --dev`` in the root of the source tree to get going.


.. _install_pre-requirements:

Installing the pre-requirements
-------------------------------

To work on the L'ART Research Client codebase, you need to have at least the following:

* `git <https://git-scm.com>`_ -- The version management system we use
* `python <https://python.org>`_ (version >= 3.10) -- The primary programming language of the app
* `pipenv <https://pipenv.pypa.io/>`_ -- The python package we use for virtual environments and dependency management
* `chrome <https://www.google.com/chrome/>`_ -- The browser we use to display the app's user interface

If you want to build the documentation locally, you will also need to have `jsdoc <https://jsdoc.app/>`_ installed.

Below are some examples of how you could install this software on various systems, e.g. Windows 10 or 11 if you use
``winget``, and Ubuntu Linux (note that the newest releases of Ubuntu will have Python > 3.10 already
installed). Please apply these with care. If you're not sure about any of this, it's best to go to the website of
the respective software (linked above) and just follow their installation instructions!

.. tab:: Windows 10/11 (winget)

   .. code-block:: powershell

      # Windows Terminal / PowerShell
      # Install Google Chrome
      winget install -e --id Google.Chrome
      # Install Git
      winget install -e --id Git.Git
      # Install Python 3.10+
      winget install -e --id Python.Python.3.10
      # Install pipenv
      pip install pipenv
      # Optional: Install npm and jsdoc (only needed to generate documentation)
      winget install -e --id OpenJS.NodeJS.LTS
      npm install -g jsdoc

.. tab:: Ubuntu Linux < 22.04 (apt)

   .. code-block:: console

      $ # Ubuntu Linux < 22.04
      $ # First make sure the system's packaged and package index are up-to-date
      $ sudo apt update && sudo apt upgrade -y
      $ # Install Google Chrome
      $ sudo apt install libxss1 libappindicator1 libindicator7
      $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
      $ sudo apt install ./google-chrome*.deb
      $ rm ./google-chrome*.deb
      $ # Install Git
      $ sudo apt install git -y
      $ # Check your current python version
      $ python3 --version
      Python 3.9.4
      $ # !! You should only run the next command if your python version is below 3.10.x !!
      $ sudo apt install software-properties-common
      $ sudo add-apt-repository ppa:deadsnakes/ppa
      $ sudo apt update && sudo install python3.10 -y
      $ # Now check that you have python3.10 running:
      $ python3.10 --version
      Python 3.10.5
      $ # Install pipenv (if you already had python 3.10 show above, just use "python3" instead of "python3.10")
      $ python3.10 -m pip install pipenv
      $ # Optional: Install jsdoc (only needed to generate documentation)
      $ sudo apt install npm -y
      $ sudo npm install -g jsdoc


.. tab:: Ubuntu Linux >= 22.04 (apt)

   .. code-block:: console

      $ # Ubuntu Linux >= 22.04
      $ # First make sure the system's packaged and package index are up-to-date
      $ sudo apt update && sudo apt upgrade -y
      $ # Install Google Chrome
      $ sudo apt install libxss1 libappindicator1 libindicator7
      $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
      $ sudo apt install ./google-chrome*.deb
      $ rm ./google-chrome*.deb
      $ # Install Git
      $ sudo apt install git -y
      $ # Check your current python version is >= 3.10.0
      $ python3 --version
      Python 3.10.5
      $ # Install pipenv
      $ python3 -m pip install pipenv
      $ # Optional: Install jsdoc (only needed to generate documentation)
      $ sudo apt install npm -y
      $ sudo npm install -g jsdoc


Following the installation of the above, make sure that both :command:`python` and :command:`pipenv` are on your
:envvar:`PATH` environment variable. You may need to re-start your terminal, or log out and log back in for this
to be the case. To test, just open a new terminal window and type both ``python --version`` and
``pipenv --version``. If this does not work, you need to find out how to add them to the :envvar:`PATH`
environment variable on your system before proceeding.


.. important:: Know your machine!

   For most of what follows we will assume you have the above software installed and know the correct commands
   to use. This is especially important for Python, which depending on your installation may go by different names.

   If you aren't sure which Python command to use, open a command-line/terminal window and try the following
   commands in order:

   * ``py --version``
   * ``python --version``
   * ``python3 --version``
   * ``python3.10 --version``

   The first one of these that doesn't give you an error message and prints a Python version that is at least
   3.10.0 is the command you should use for everything else.

   For simplicity, unless specifying something OS-specific, we will just use ``python`` throughout the
   documentation -- it's *your responsibility* to adapt accordingly.


If you have the pre-requirements above out of the way, you can follow these steps to get the source code and all
dependencies set up.


Get a copy of the source code
-----------------------------

These are the steps you need to follow to get a current copy of the sourcecode:

#. Open a terminal (console / command-line prompt)

#. Go to (or make) your prefered directory for development.

   For example ``cd C:\Users\florian\Development`` (Windows) or ``cd /home/florian/development``
   (Linux). If you don't have a directory you use for software development yet, you can use the
   :command:`mkdir` command to create it, then :command:`cd` into it.

#. Clone the repository with ``git clone https://github.com/lart-bangor/research-client.git``.

   This will make a local copy of the remote git repository, to which you can then make local
   changes and which you can sync back and forth with the remote repository (called *pulling*
   and *pushing*).

   .. tip:: Fork the repository before cloning it...

      You might want to make a *fork* of our repository on GitHub and work on that fork, so that
      your own work benefits from the added security of having the version control history in the
      cloud even if you do not have write permissions to our repository.
      
      You will also have to make a fork if you want to make a *pull request* later, which is
      what you would do to have your modifications adopted in our official repository and
      included in future builds of the L'ART Research Client.

      For more information, check out how to
      `fork a repo <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ in the
      `GitHub Quickstart Guide <https://docs.github.com/en/get-started/quickstart>`_.

#. Enter the project's root directory.

   You can do this with the command ``cd ./research-client``. If you now type
   ``ls`` (Linux) or ``dir`` (Windows), you should see a list of files including one called
   :file:`manage.py` -- if you see that you know that your code has cloned successfully and
   you are in the project's root directory.


Set up pipenv and install dependencies
--------------------------------------

We use :command:`pipenv` to manage the environment and dependencies.
This makes it very easy to ensure that everyone working on the app can keep their
dependencies up-to-date and have the same, stable environment for development.

After cloning the source code repository, there are just two steps to get this all set up.
We're assuming you're still in the same terminal session as above, inside the project's root
directory (see the last step above).

#. Run ``pipenv install --dev``.

   This will set up a new virtual environment (so it doesn't get polluted by any 
   other packages or changes on your system's Python installation, and vice-versa), and then install all the
   Python packages you need. The ``--dev`` switch is quite important here, because without it you will be able
   to run the app from the terminal, but you won't be able to build the app binaries or the documentation for
   example.

#. Activate the pipenv environment with ``pipenv shell``.

   You now have to actually activate the virtual environment, so your terminal knows to use the isolated copy
   of Python it made for this project instead of the system installation. You activate the environment by
   typing ``pipenv shell`` (normally, after this you will see something like ``(research-client)`` at the
   start of your command prompt.)

   .. important:: Remember pipenv!
      
      It's important to remember to activate and use :command:`pipenv` whenever you start working on the project.
      If you don't, you'll probably get error messages, and if you then just use regular ``pip`` to try and
      resolve these you'll mess up your system-wide installation and run the risk of introducing new
      dependencies that can break the code, without other people being able to later see what these
      dependencies were. It might also prevent you from being able to build the binaries from the source.
      
      So, every time you open a terminal to work on the project, remember to use ``pipenv shell`` first.
      Every time you install a package, remember to use ``pipenv install <pkgname>`` or
      ``pipenv install <nobr>--dev</nobr> <pkgname>`` (if the package is only needed for development,
      but not for the version the end-user gets).


.. _run_from_source:

Running the app from the source
-------------------------------

Now let's test that things are working as they should. Open a terminal and go to the directory to which
you've cloned the source code, e.g. :file:`C:\\Users\florian\Development\research-client` (Windows)
or :file:`/home/florian/development/research-client` (Linux). You know that you are in the right
directory if you type ``ls`` (Linux) or ``dir`` (Windows) and the list shown contains a file
named :file:`manage.py`.

Now just type ``python manage.py run`` in your terminal and hit :kbd:`Enter`. If you get an error,
something in the above steps probably went wrong --- check which of the steps the error message
seems to relate to and try again from there. If you see the app's main window and some text on
the terminal telling you that it is running, then you should be good to go.


.. tip:: Use a dedicated code editor...

   If you use `VS Code <https://code.visualstudio.com/>`_ as your editor, you can tell it to
   automatically activate the :command:`pipenv` environment when you open your source code.
   
   Just install the `Python extension <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_
   in VS Code. Then press :kbd:`Ctrl+Shift+P` and type
   *Python: Select Interpreter*, then select the one showing "(PipEnv)" in parentheses at the end.
   
   Similar extensions are available for most other editors and IDEs, it's worth consulting their
   documentation on this.


Bonus: Consider using a specialised source code editor
------------------------------------------------------

If you have only written a few lines of Python, HTML, or JavaScript here and there in the past,
chances are that you've just used a general purpose text editor in the past, such as *notepad*
or *gedit*.

We recommend that you consider a modern specialised source code editor or
:abbr:`IDE (Integrated Development Environment)` instead. The extra features they offer, such
as running terminal commands from within the editor, integrating with git, showing type-error
hints in your code, etc. will pay of quickly on a codebase like this.

Some free options you might want to consider:

* `VS Code`_: Lightweight, responsive, platform-independent. Used by most people on our team.
* `Geany <https://www.geany.org/>`_: Super-lightweigt, responsive, platform-independent. A popular choice for those that don't
  want to run just a 'free' Microsoft product or otherwise don't like VS Code.
* `Spyder <https://www.spyder-ide.org/>`_: Medium-weight, aimed primarily at scientific computing, a bit like
  `RStudio <https://posit.co/products/open-source/rstudio/>`_. Worth considering if you want to also run data analysis in Python.
* `PyCharm <https://www.jetbrains.com/pycharm/>`_: A more heavy-weight IDE with many features, quite popular and probably a bit
  more than what is needed. It's commercial software, but there is a free community version you can download, and if you're an
  academic or student you can get a free full license.
* `vim <https://www.vim.org/>`_: Lightweight, super-fast, very powerful terminal-based editor. If you prefer not to use a graphical
  user interface and stay on the command line this is probably for you, but the learning curve is rather steep.
