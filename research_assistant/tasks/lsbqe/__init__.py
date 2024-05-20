"""Package implementing the Language and Social Background Questionnaire."""


def expose_to_eel():
    """Expose the LSBQe API to Python Eel."""
    from . import eel  # type: ignore # noqa: F401
