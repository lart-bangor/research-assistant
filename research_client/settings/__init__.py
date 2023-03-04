"""Package implementing the Settings UI for the LART Research Client."""


def expose_to_eel():
    """Expose the Settings API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
