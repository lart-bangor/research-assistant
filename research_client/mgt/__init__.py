"""Package implementing the Matched Guise Task (MGT)."""


def expose_to_eel():
    """Expose the MGT API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
