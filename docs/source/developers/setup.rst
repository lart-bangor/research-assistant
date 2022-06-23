Setting up the development environment
======================================

Installing the pre-requirements
-------------------------------

To work on the LART Research Client codebase, you need to have at least the following:

* `git <https://git-scm.com>`_ -- The version management system we use
* `python <https://python.org>`_ (version >= 3.10) -- The primary programming language of the app
* `pipenv <https://pipenv.pypa.io/>`_ -- The python package we use for virtual environments and dependency management
* `chrome <https://www.google.com/chrome/>`_ -- The browser we use to display the app's user interface

Below are some examples of how you could install this software on various systems, e.g. Windows 10 or 11 if you use
``winget`` or ``choco``, and Ubuntu Linux (note that the newest releases of Ubuntu will have Python > 3.10 already
installed). Please apply these with care. If you're not sure about any of this, it's best to go to the website of
the respective software (linked above) and just follow their installation instructions!

.. tab:: Windows 10/11 (winget)

    .. code-block:: powershell

        # Install Google Chrome
        winget install -e --id Google.Chrome
        # Install Git
        winget install -e --id Git.Git
        # Install Python 3.10+
        winget install -e --id Python.Python.3
        # Install pipenv
        pip install pipenv


.. tab:: Windows 10/11 (choco)

    .. code-block:: powershell

        # Install Google Chrome
        choco install googlechrome
        # Install Git
        choco install git
        # Install Python 3.10+
        choco install python
        # Install pipenv
        pip install pipenv


.. tab:: Ubuntu Linux (apt)

    .. code-block:: console

        $ # First make sure the system's packaged and package index are up-to-date
        $ sudo apt update && sudo apt upgrade -y
        $ # Install Google Chrome
        $ sudo apt install libxss1 libappindicator1 libindicator7
        $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        $ sudo apt install ./google-chrome*.deb
        $ rm ./google-chrome*.deb
        # Install Git
        $ sudo apt install git -y
        # Check your current python version
        $ python3 --version
        Python 3.9.4
        # !! You should only run the next command if your python version is below 3.10.x !!
        $ sudo apt install software-properties-common
        $ sudo add-apt-repository ppa:deadsnakes/ppa
        $ sudo apt update && sudo install python3.10 -y
        # Now check that you have python3.10 running:
        $ python3.10 --version
        Python 3.10.5
        # Install pipenv (if you already had python 3.10 isntall, just use "python3" instead of "python3.10")
        $ python3.10 -m pip install pipenv

.. important:: Know your machine!

    For most of what follows in this Developers' Guide we will assume you have the above Software installed and
    know the correct commands to use. This is especially for Python, which depending on your installation may go
    by different names.

    If you aren't sure, open a command-line/terminal window and try the following commands in order:

    * ``py --version``
    * ``python --version``
    * ``python3 --version``

    The first one of these that doesn't give you an error message and prints a Python version that is at least
    3.10.0 is the command you should use for everything else.

    For simplicity, unless specifying something OS-specific, we will just use ``python`` throughout the
    documentation -- it's *your responsibility* to adapt accordingly.


Setting up the development environment
--------------------------------------

If you have the pre-requirements above out of the way, you can follow these steps to get the sourcecode and all
dependencies setup.

Get a copy of the sourcecode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are the steps you need to follow to get a current copy of the sourcecode:

#. Open a console (terminal / command-line prompt)
#. Go to (or make) your prefered directory for development, for example
   ``cd C:\Users\florian\development`` (Windows) or ``cd /home/florian/development`` (Linux/Unix). If you don't have
   a directory you use for software development yet, you can use the `mkdir` command to create it, then ``cd`` into
   it.
#. Clone the repository with ``git clone https://github.com/lart-bangor/lart-research-client.git``.



Set up a Python virtual environment and install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned above, we use *pipenv* to manage the environment and dependencies. This makes it very easy to ensure
that we all keep up-to-date and have the same, stable environment for development.

After cloning the sourcecode repository, there are just two steps to get this all set up (assuming you're still
in the same console session as above).

#. Run ``pipenv install --dev``. This will set up a new virtual environment (so it doesn't get polluted by any 
    other packages or changes on your system's Python installation, and vice-versa), and then install all the
    Python packages you need. The ``--dev`` switch is quite important here, because without it you will be able
    to run the app from the console, but you won't be able to build the app binaries or the documentation for
    example.
#. You now have to actually activate the virtual environment, so your console knows to use the isolated copy
    of Python it made for this project instead of the system installation. You activate the environment by
    typing ``pipenv shell`` (normally, after this you will see something like ``(lartrc)`` at the start of
    your command prompt.)


.. important:: Remember pipenv!
    It's important to remember to activate and use ``pipenv`` whenever you start working on the project.
    If you don't, you'll probably get error messages, and if you then just use regular ``pip`` to try and
    resolve these you'll mess up your system-wide installation and run the risk of introducing new
    dependencies that can break the code, without other people being able to later see what these
    dependencies were. It might also prevent you from being able to build the binaries from the source.

    So, every time you open a console to work on the project, remember to use ``pipenv shell`` first.
    Every time you install a package, remember to use ``pipenv install <pkgname>`` or
    ``pipenv install <nobr>--dev</nobr> <pkgname>`` (if the package is only needed for development, but not for the
    version the end-user gets).