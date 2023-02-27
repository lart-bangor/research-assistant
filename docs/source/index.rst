Welcome to the L’ART Research Client documentation!
==============================================

The L’ART Research Client is a freely available open-source app that aims to make life easier for
researchers working on bilingualism, sociolinguistics, language attitudes, and
regional/minority/minoritized languages.

The app was developed to ease the collection, storage and transfer of data from commonly employed
tasks such as the collection of informed consent and linguistic background questionnaires, while
at the same time increasing standardisation, comparability and reproducibility of the administered
tasks.

At present the Research Client (version |version|) implements an informed consent facility and two
variants of the Language and Social Background Questionnaire (one very close to the standard LSBQ,
the other adapted for use with potentially unwritten regional- and/or minority languages).
However, we're actively working on adding further tasks to the Research Client and it has been
designed in such a way that it can be easily extended by researchers (or research groups)
with just a basic knowledge of Python, JavaScript and HTML needed to implement additional tasks
(see the :doc:`developers/index` for more info). Translating an existing task for a new language or
language pair is even easier and can be done by just editing a simple
`JSON <https://en.wikipedia.org/wiki/JSON>`_ file in a text editor (see :doc:`tutorials/translating-tasks`).


Citing
------
If you use the L’ART Research Client (or parts of it) in your research, please use the following
citation to reference the app:

   Breit, F., Tamburelli, M., Gruffydd, I. and Brasca, L. (2022). *The L’ART Research Client app: An electronic tool for bilingual research.* Bangor University.

License
-------
The L’ART Research Client and its implementation of the LSBQe are free and open source. The app is
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


.. toctree::
   :maxdepth: 2
   :caption: Contents

   about
   users/index
   tutorials/index
   developers/index
   api
   references




Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
