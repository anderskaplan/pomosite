# pomosite: A multi-lingual static site builder based on jinja templates

There are many tools available to build static web sites.
See e.g. https://jamstack.org/generators/

Why yet another one?
- multi-language support with a translation workflow using industry standard PO files
- pages built from templates using the powerful Jinja engine
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

## Site configuration and generation

To use pomosite you need to create a generator script for your web site. This is the script
you run to generate the site, that is, to write all the content of the site to a given directory, so that it can be uploaded to a web server.

the generator script is a configuration file written in python. this gives you plenty of flexibility to extend the system if you like. but you can also keep it short and sweet. you are welcome to use the one in the sample directory (sample/sample-site.py) as a starting point.

the basic workflow of the generator script is as follows:
1. create_site_config()
2. add_resources(), once for each resource directory
3. add_language(), once for each translated language
4. generate()

the first step creates a python dictionary called site_config. steps 2 and 3 add to this data container, and in step 4 it is used as the specification when generating the file tree for the site.

## Templates

templates let you create similar web pages without copy-and-pasting between them. when you make an edit, you only need to do it in one place.
they also let you refer from one web page to another, or from web pages to images and other resources, without hard-coding urls. hard-coded urls are notoriously brittle especially for a multi-language site.

there can be templates for web pages on various formats (html, php, markdown, etc). there can also be templates for different categories of pages, or templates for fragments of pages such as a menu for navigation.

Pomosite uses the Jinja templating engine, so please refer to the [Jinja documentation](https://jinja.palletsprojects.com/templates/) for a description of the template syntax.

### Referencing pages and translations
To reference a page or resource from a template, pass its unique ID to the `url_for()` function like so:

  `<a href="{{ url_for('PAGE1') }}">link to page 1</a>`

Language tags will be applied automatically for URLs to templated pages.

To reference a particular language version of the current page, pass the language tag to the `url_for_language()` function like so:

  `<a href="{{url_for_language('en')}}">English</a>`

A common use case is a menu where the user gets to select language.

### Page-config headers
All template files for the site should be placed in one directory.
`create_site_config()` scans all the files in the template directory for page-config headers and adds the ones with valid headers to the site configuration. a page-config header is always the first line of the file and is on the format:

  `{# key1: value1, key2: value2, ... #}`

for example:

  `{# id: "START", endpoint: "/" #}`

there are two mandatory key/value pairs for a page:
- `id` is a unique ID for the page and can be used to reference the page from other pages.
- `endpoint` is the path part of the URL where the page will be published. it must start with a slash.

## Resources

resources are content files like images and style sheets which do not need template processing. to add resources to your site, put them in a directory (with subdirectories as needed) and call `add_resources()`. they will be copied to the site file tree when the site is generated.

Note that you need to be careful with what you put in the resource directory, so that you don't publish e.g. your git repository by mistake. "Hidden" files where the name starts with a full stop are deliberately included in the copying operation, as we may want to include files like ".htaccess".

resource files of common media types (.jpg, .css, etc) are added to the site configuration with their file name as ID. this means that you can refer to them from your templates like so:

  `<img src="{{url_for('my-image.jpg')}}">`

note that this means that you must give all resource files of common media types unique names.

## Translations
TODO

one template directory per language. temp dir

workflow
PO files
currently only html templates

language tags https://en.wikipedia.org/wiki/IETF_language_tag

url scheme: / => /lang/


# For developers: Modifying/Extending pomosite

## Set up the development environment

install python 3.x
it is recommended to use a python virtual environment. on Windows, use "python -m venv python-venv" followed by "python-venv\Scripts\activate.bat".
pip install -r requirements.txt

## Run the unit tests

run pytest

## Run code checks

black .
pydocstyle

## Install for local use

pip install -e .

## Package for deployment

pip install --upgrade build
python -m build
