Contributing
============

What do I need to know to help?
-------------------------------

If you are looking to helo with a code contribution, our project uses `Python 3.10 <https://python.org>`_ and
`Eel <https://github.com/python-eel/Eel>`_ for the backend,
`JavaScript <https://developer.mozilla.org/en-US/docs/Web/JavaScript>`_ for the frontend logic, and
`HTML <https://developer.mozilla.org/en-US/docs/Web/HTML>`_ & `CSS <https://developer.mozilla.org/en-US/docs/Web/CSS>`_
(specifically, `Bootstrap <https://getbootstrap.com/>`_) for the frontend design (i.e., the user interface). If you
don't feel ready to make a code contribution yet, no problem! You can also checkout
`Documentation issues <https://github.com/lart-bangor/research-client/issues?q=is%3Aissue+is%3Aopen+label%3Adocumentation>`_,
help by :doc:`../tutorials/localisation-translations` adding localised/translated versions for the research tasks
we have already implemented, or thoroughly test the latest release in the app and submit high-quality bug reports to
our `issue tracker <https://github.com/lart-bangor/research-client/issues>`_.

If you are interested in making a code contribution and would like to learn more about the technologies that we use,
check out the list of free resources below.

* `The official Python Tutorial <https://docs.python.org/3/tutorial/>`_ --
  Best if you've done some programming before but not necessarily in Python 3.
* `Sebastiaan Mathôt's Video Tutorials for Python <https://pythontutorials.eu/video/object-oriented-programming/>`_ --
  Good if you're still relatively unsure about programming and especially Object-Oriented Programming.
* `Learn Python 3 The Hard Way <https://learnpythonthehardway.org/python3/preface.html>`_ --
  No need to purchase the book, just open the "Contents" menu on the top left and work through the exercise chapters.
* `The Modern JavaScript Tutorial <https://javascript.info/>`_ --
  Pretty comprehensive introduction to all things JavaScript.
* `Mozilla's JavaScript Guide <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide>`_ --
  Can be worked through quite readily and well-integrated with the relevant API documentation, very good starting point if you've done some programming before but not necessarily (modern) JavaScript.
* `Mozilla's JavaScript API Documentation <https://developer.mozilla.org/en-US/docs/Web/JavaScript>`_ --
  All the API documentation you will need for JavaScript.
* `Mozilla's HTML Guide <https://developer.mozilla.org/en-US/docs/Learn/HTML>`_ --
  Good starting point whether you're new to HTML or just a bit rusty.
* `Mozilla's CSS Guide <https://developer.mozilla.org/en-US/docs/Learn/CSS>`_ --
  Definitely much more than you'll need to know for this.
* `Official Bootstrap Documentation <https://getbootstrap.com/docs/5.0/getting-started/introduction/>`_ --
  As long as you know some HTML and a little bit of CSS, this will cover most of the rest you'll need to know to work on the design of the frontend.


How do I make a contribution?
-----------------------------

Never made an open source contribution before? Wondering how contributions work in our project? Here's a quick
rundown!

#. Find an issue that you are interested in addressing or a featue that you would like to add.

#. Fork our :github:repo:`lart-bangor/research-client` repository.

   This means that you will have a copy of the repository under
   :file:`your-GitHub-username/research-client`.

#. Clone the repository to your local machine using :code:`git clone https://github.com/your-GitHub-username/research-client.git`.

#. Create a new branch for your fix using :code:`git checkout -b branch-name-here`.

   The branch name should ideally follow the schema :code:`active/category/description-of-issue`.
   For example to make improvements to the backend logic for the LSBQ, this could
   be :code:`active/lsbq/improve-backend-logic`. For a new tutorial in the documentation it could
   be :code:`active/docs/basketweaving-tutorial`.

   We generally follow the principle of using the :code:`active` prefix for branches that have
   active development happening (except the three core branches :code:`main`, :code:`dev`, and
   :code:`docs`). Once an issue developed on one of these "active" branches has either been
   merged into one of the core branches or abandoned (e.g. because someone coded themselves
   into a knot) we rename them with the prefix :code:`obsolete` instead of :code:`active`.
   This helps us to keep a good picture of what is happening on the repository.

   If you're not sure about the 'category' or it doesn't neatly fit to one sub-part of the
   project, you can just write :code:`active/general/description-of-issue`.

#. If you need to run the app, make test builds, or build the documentation locally, then
   install the required dependencies with :code:`pipenv install --dev` (run from inside the
   project directory, where the file called :file:`Pipfile` is located).
   
   If you don't need to run the app, make test builds, or build the documentation locally, you can omit this.

#. Make the appropriate changes for the issue you are trying to address or the feature that you want to add.

#. Use :code:`git add insert-paths-of-changed-files-here` to add the file contents of the changed files to the
   "staging area" git uses to manage the state of the project, also known as the index.

#. Use :code:`git commit -m "Insert a short summary message of the changes made here"` to store the contents of the
   changes in your "staging area" together with a descriptive message.

#. Push the changes back to your remote repository (:file:`your-GitHub-username/research-client`) by using
   :code:`git push origin branch-name-here` (using the same branch name you decided on above).

#. Submit a `pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_
   to our upstream repository (:github:repo:`lart-bangor/research-client`).

#. Title the pull request with a short description of the changes made, and if applicable the issue or bug number
   associated with your change.

   For example, you could title a pull request "Added additional check to LSBQ data model to
   resolve issue #1234" or "Add a basketweaving tutorial to the documentation".

#. In the description of the pull request, explain the changes you have made, any issues you think exist with the
   contribution you're submitting, and ask any questions you have for the maintainer(s).

   It's completely OK if your pull request is not perfect (no pull request is!) --- your pull request will be
   reviewed and the reviewer will be able to help you fix any problems it might have and help you improve it
   if needed.

   In case you explicitly do not want to be credited for your contribution for any reason you should also mention
   this in your pull request --- otherwise we will assume by default that you are happy for us to add your name
   and a link to your GitHub profile to the :ref:`contributors_list` in furture versions of the :doc:`../users/index`.

#. Wait for the pull request to be reviewed by a maintainer.

#. Make any changes to the pull request that the reviewing maintainer recommends. They might ask you some questions
   to clarify some aspect of your pull request, and it's totally okay for you to ask questions during this process
   as well.

#. Celebrate your success after your pull request is merged!


For a more detailed guide on getting set up to work on the codebase, including if you need to install the dependencies
(like :command:`git`, :command:`python`, etc.) so that you can test run and build the app locally, see our guide on
:doc:`setup`. 


Where can I go for help?
------------------------

If you need help, you can ask questions on one of our `GitHub Discussions <https://github.com/lart-bangor/research-client/discussions>`_
sections. We'll be happy to help where we can!


Code of Conduct
---------------

We currently have a very simple Code of Conduct:

#. You are responsible for treating everyone on the project with respect
   and courtesy, regardless of who they are or what their attributes are.
#. If you are the victim of any inappropriate behaviour or comments, we
   are here for your and will do the best to ensure that any abusers are
   reprimanded and/or removed, as may be appropriate in the situation.
#. If you are abusive to anyone on the project we reserve the right to
   reprimand you or remove you from the project, as we may judge appropriate
   in the situation.
#. Always remember that this is a community we build together 💪.


.. only:: html

   .. raw:: html

    <p>
      <small>
        <i>Note:</i>
        These contributing guidelines have been adapted from a very neat
        <a hre="https://opensource.com/life/16/3/contributor-guidelines-template-and-tips">template provided by Safia Abdalla</a>.
      </small>
    </p>

.. only:: not html

  *Note:* These contributing guidelines have been adapted from a very neat
  `template provided by Safia Abdalla <https://opensource.com/life/16/3/contributor-guidelines-template-and-tips>`_.
