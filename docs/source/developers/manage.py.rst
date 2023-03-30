The *manage.py* utility
=======================

The project includes its own little script to simplify many common project
management tasks. From inside the project directory, you can run the following commands:

.. code-block:: bash

   python manage.py -h         # show the available commands
   python manage.py run        # runs the app from the source files
   python manage.py debug      # runs the app in debug mode
   python manage.py clean      # cleans up your project directory
   python manage.py build      # builds an executable with PyInstaller
   python manage.py docs       # build the documentation