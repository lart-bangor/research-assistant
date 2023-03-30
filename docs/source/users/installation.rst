Installation
============

.. //double check before adding 1.1.1, 1.1.1.1, etc

Installing on Windows 10/11
---------------------------

#. Download the official Windows installer for the L'ART Research Client on Windows.

   You can find the latest release (as well as earlier versions) at
   `github.com/lart-bangor/research-client/releases <https://github.com/lart-bangor/research-client/releases>`_.

#. Once downloaded to your device, open the *Downloads* dialogue in the browser and click :guilabel:`Open file`.
   Alternatively, navigate to your :file:`Downloads` folder in File Explorer and double click on the installer file.

   .. figure:: figures/figure1.png
      :name: users_install_open_from_downloads
      :width: 400
      :alt: Screenshot of Windows download dialogue showing the downloaded installer file.

      Open file from downloads

   This text now links to :numref:`users_install_open_from_downloads`, which is straight above. (CHLOE: DELETE THIS LINE)

   .. note::

      If you have Microsoft Defender active, you may be warned about running an unrecognised app.
      
      This is expected behaviour for unsigned software downloaded from the internet. It is meant to get you to
      check that you've downnloaded the Software from a reputable source before running it.
      
      *This is fine if you've used our official download link above!*
      
      Click :guilabel:`Run anyway` to continue with the installation.

      .. figure:: figures/figure2.png
         :width: 400
         :alt: An image of protection message from Windows taken from Microsoft Defender Smartscreen.

         Figure 2 - Microsoft Defender SmartScreen

#. Select you preferred install mode.

   We recommend choosing :guilabel:`Install for me only` for most use cases, which
   will install the app only for the current user.
   
   *However*, you may wish to install the app for all users. For example, if you're installing on a
   shared university or lab computer and want to centrally manage the installation for all users
   (requires administrator privileges).

   If in any doubt, choose :guilabel:`Install for me only`.

   .. figure:: figures/figure3.png
      :width: 400
      :alt: Screenshot of selecting an install mode for users

      Figure 3 - Install mode setup

#. Click :guilabel:`Yes` to allow L'ART Research Client to make changes to your device
   (namely, to install the app).

   .. figure:: figures/figure4.png
      :width: 400
      :alt: Screenshot of User Account Control Screen.

      Figure 4 - User account control screen

#. Read and accept the licence agreement.

   You must accept the agreement before installation can begin.

   .. figure:: figures/figure5.png
      :width: 400
      :alt: Screenshot of setup screen for the License agreement.

      Figure 5 - License agreement

#. Select the destination location for your app.

   Normally you should be able to leave this at the path already suggested by the installer,
   which will be the default directory for app installation for your system and the chosen
   installation mode.
   
   Make sure you have at least 65MB of free disk space on your device.
   
   Click :guilabel:`Browse...` if you wish to change the installation path of the app.  

   .. figure:: figures/figure6.png
      :width: 400
      :alt: Screenshot of setup screen requesting the user to select a destination location

      Figure 6 - Select destination location

#. Click :guilabel:`Install` to install the L’ART Research Client app on your device. 

   .. figure:: figures/figure7.png
      :width: 400
      :alt: Screenshot of application ready for installation.

      Figure 7 - Install Research Client app

#. Complete setup by clicking :guilabel:`Finish` and enjoy!

   .. figure:: figures/figure8.png
      :width: 400
      :alt: Screenshot of completing the L'ART Research Client Setup Wizard

      Figure 8 - Complete setup of Research Client app


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

The easiest way is to run directly from source. On Ubuntu 22.04, follow the steps below the get
the source code and all the dependencies installed. The last line will run the Research Client.

.. parsed-literal::

   $ sudo apt install chromium-browser
   $ pip install pipenv
   $ cd ~/
   $ wget https\ :/\ |github_refs_tags_url|\ |version|\ .tar.gz
   $ tar -xf ./v\ |version|\ .tar.gz
   $ rm ./v\ |version|\ .tar.gz
   $ cd research-client-|version|
   $ python3.10 -m pipenv install
   $ python3.10 -m pipenv run python ./manage.py run

.. |github_refs_tags_url| replace:: /github.com/lart-bangor/research-client/archive/refs/tags/v

If you want to make an executable shortcut, create a file with the executable flag (+x) in your
:file:`~/.local/bin` directory. You can do this by following these steps:

.. code-block:: console

   $ cd ~/.local/bin
   $ echo > research-client
   $ chmod +x research-client
   $ gedit research-client

In the editor that pops up, enter the following text and then save the file:

.. parsed-literal::

   #!/usr/bin/env bash

   cd ~/research-client-|version|
   python3.10 -m pipenv run python manage.py


After savin the above, you can now launch the Research Client from the terminal by
just typing in :code:`research-client` and hitting :kbd:`Enter`. (You may need to
log out and log back in if this doesn't work straight away...)


Building from source
^^^^^^^^^^^^^^^^^^^^

Alternatively, if you want to build the app properly for your system, you can
follow the steps for :doc:`../developers/setup` from the :doc:`../developers/index`,
and then just run :code:`python3.10 -m pipenv run python manage.py build` from
inside the project's root directory.

This will produce a tarball (:file:`*.tar.gz`) in the :file:`./dist/linux/`
directory containing the full set of binaries for the application, which can then
be installed in the appropriate way for you system or run directly from the
executable therein.

The only real advantage this might offer is if you want to install the
Research Client on several machines, as you can just copy over the tarball,
exctract it and run the app, without needing to worry about any dependencies
(they are all packaged together when the executable is built). There is no
real additional advantage over running as a Python package.



Installing on MacOS
-------------------

This currently requires building from source or running as a Python package (requires Python 3.10),
but should run if you have Chrome or Chromium installed. You should be able to largely
follow the steps for Linux above, though you will need to adjust the commands to install
dependencies, as :command:`apt` is of course not available on MacOS.
