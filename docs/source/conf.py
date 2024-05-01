"""Configuration file for the Sphinx documentation builder."""

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path
from configparser import ConfigParser
from datetime import date
sys.path.insert(0, os.path.abspath('../..'))


# -- Custom setup event connectors -------------------------------------------

def _build_finished_handler(app, exception):
    import subprocess
    rtd_dir = os.getenv("READTHEDOCS_OUTPUT")
    print("Current directory:", os.getcwd())
    ls = subprocess.run(["ls", "-la"], capture_output=True)
    print(ls, "\n")
    print("Build dir for html:", f"{rtd_dir}html")
    ls = subprocess.run(["ls", "-la", f"{os.getenv}html"], capture_output=True)
    print(ls, "\n")
    print("Build dir for pdf:", f"{rtd_dir}pdf")
    ls = subprocess.run(["ls", "-la", f"{os.getenv}pdf"], capture_output=True)
    print(ls, "\n")


def setup(app):
    app.connect('build-finished', _build_finished_handler)


# -- Project information -----------------------------------------------------

project_root_path = Path(__file__).parent.parent.parent

setup_cfg = ConfigParser()
setup_cfg.read(project_root_path / "setup.cfg", encoding='utf-8')

project = " ".join([
        setup_cfg.get("app.options", "author"),
        setup_cfg.get("app.options", "name")
])

copyright = " ".join([
    f"2022-{date.today().year}",
    setup_cfg.get("app.options", "long_author")
])

author = setup_cfg.get("metadata", "author")

# The full version, including alpha/beta/rc tags
release = setup_cfg.get("metadata", "version")
version = release

github_url = setup_cfg.get("metadata", "url")

html_logo = str(project_root_path / "research_assistant" / "web" / "img" / "appicon.png")
html_favicon = str(project_root_path / "research_assistant" / "web" / "img" / "appicon.png")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx_inline_tabs',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx_toolbox',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_toolbox.collapse',
    'sphinx_toolbox.confval',
    'sphinx_toolbox.github',
    'sphinx_toolbox.sidebar_links',
    'sphinx_toolbox.more_autodoc.no_docstring',
    'sphinx_toolbox.more_autodoc.generic_bases',
    'sphinx_toolbox.more_autodoc.genericalias',
    'sphinx_toolbox.more_autodoc.regex',
    # 'sphinx_toolbox.more_autodoc.sourcelink',
    # 'sphinx_toolbox.more_autodoc.typehints',
    'sphinx_toolbox.more_autodoc.typevars',
    'sphinx_toolbox.more_autodoc.variables',
    'sphinx_toolbox.tweaks.param_dash',
    'sphinx_autodoc_typehints',
    'sphinx_js'
]

js_source_path = '../../research_assistant/web/js'
jsdoc_config_path = './jsdoc_conf.json'

github_username = 'lart-bangor'
github_repository = 'research-assistant'

autoapi_dirs = ['../../research_assistant']

autodoc_default_options = {
    'members': True,
    'private-members': True,
    # 'inherited-members': True,
    'undoc-members': True,
    # 'exclude-members': ['with_traceback'],
    'show-inheritance': True,
    'ignore-module-all': True,
}

autodoc_class_signature = 'separated'
autodoc_member_order = 'groupwise'
autodoc_typehints = 'both'
autodoc_typehints_format = 'short'
autodoc_preserve_defaults = True
typehints_defaults = 'comma'
autodoc_show_sourcelink = True
python_use_unqualified_type_names = True

default_role = 'py:obj'

add_module_names = False
modindex_common_prefix = ['research_assistant']

napoleon_google_docstring = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# Numbered figures
numfig = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'body_max_width': 'none',
    'style_external_links': True,
    'prev_next_buttons_location': 'both',
    'style_nav_header_background': '#2980B9',  # Default: #2980B9
}
html_css_files = [
    'style.css',
]
html_context = {
    "display_github": True,
    "github_user": "lart-bangor",
    "github_repo": "research-assistant",
    "github_version": "docs",
    "conf_py_path": "/docs/source/",
}
html_show_sphinx = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
