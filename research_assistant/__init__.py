"""LART Research Assistant Package __init__ file.

This file doesn't do anything, it merely exists to qualify the
research_assistant package as a valid, importable Python package.
The package can be imported via `import research_assistant`, though
usually in this scenario one would want to import subpackages, such as
the `lsbqe` or `atolc` package, eg. via
`from research_assistant import lsbqe`.
"""
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
