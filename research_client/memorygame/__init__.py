"""Package implementing the Memory Game for the LART Research Client."""


def expose_to_eel():
    """Expose the Memory Game API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
