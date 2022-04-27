"""Package implementing the Language and Social Background Questionnaire (RML)."""


def expose_to_eel():
    """Expose the LSBQ-RML API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
