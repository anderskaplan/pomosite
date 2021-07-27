"""pomosite: A multi-lingual static site builder based on jinja templates.

More info: https://github.com/anderskaplan/pomosite/blob/main/README.md
"""

from .gen import ConfigurationError, InvalidReferenceError, make_relative_url, generate
from .itemconfig import create_site_config, add_resources_dir, add_translation
from .translate import translate_page_templates
