"""Package implementing the Matched Guise Task (MGT)."""


def expose_to_eel():
    """Expose the AGT API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
