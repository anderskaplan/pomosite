"""pomosite: A multi-lingual static site builder based on jinja templates.

More info: https://github.com/anderskaplan/pomosite/blob/main/README.md
"""

from .gen import ConfigurationError, InvalidResourceIdError, make_relative_url, generate, add_dynamic_content_templates, add_static_content
from .translate import translate_page_templates
