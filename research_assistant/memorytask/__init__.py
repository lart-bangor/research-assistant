"""Package implementing the Memory Task for the L'ART Research Assistant."""


def expose_to_eel():
    """Expose the Memory Task API to Python Eel."""
    from . import eel                                                    # type: ignore # noqa: F401
