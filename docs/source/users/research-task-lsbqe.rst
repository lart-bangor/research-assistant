Research task: LSBQe
====================

In the LSBQe, the task start screen is followed by the three main sections of the LSBQe on Language and Social Background, Language and Dialect Background, and Community Language Use Behaviour respectively. 

For more details on the contents of the LSBQe and how this differs from the standard version of the LSBQ, see Breit et al. (2023) [INSERT LINK].  


Any mandatory fields that haven’t been completed by the participant will be flagged up if the user attempts to continue
to the next page without having fully completed any section of the LSBQe or the response entered in a field is invalid 
(e.g. text entered in a field expecting a date). 

The user is given instructions on how they should complete the missing fields if this happens. 

For researchers using the app, or a specific localisation of the LSBQe for the first time, it might be useful to complete 
the LSBQe and purposely leave all fields blank before trying to submit so they can read through and familiarise themselves
with the user-feedback provided for each field.  

.. figure:: figures/lsbqefigure14.png
      :width: 600
      :alt: Screenshot of unanswered mandatory fields flagged in red.

      Mandatory fields that remain unanswered or contain invalid input will be flagged in red

.. figure "15" will be merged with app presentation


Loading a generic version of the LSBQe
--------------------------------------

An “English – generic” version of the LSBQe is available for you to use if the languages pertinent to your research location are not available amongst our
four LSBQe versions, or if you prefer a generic or customisable version of the LSBQe.

To select the generic version of the LSBQe, choose "English-generic (United Kingdom)" from the LSBQe version drop down list.

.. figure:: figures/lsbqefigure16.png
      :width: 600
      :alt: Screenshot of loading a generic version of the LSBQe.

      Loading a generic version of the LSBQe

This version of the LSBQe will give you English and "Other Language" at every juncture where both languages are named.

.. add figure 'for example' (below)

Customizing a generic version of the LSBQe
------------------------------------------

You may wish to customize a generic version of the LSBQe if you would like the LSBQe to present a specific language pair to use during your study.

In order to customize a version of the LSBQe, open the file :file:`[EngZzz_Eng_GB]` by following the path below:

:guilabel:`C:\Users\username\AppData\Local\Programs\LART\ResearchClient\lart_research_client\lsbq\versions`

.. insert screenshot of folder once available

Firstly, you **must "save as"**, following the ISO standard code sequence (see the note `here <file:///C:/Users/admin/Documents/lart-research-client/docs/build/html/tutorials/localisation-translations.html#id5>`_ for standard code sequence generating) **(see Figure 22)**.

For example, if you wish to customize a version for English and Irish for use in Ireland through the medium of English, you will create a file called
:file:`[EngGle_Eng_IE]` **(see Figure 23)**.  

.. figure:: figures/lsbqefigure17.png
      :width: 600
      :alt: Screenshot of saving generic files as

      Save the generic files as and follow the ISO code sequence

After your new version is saved, you must change the **“versionID”** and **“versionName”**
to reflect your customization. Your **“versionID”** should match your file name.

.. figure:: figures/lsbqefigure18.png
      :width: 600
      :alt: Screenshot of new LSBQe file

      New LSBQe file EngGle_Eng_IR

A further customization that you can make inside the file relates to how your LSBQe version will refer to the language you wish to include. 

To do this, you must search for **"RML”** in your :guilabel:`[EngGle_Eng_IE]` and change **“the other language”** to the language name you wish to be displayed.
In our current example that would be **“Irish”** as shown in Figure 24 below.

.. figure:: figures/lsbqefigure19.png
      :width: 600
      :alt: Screenshot of saving generic files as

      Customizing inside your LSBQe file.

It is not mandatory to include English as one of the languages on your LSBQe version. For example, if you require an LSBQe version to study Ulster Scots and Irish in Northern Ireland, you would call the file :file:`[ScoGle_Eng_GB]`
and apply the relevant changes in Figure 22 and Figure 23.

Additionally, in order to change the default **"English"** in the LSBQe, you would have to search **“MajorityLanguage”** and change each instance of "English" to "Ulster Scots" 
**(see Figure 25)**

.. figure:: figures/lsbqefigure20.png
      :width: 600
      :alt: Screenshot of customizing both languages in your generic LSBQe file 

      Customizing both languages in your generic LSBQe file

.. note::
    Note that the third label in the file name :file:`[ScoGle_Eng_GB]` remains **“Eng”**, as this refers to the language in which the LSBQe is presented, which in this case is still English. 
    
    See `here <file:///C:/Users/admin/Documents/lart-research-client/docs/build/html/tutorials/localisation-translations.html>`_ for details on file naming and ISO codes.


Excludable Questions   
--------------------

The LSBQe allows users to include or exclude certain questions depending on the nature of the language communities to be researched (see Breit et al. 2023 for details on the rationale behind these choices).

Below you’ll find instructions on which questions allow this option and how to go about excluding them. 

"Other" Sex
***********

As default, the LSBQe contains three options that a participant may select as their sex: “Female”; “Male”; “Other”. 

.. figure:: figures/eqfigure21.png
      :width: 400
      :alt: Screenshot of default options for sex on LSBQe

      Default options for sex on LSBQe

However, some researchers may prefer to use a binary choice (e.g., where biological sex is a research variable) and therefore exclude “Other” from the available options. 

To do this, open your LSBQe version file from the following path:

:file:`C:\\Users\\username\\AppData\\Local\\Programs\\LART\\ResearchClient\\lart_research_client\\lsbq\\versions`

With the file open, you will see that below the section “options” the line labelled :file:`“lsb_show_other_sex”`` is set to :file:`true`:

.. figure:: figures/eqfigure22.png
      :width: 400
      :alt: Screenshot of the feature 'lsb_show_other_sex' set to "true"

      The feature "lsb_show_other_sex" set to "true"

To exclude the **“Other”** option in your version of the LSBQe you simply need to set that option to :file:`“false”`.

.. figure:: figures/eqfigure23.png
      :width: 400
      :alt: Screenshot of the feature 'lsb_show_other_sex' set to "false"

      The feature "lsb_show_other_sex" has been changed to "false"

.. note::
      Make sure to restart the app so that the change can take effect.

.. figure:: figures/eqfigure24.png
      :width: 400
      :alt: Screenshot of how the question appears in the app after removing "Other"

      How the question appears in the app after removing "Other"

If you wish to change it back to including **"Other"**, you must reverse the above procedure and change the setting back to :file:`"true"`.

Minimum required languages
**************************

In the “Language and Dialect Background” section, the opening question asks participants to list all the languages and dialects that they speak and give information regarding
where they learned each of them, when they learned them, and if there were significant periods where the participant did not use any of them.

By default, the LSBQe  requires a minimum of two required language names, by presenting participants with two blank lines that must be filled before continuing.

While participants have the option of adding more language varieties via the :guilabel:`Add Line` button (i.e. for participants who are multilingual),
only two lines will appear as default **(see Figure 30 below)**. 

.. figure:: figures/mrlfigure25.png
      :width: 400
      :alt: Screenshot of Language and Dialect Background section

      The opening question on the Language and Dialect Background section set to two minimum required languages

Should you wish to make three or more languages the default without having to add more lines, for instance if you’re researching trilingualism within a community,
you may set the minimum required languages to three.

To do this, firstly, open your LSBQe version file from the following path:

:file:`C:\\Users\\username\\AppData\\Local\\Programs\\LART\\ResearchClient\\lart_research_client\\lsbq\\versions`

With the file open, you will see that below the section :file:`“options”` the line labelled :file:`“ldb_minimum_required_languages”` is set to **“2”**: 

.. figure:: figures/mrlfigure26.png
      :width: 400
      :alt: Screenshot of the feature “ldb_minimum_required_languages” set to “2”.   

      The feature “ldb_minimum_required_languages” set to “2”   

To change this to a different number, e.g., 3, you simply type “3” in place of “2”: 

.. figure:: figures/mrlfigure27.png
      :width: 400
      :alt: Screenshot of changing the minimum required languages

      Changing the minimum required languages to three

.. note:: 
      Make sure to restart the app so that the change can take effect.

.. figure:: figures/mrlfigure28.png
      :width: 400
      :alt: Screenshot of how the question appears in the app with a minimum of three required languages

      How the question appears in the app with a minimum of three required languages
 
If you wish to change the option back to two languages, you must reverse the above procedure and change the setting back to **“2”**.

Reading and Writing:
********************

In the “Language and Dialect Background” section, participants are asked how much time they spend engaged in speaking, listening, reading, and writing in each of their languages.

.. figure:: figures/rawfigure29.png
      :width: 400
      :alt: Screenshot of how the question appears in the app with "Reading" and "Writing" options

      How the question appears in the app with "Reading" and "Writing" options

The “reading” and “writing” parts of the questions can be removed. For example when researching a community whose one or more languages is only/mostly oral
or doesn’t have an accepted orthographic system, making the “reading” and “writing” options irrelevant to participants.  

To remove the “reading” and “writing” options, firstly, open your LSBQe version file from the following path:

:file:`C:\\Users\\username\\AppData\\Local\\Programs\\LART\\ResearchClient\\lart_research_client\\lsbq\\versions`

With the file open, you will see that below the section :file:`“options”` the lines labelled :file:`“ldb_show_reading”` and :file:`“ldb_show_writing”` are set to :file:`“true”``: 

.. figure:: figures/rawfigure30.png
      :width: 400
      :alt: Screenshot of the features “ldb_show_reading” and “ldb_show_writing” set to “true” by default  

      The features “ldb_show_reading” and “ldb_show_writing” are set to “true” by default 

To exclude these options from your version of the LSBQe, simply change the values to :file:`“false”`: 

.. figure:: figures/rawfigure31.png
      :width: 400
      :alt: Screenshot of user setting the "reading" and "writing" options to “false”

      Setting the "reading" and "writing" options to “false”

.. note::
      Make sure to restart the app so that the change can take effect.

If you wish to change it back to including “reading” and “writing”, you must reverse the process and change the values back to :file:`“false”`.

.. figure:: figures/rawfigure32.png
      :width: 400
      :alt: Screenshot of how the question appears in the app with "Reading" and "Writing" options removed

      How the question appears in the app with "Reading" and "Writing" options removed 

Show code-switching
*******************

The LSBQe’s Community Language Use Behaviour section contains a final section on code-switching where participants are asked how often they code-switch in different contexts **(see Figure 38)**. 

.. figure:: figures/csfigure33.png
      :width: 400
      :alt: Screenshot of - CLUB section with code-switching question included

      CLUB section with code-switching question included

The code-switching question can be removed if this information is not required in your study.  

To remove the code-switching question, firstly, open your LSBQe version file from the following path: 

:file:`C:\\Users\\username\\AppData\\Local\\Programs\\LART\\ResearchClient\\lart_research_client\\lsbq\\versions`

With the file open, you will see that below the section :file:`“options”` the line labelled :file:`“club_show_codeswitching”`` is set to :file:`“true”` **(see Figure 39)**

.. figure:: figures/csfigure34.png
      :width: 400
      :alt: Screenshot of the feature “club_show_codeswitching” set to “true” by default

      The feature “club_show_codeswitching” is set to “true” by default

To exclude the code-switching question from your version of the LSBQe, simply change the value to :file:`“false”` **(see Figure 40)**

.. figure:: figures/csfigure35.png
      :width: 400
      :alt: Screenshot of setting the codeswitching option to “false”

      Setting the codeswitching option to “false” 

.. note::
      Make sure to restart the app so that the change can take effect.

After removing the code-switching section, the CLUB section finishes on the question prior to the code-switching question that asks participants to indicate
which language or dialect they generally use for various activities **(see Figure 41)**.  

If you wish to change it back to including the code-switching question, you must reverse the process and change the value back to :file:`“true”`.

.. figure:: figures/csfigure36.png
      :width: 400
      :alt: Screenshot of how the question appears in the app with "Reading" and "Writing" options removed

      How the question appears in the app with "Reading" and "Writing" options removed 

