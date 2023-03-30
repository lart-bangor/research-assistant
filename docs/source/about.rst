About the Research Client
=========================

Introduction
------------

The L’ART Research Client is a freely available open-source app to aid researchers in the collection, 
storage and transfer of data for research in bilingualism and language attitudes, with a particular focus
on bilingual populations who speak a majority language and a regional / minority / minoritized language. 
The app aims to make research in bilingualism easier, more comparable and reproduceable. 
For a detailed discussion of the specific methodological choices, see Breit et al., 2023.


What the L'ART Reserch Client can do
------------------------------------

The current version (L'ART Research Client |version|) implements four tools (for a detailed discussion of
methodological adaptations, please see Breit et al., 2023).

* **Participant consent**: A digital informed consent process, including participant information sheets & consent forms.

* **LSBQe**: A digital adaptation of the **Language and Social Background Questionnaire**, or LSBQ [Anderson-Mak-EtAl-2018]_,
  which we term the LSBQe (“e” for electronic).

* **AToL**: A digital implementation of the **Attitudes towards Languages Questionnaire** or AToL [Schoel-Roessel-EtAl-2013]_. 

* **MGT** and **VGT**: A digital tool for measuring language attitudes via the speaker evaluation paradigm.
  This tool enables users to run several evaluations of audio guises such as the **Matched Guise Technique**
  [Lambert-Hodsgon-EtAl-1960]_ and the **Verbal Guise test** (e.g., [Markel-EtAl-1967]_). Due to its
  flexibility as either MGT or VGT, we named this tool **‘Audio Guise Test’**, or **AGT** for short.

 
The main functionality of the L’ART Research Client resides in its format as a stand-alone app 
that can run on a large variety of desktop and laptop computers without the need for internet connectivity. 
This makes it highly usable both in lab environments and in the field, for example when collecting data 
in remote areas with inconsistent internet access. 


The L'ART Research Client has been
designed in such a way that it can be easily extended by researchers (or research groups)
with just a basic knowledge of Python, JavaScript and HTML needed to implement additional tasks
(see the :doc:`developers/index` for more info). Translating an existing task for a new language or
language pair is even easier and can be done by just editing a simple
`JSON <https://en.wikipedia.org/wiki/JSON>`_ file in a text editor (see :doc:`tutorials/translating-tasks`).


Reasons to use the Research Client
----------------------------------

* **Less work for the researcher:** With research tasks pre-implemented, preparation for a new study only
  involves translation/localisation of the interface where a suitable one is not yet available for the target
  population. There is also no need to manage forms and manually enter data after collecting responses. 

* **Enhanced consistency and comparability within and across studies:** The translation/localisation of
  tasks is the only thing that varies within tasks. The presentation, data types and validation, coding,
  and output format stay constant across different use instances, whether as part of the same study or
  across different studies and research teams. 

* **Improved transparency and reproducibility:** Because the entire source code for the L’ART Research
  Client is publicly available and version-controlled, it’s easy to reference the specific version and
  task that was used, which allows other researchers to easily view and reconstruct the tasks exactly as
  they were administered at the time the research was carried out. 

For detailed examples and more concrete illustrations of these advantages, see Breit et al., 2023. 

Citing the Research Client
--------------------------

.. epigraph::

Breit, F., Tamburelli, M., Gruffydd, I. and Brasca, L. (2022). *The L’ART Research Client app: A digital toolkit for bilingualism and language attitude research* [Software, version |version|]. Bangor University. 


Licensing
---------

The L’ART Research Client and all the tools implemented within it are free and open source. The app is
dual licensed under the terms of the `Affero General Public License <https://www.gnu.org/licenses/agpl-3.0.en.html>`_
(the AGPL) and the `European Union Public License <https://commission.europa.eu/content/european-union-public-licence_en>`_
(the EUPL). Dual licensing means that you are free to choose under which of the two license’s
terms you want to use it. 

Both licenses allow you to:

- Use the app and its functionality freely (as in freedom) and for free (as in free beer) in your
  work, whether commercial or non-commercial. 
- Modify or otherwise make adaptations to the app and its source code, as long as you yourself make
  those changes available to others under the same license terms (or the terms of another compatible
  license where this is expressly permitted by the AGPL or EUPL). 
- Allow you to add yourself to the credits/copyright notice when you modify the software, as long as
  you do not remove, materially change, or misrepresent in any way the copyright and author attribution
  notes as they appear in the app, its source code, documentation, distributions (e.g. installers), etc.
  This means that: 
- Naturally, if you intend on modifying and/or improving the Research Client, we would appreciate it
  if you would share those developments with us so we can incorporate any improvements and enhancements
  into the official version of the app. 
- Where possible we would also strongly encourage you to retain the dual licensing model, as we
  believe this ensures maximal adoptability and reusability across a large variety of potential
  users in different parts of the world.

.. _contributors_list:

Contributors
------------

The L'ART Research Client core developers are :github:user:`Florian Breit <thatfloflo>` (Lead) and :github:user:`Marco Tamburelli <dakrismeno>`.

We would like to thank the following for contributing (in alphabetical order):

* :github:user:`Chloe Cheung <cwyc8>` (Documentation)
* Lissander Brasca (Translation, Documentation)
* :github:user:`Ianto Gruffydd <iantogruff>` (User testing, Translation, Documentation)
* Athanasia Papastergiou (Translation)


Acknowledgements
----------------

The L'ART Research Client was developed by the `Language Attitudes Research Team <https://bangor.ac.uk/lart>`_ (:github:org:`GitHub <lart-bangor>`)
in the `School of Arts, Culture and Language <https://bangor.ac.uk/arts-culture-language>`_
at `Bangor University <https://bangor.ac.uk>`_.
Development of the app was supported by the `Economic and Social Research Council <https://ukri.org/councils/esrc/>`_ [grant number `ES/V016377/1 <https://gtr.ukri.org/projects?ref=ES%2FV016377%2F1>`_].

.. TODO: Add logos for BU and ESRC


