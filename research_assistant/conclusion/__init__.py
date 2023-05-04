"""Conclusion screen for end of task series.

This module implements a configurable screen for the conclusion of a task
or series of tasks in the Research Assistant app.

The functionality provided does not implement any data models, but simply
provides text in different language versions which can be used to indicate
to a user that they have reached the end of their assigned tasks in the app.

This is nicer than just sending the user straight back to the home screen of
the app, which might not provide sufficient closure to leave the user confident
that everything was successfully concluded.
"""


def expose_to_eel():
    """Expose the Conclusion screen API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
