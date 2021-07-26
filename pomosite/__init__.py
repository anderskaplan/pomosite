"""pomosite: A multi-lingual static site builder based on jinja templates.

More info: https://github.com/anderskaplan/pomosite/blob/main/README.md
"""

from .gen import ConfigurationError, InvalidResourceIdError, make_relative_url, generate
from .itemconfig import add_page_templates_dir, add_resources_dir
from .translate import translate_page_templates
