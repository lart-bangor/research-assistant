"""LART Research Client Package __init__ file.

This file doesn't do anything, it merely exists to qualify the
lart_research_client package as a valid, importable Python package.
The package can be imported via `import lart_research_client`, though
usually in this scenario one would want to import subpackages, such as
the `lsbqrml` or `atolc` package, eg. via
`from lart_research_client import lsbqrml`.
"""
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
