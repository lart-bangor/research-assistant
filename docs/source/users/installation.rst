Installation
============

Installing on Windows 10/11
---------------------------

#. Download the official Windows installer for the L'ART Research Assistant on Windows.

   You can find the latest release (as well as earlier versions) at
   `github.com/lart-bangor/research-assistant/releases <https://github.com/lart-bangor/research-assistant/releases>`_.

#. Once downloaded to your device, open the *Downloads* dialogue in the browser and click :guilabel:`Open file`.
   Alternatively, navigate to your :file:`Downloads` folder in File Explorer and double click on the installer file.

   .. figure:: figures/users_install_open_from_downloads.png
      :name: users_install_open_from_downloads
      :width: 400
      :alt: Screenshot of Windows download dialogue showing the downloaded installer file.

      Open file from downloads

   .. note::

      If you have Microsoft Defender active, you may be warned about running an unrecognised app.
      
      This is expected behaviour for unsigned software downloaded from the internet. It is meant to get you to
      check that you've downnloaded the Software from a reputable source before running it.
      
      *This is fine if you've used our official download link above!*
      
      Click :guilabel:`Run anyway` to continue with the installation.

   .. figure:: figures/microsoft_defender_smartscreen.png
         :name: microsoft_defender_smartscreen
         :width: 400
         :alt: An image of protection message from Windows taken from Microsoft Defender Smartscreen.

         Microsoft Defender SmartScreen

#. Select you preferred install mode.

   We recommend choosing :guilabel:`Install for me only` for most use cases, which
   will install the app only for the current user.
   
   *However*, you may wish to install the app for all users. For example, if you're installing on a
   shared university or lab computer and want to centrally manage the installation for all users
   (requires administrator privileges).

   If in any doubt, choose :guilabel:`Install for me only`.

   .. figure:: figures/user_install_mode_setup.png
      :name: user_install_mode_setup
      :width: 400
      :alt: Screenshot of selecting an install mode for users

      Install mode setup

#. Click :guilabel:`Yes` to allow L'ART Research Assistant to make changes to your device
   (namely, to install the app).

   .. figure:: figures/user_account_control_screen.png
      :name: user_account_control_screen
      :width: 400
      :alt: Screenshot of User Account Control Screen.

      User account control screen

#. Read and accept the licence agreement.

   You must accept the agreement before installation can begin.

   .. figure:: figures/user_install_license_agreement.png
      :name: user_install_license_agreement
      :width: 400
      :alt: Screenshot of setup screen for the License agreement.

      License agreement

#. Select the destination location for your app.

   Normally you should be able to leave this at the path already suggested by the installer,
   which will be the default directory for app installation for your system and the chosen
   installation mode.
   
   Make sure you have at least 65MB of free disk space on your device.
   
   Click :guilabel:`Browse...` if you wish to change the installation path of the app.  

   .. figure:: figures/user_install_destination_location.png
      :name: user_install_destination_location
      :width: 400
      :alt: Screenshot of setup screen requesting the user to select a destination location

      Select destination location

#. Click :guilabel:`Install` to install the L’ART Research Assistant app on your device. 

   .. figure:: figures/user_install_research_assistant.png
      :name: user_install_research_assistant
      :width: 400
      :alt: Screenshot of application ready for installation.

      Install Research Assistant app

#. Complete setup by clicking :guilabel:`Finish` and enjoy!

   .. figure:: figures/complete_setup_research_assistant.png
      :name: complete_setup_research_assistant
      :width: 400
      :alt: Screenshot of completing the L'ART Research Assistant Setup Wizard

      Complete setup of Research Assistant app


Installing on Linux
-------------------

This currently requires building from source or running as a Python package (requires Python 3.10),
but should run if you have Chrome or Chromium installed.

.. note:: Help wanted!

   We would welcome help for developing a sustainable workflow to build distributables for Linux.
   If you have any experience with packaging for one or more Linux distributions (e.g. as flatpaks,
   \*.debs, snaps, etc.) and would be willing to help with that please do get in touch!



Running as a Python package
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The easiest way is to run the app as a Python package. On Ubuntu 22.04 or newer, follow the steps
below to install the Python package and all its dependencies:

.. code-block:: console

   $ sudo snap install chromium
   $ sudo apt update && sudo apt upgrade -y
   $ sudo apt install pipx -y
   $ pipx install research-assistant
   $ research-assistant

You can now launch the app by simply running the command :code:`research-assistant` from a terminal. If
this doesn't work straight away, you might need to log out and log back in before launching the app
for the first time.

.. The easiest way is to run directly from source. On Ubuntu 22.04, follow the steps below the get
   the source code and all the dependencies installed. The last line will run the Research Assistant.

   .. parsed-literal::

      sudo apt install chromium-browser python3-pip python3-tk -y
      python3.10 -m pip install pipenv
      cd ~/
      wget https\ :/\ |github_refs_tags_url|\ |version|\ .tar.gz
      tar -xf ./v\ |version|\ .tar.gz
      rm ./v\ |version|\ .tar.gz
      cd research-assistant-|version|
      python3.10 -m pipenv install
      python3.10 -m pipenv run python ./manage.py run

.. If you want to make an executable shortcut, create a file with the executable flag (+x) in your
   :file:`~/.local/bin` directory. You can do this by following these steps:

   .. code-block:: console

      $ cd ~/.local/bin
      $ echo > research-assistant
      $ chmod +x research-assistant
      $ gedit research-assistant

   In the editor that pops up, enter the following text and then save the file:

   .. parsed-literal::

      #!/usr/bin/env bash

      python3.10 -m research-assistant

   After saving the above, you can now launch the Research Assistant from the terminal by
   just typing in :code:`research-assistant` and hitting :kbd:`Enter`. (You may need to
   log out and log back in if this doesn't work straight away...)


Building from source
^^^^^^^^^^^^^^^^^^^^

Alternatively, if you want to build the app as a proper binary for your system,
you can follow the steps for :doc:`../developers/setup` from the
:doc:`../developers/index`, and then just run
:code:`python3.10 -m pipenv run python manage.py build` from inside the
project's root directory.

This will produce a tarball (:file:`*.tar.gz`) in the :file:`./dist/linux/`
directory containing the full set of binaries for the application, which can then
be installed in the appropriate way for you system or run directly from the
executable therein.

The only real advantage this might offer is if you want to install the
Research Assistant on several machines, as you can just copy over the tarball,
exctract it and run the app, without needing to worry about any dependencies
(they are all packaged together when the executable is built). There is no
real additional advantage over running as a Python package.



Installing on MacOS
-------------------

This currently requires building from source or running as a Python package (requires Python 3.10),
but should run if you have Chrome or Chromium installed.

.. caution:: App termination issue on MacOS

   There is currently an issue where the app may not terminate correctly on MacOS after the main
   window has been closed. If the background Terminal window remains open after a few seconds, this
   may have to be closed manually and the user may have to confirm that they want to really terminate
   the process.

   This is not harmful beyond the annoyance value, as long as the user does not close the Terminal
   window *before* they have finished the data collection.

   For more information see :github:issue:`37`.


To build from source follow the same instructions as for Linux above, with some adjustments necessary
(such as using :command:`port` instead of :command:`apt`). Since we don't currently have full
instructions that have been tested on MacOS for this, it will be preferable to run as a Python
package unless you want to actively figure out any problems you might encounter during the build.

To run as a Python package, follow these instructions:

#. Install Chrome from the app store (or install Chromium using your preferred method).

#. Install the latest version of Python 3.10x (that is version 3.10.10 as of the time of
   writing not 3.11.x!) from `the official Python releases for MacOS <https://www.python.org/downloads/macos/>`_.

   After runnin the installer, open a Terminal and check that :code:`python3 --version`
   prints something like "Python 3.10.10". This means python has installed correctly and
   you're ready to continue.

#. From the Terminal, install the Research Assistant with the command
   :code:`pip3 install research-assistant`.

   This will download and install the research-assistant and all its dependencies (other than Chrome,
   which you should have installed from the app store already).

.. #. Install :command:`pipenv` with the command :code:`pip3 install pipenv`. This should
      print out a success message at the end of the process. You can ignore any messages it
      might print about updating pip itself (or follow the instructions it provides if you like).

   #. Now run the following commands in your terminal to set up the package from source:

      .. parsed-literal::

         cd ~
         curl -L https\ :/\ |github_refs_tags_url|\ |version|\ .tar.gz -o research-assistant.tar.gz
         tar -xf ./research-assistant.tar.gz
         rm research-assistant.tar.gz
         mv research-assistant-|version| research-assistant
         cd research-assistant
         python3 -m pipenv install

   .. |github_refs_tags_url| replace:: /github.com/lart-bangor/research-assistant/archive/refs/tags/v

#. You can now launch the app from within a Terminal using the following command:
   
   .. code-block:: console

      $ python3 -m research-assistant


Obviously, you may not want to open a Terminal, do :code:`cd ~/research/assistant` and then
type :code:`python3 -m research-assistant` every time. You can create
a shortcut which can be clicked to launch the app by following these additional steps:

#. Make an executable :file:`.command` file on your Desktop directory (:file:`~/Desktop`)
   by running the following in a Terminal:

   .. code-block:: console

      $ cd ~/Desktop/
      $ echo > Research-Assistant.command
      $ chmod +x ./Research-Assistant.command
      $ open -a TextEdit ./Research-Assistant.command

#. In the editor that popped up with the last command above, copy and paste the following
   code, then save and close the file.

   .. code-block:: bash

      #!/bin/bash

      python3 -m research-assistant

#. Once you've created the :file:`Research-Assistant.command` file as per the two steps above,
   you can just locate it on your Desktop or in Finder (e.g. launch Finder, then in the top
   click on :menuselection:`Go -> Home`, and open the :file:`Desktop` folder) and then drag
   and drop the :file:`Research-Assistant.command` onto your dock.

   When you click on the file in the dock or on the Desktop now, it should launch a Terminal
   window together with the app.
