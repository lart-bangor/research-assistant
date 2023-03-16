"""Package implementing the Audio Guise Task (AGT)."""


def expose_to_eel():
    """Expose the AGT API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
