# pomosite: A multi-lingual static site builder based on jinja templates

There are many tools available to build static web sites.
See e.g. https://jamstack.org/generators/

Why yet another one?
- multi-language support with a translation workflow using industry standard PO files
- pages built from templates using the powerful jinja engine
- built for sites with different types of content, not only blog posts.


# Using pomosite

## Overview
Pomosite is a static web site generator. "Static web site" means that all the content
on the web site is represented by files in a directory. Some files are generated from
page templates, optionally with translation, while others (like image files) are just
copied from their source locations. The resulting file tree can then be uploaded to a
web server and made available to the Internet.

This is different from non-static web site frameworks like WordPress or Django. There,
the content is stored in a database, and the web pages are generated on-the-fly on the
web server when a request comes in.

While "static web site" might sound limiting, this is in fact not the case. Pomosite
is not limited to plain HTML; its templating engine works with whatever you feed it
with, as long as it it text based. For example, PHP code to be run on the web server, or
javascript code to be run in the web browser.

A web site created with pomosite consists of the following:
- a *templates* directory for the page templates (in the default language)
- a *resources* directory for style sheets, images, etc
- a *translations* directory for translation files
- a *generator script* written in python. This script provides some site-specific
  configuration information. It also responsible for loading and calling on the
  pomosite module.

Since all of this is plain file-based content, it is highly recommended to store it in
a version control tool such as git.

A sample web site can be found in the sample directory.

## Item config and site generation

config header syntax

item_config format
items: key unique id. value { endpoint, template or source, optionally other values too }
can be auto-populated using create_site_config() and add_resources_dir()

## Templates

TODO
template syntax
referencing content with url_for() and url_for_language()

one template directory per language.
use translate_page_templates() to generate them from the default language.

## Resources
TODO

whack them in a directory tree
how to reference them
unique names

## Translations
TODO

workflow
PO files
currently only html templates


# For developers: Modifying/Extending pomosite

## Set up the development environment

installera python 3.x
- sätt upp python virtual environment, "python -m venv python-venv" och "python-venv\Scripts\activate.bat"
pip install -r requirements.txt

## Run the unit tests

tests\translate-templates.bat
pytest

## Run code checks

black .
pydocstyle

## Install for local use

pip install -e .

## Package for deployment

pip install --upgrade build
python -m build
