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


Installing on MacOS
-------------------

This currently requires building from source or running as a Python package (requires Python 3.10),
but should run if you have Chrome or Chromium installed.
