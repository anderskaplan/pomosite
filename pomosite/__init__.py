"""pomosite: A multi-lingual static site builder based on jinja templates.

More info: https://github.com/anderskaplan/pomosite/blob/main/README.md
"""

from .templating import ConfigurationError, InvalidReferenceError, generate
from .config import create_site_config, add_resources, add_translation
