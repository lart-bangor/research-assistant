Building from source
====================

This guide will describe how to build the app for distribution with
`PyInstaller <https://pyinstaller.org/>`_ and `Inno Setup <https://jrsoftware.org/isinfo.php>`_
(if you're building on Windows). We assume that you have successfully
followed the steps to :doc:`setup` and :ref:`run_from_source` works already.


Additional build dependencies
-----------------------------

The L'ART Research Assistant app is built with `PyInstaller`_, and `Inno Setup`_ is used on
Windows to package it up as an executable installer.

PyInstaller
^^^^^^^^^^^

PyInstaller will already have been installed when you have installed the development
dependencies with :code:`pipenv install --dev` while :doc:`setup`. If you get an
error saying that PyInstaller could not be found, just run that command again.

Inno Setup
^^^^^^^^^^

Inno Setup is only needed if you're building on Windows --- so if you're on Linux or
MacOS you can just ignore anything to do with Inno Setup.

On Windows, Inno Setup needs to be installed on your system or the build process will
fail. Follow these simple steps to install it:

#. Download the latest version of Inno Setup from `<https://jrsoftware.org/isdl.php>`_.

#. Run the Inno Setup installer on your system to install it.

#. Check whether the command :command:`iscc` is on your system's :envvar:`Path`
   by opening a terminal window (:kbd:`Windows+R`, type :code:`cmd`, hit :kbd:`Enter`)
   and then entering the command :code:`iscc` followed by :kbd:`Enter`.

#. If you see soem text starting with something like "Inno Setup 6 Command-Line
   Compiler" followed by instructions, you're good to know and can skip to the next
   section. In the (very likely) event that you get an error instead, continue
   with the next step here.

#. Locate :file:`ISCC.exe` and note the path to the directory where it is located.
   This is probably `C:\\Program Files\\Inno Setup 6` or `C:\\Program Files (x86)\\Inno Setup 6`.

#. Either type "environment variables" in the Start search box and open the
   "Edit the system environment variables" shortcut that shows up, or go to
   :menuselection:`Settings -> System -> Advanced system settings`.

#. On the bottom of the dialog box, click on :guilabel:`Environment Variables...`.

#. Highlight the variable called :envvar:`Path` in the top half of the dialogue
   window, then click on :guilabel:`Edit`.

#. Click on :guilabel:`New` and add the path to the directory where Inno Setup
   (:file:`ISCC.exe` from before) is installed, e.g.
   `C:\\Program Files (x86)\\Inno Setup 6`.

#. Click :guilabel:`OK` repeatedly until all the dialogue windows are closed.

#. Start a *new* terminal window (it will not work in any terminal windows that
   were opened before you edited the :envvar:`Path` environment variable) and
   try running :code:`iscc` again --- it should work now, meaning you're ready
   to build the app on Windows (if it still doesn't work, you probably entered
   the wrong path two steps earlier).


Building the app and the installer
----------------------------------

Building the app is super simple. Just go to the folder containing the
:file:`manage.py` file, make sure you're running in the :command:`pipenv`
shell (if you're not sure, just run :code:`pipenv shell` again), and then
run the command :code:`py ./manage.py build` (on Windows) or
:code:`python3.10 manage.py build` (on Linux and MacOS).

The folder :file:`./build` will contain all the build artificats and direct
outputs from PyInstaller.

The folder :file:`./dist` will contain the distributables for the app,
in a subfolder named after the system on which they were built. For example
on Linux, there will be a tarball (:file:`*.tar.gz`) in :file:`./dist/linux`,
while on Windows there will be both a ZIP archive and an executable
(:file:`.exe`) installer in :file:`./dist/win64`, which can be used to
install the app.


Building the documentation
--------------------------

The documentation is built automatically on `Read the Docs <http://readthedocs.io/>`_
whenever a pull request, push or merge succeeds on the :code:`docs` branch of the
repository. Even so, if you're updating the documentation (even in the inline
documentation in the Python and JavaScript files) it might be desirable to build it
locally to make sure any changes are reflected as they should be and nothing breaks.

Additional documentation dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To build the documentation, you need to additionally install `jsdoc <https://jsdoc.app/>`_,
as shown as an optional step in :ref:`install_pre-requirements`.

:command:`jsdoc` is used to extract documentation from within the JavaScript files that
provide the app's APIs in the frontend.

You can check whether :command:`jsdoc` works by opening a terminal and typing
:code:`jsdoc`. If it is installed correctly and available on your :envvar:`Path`,
it should print something like "There are no input files to process." --- otherwise
you will need to install it and make sure it is available on the :envvar:`Path` before
you can build the documentation.

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Building the documentation is just as simple as building the app. Like with
building the app, make sure you're in the directory containing the file
:file:`manage.py` and that you're in the :command:`pipenv` shell (any doubt,
just run :code:`pipenv shell`). Then just run the command
:code:`py ./manage.py docs` (on Windows) or :code:`python3.10 manage.py docs`
(on Linux and MacOS).

The folder :file:`./dist/docs/html` will contain the HTML version of the
documentation (we do not currently build the latex/PDF version offline, as
this has too many dependencies and quirks to work reliably from one person to
the next).

Cleaning up after yourself
--------------------------

Just like with your bedroom, it's important to keep your development environment
tidy. So once you've completed your builds and inspected that everything is as
it should be, you probably want to clean up all the artifacts, local documentation
and distributables generated by the build process...

Just run :code:`py ./manage.py clean` (on Windows) or :code:`python3.10 manage.py clean`
(on Linux or MacOS), and the *manage.py* utility will make everything nice and
tidy again 🧹.


Known issues with building
--------------------------

* Building fails with Python version 3.10.0 due a bug in Python that affects
  PyInstaller (`issue <https://github.com/pyinstaller/pyinstaller/issues/6301>`_).
  If your Python version is 3.10.0 then update to 3.10.1 or later (but not 3.11.x,
  for which nothing has been tested, ...yet).
