Settings: configuring the app
=============================

The app’s settings can be accessed via the app side menu. There are numerous aspects of the app that 
can be changed on the settings page. The various options are discussed in some detail below. 

Remember to click :guilabel:`Save changes` and restart the app in order for the changes you make to take effect. 

.. figure:: figures/figure40.png
      :width: 400
      :alt: Screenshot of completing the L'ART Research Client menu

      Figure 9 - Open the sidebar to enter settings

Shutdown delay
--------------

Shutdown delay is the amount of time the app’s backend process (basically, what you can see in the terminal window)
waits before closing after you close the main app window.

Under normal circumstances there should be no need to adjust this. However, it can be beneficial to increase the shutdown
delay when using an underpowered device e.g., a 4GB Surface Tab Go or some other device not meeting the recommended system requirements
(see `System Requirements <file:///C:/Users/admin/Documents/lart-research-client/docs/build/html/users/system-requirements.html>`_ for more information). 

Problems with limited system resources can lead to the app freezing or becoming unresponsive.
Increasing the shutdown delay means that the app will wait longer in case the system temporarily delays the processing of expected signals and information. 

.. figure:: figures/figure41.png
      :width: 400
      :alt: Screenshot of shutdown delay section in general app settings

      Figure 10 - Editing shutdown delay

Logging settings
----------------

Logging settings involves the app’s debug and error logging functionality. While you will not usually have to access these files,
they can contain useful information for researchers developing an extension for the app, those creating a new localisation of a task,
or generally for diagnostic information if an unexpected error occurs. 

You may be asked for information from the log files if you report a bug, which will help us to reconstruct what happened when the error
occurred on your computer. 

.. warning::

      The log files may potentially contain any of the information that a user/researcher/participant enters into the app while it is running. 
                
      For this reason, **you must apply the same information security policies to the log files as you do to the response data itself.** 

      If you share log files with a third party, you should ensure that they do not contain identifiable data which you would not otherwise
      share with that party. 
                
      You may want to "sanitise" your log files *(by manually removing any sensitive/identifiable data)* before sharing
      them and/or make sure that the other party is aware and capable of keeping this data secure in line with your policies.

The maximum number of log files to keep determines how many logs from previous runs of the app are kept, and once this number is reached old logs are deleted.
By default, the app keeps logs files for the last 10 times it was started. 

The log level determines how detailed the log files are. The lower the numeric level, the more detail is stored in the log files. 

Lowering the log level might be useful if you try to diagnose an error or bug and it is not apparent what led to the undesired behaviour from the existing logs
(however, we recommend **not** doing this "just in case", as the amount of information might be overwhelming with log levels below 30).

The log message format is only relevant for advanced users and developers who may want to format logs in a specific way for working with their
preferred analysis tools. If you are not sure what this is or how it works, there is no need for you to modify it. 

For details on the formatting see the documentation of the :py:mod:`logging` package in the Python standard library.

.. figure:: figures/figure23.png
      :width: 400
      :alt: Screenshot of Logging settings

      Figure 11 - Logging settings

Task sequencing
---------------

The task sequencing settings allows you to configure which tasks (if any) should follow the completion of a specific task.

Task sequencing facilitates a more convenient data collection process for the researcher by allowing one task to follow another.

This negates the need to re-enter participant details at the start of each task. 

.. See section XX in (Breit et al. 2023).   

For example, with the default settings, when the informed consent task is completed the participant will be automatically advanced to the LSBQe,
and when the LSBQe is complete they will be sent back to the app home screen (see Figure 24)

.. figure:: figures/ts43.png
      :width: 400
      :alt: Screenshot of default sequencing

      Figure 12 -  Default sequencing: Consent Form > LSBQe > App Start Screen

You could decide to use any possible sequence consisting of available tasks.

For example, you may not want to require an electronic consent form for your study, thus removing the consent form from the sequence, and may want
the LSBQe to advance into the AGT as is typical in linguistic studies where a background questionnaire precedes the main research method (see Figure 13). 

.. figure:: figures/tsfigure44.png
      :width: 400
      :alt: Screenshot of task sequencing screen

      Figure 13 - LSBQe > MGT > App Start Screen sequencing 

Should you require every available task to be sequenced, you may also do so (see Figure 14)

.. figure:: figures/ts45.png
      :width: 400
      :alt: Screenshot of task sequencing screen

      Figure 14 -  Consent Form > LSBQe > AToL > Memory Game > AGT > App Start Screen sequencing

If you set a new task sequence, it will show up in gold, with a reset option in red. To make a new sequence your default, press the green default button and save changes (see Figure 15).

.. figure:: figures/ts46.png
      :width: 400
      :alt: Screenshot of task sequencing screen

      Figure 15 - Creating new sequencing



