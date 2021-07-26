import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate, ConfigurationError

content_path = str(Path(Path(__file__).parent, "content/test_templating"))
templates_by_lang = [("lang", content_path + "/templates")]
output_base_path = "temp/test_validation"


class TestConfigValidation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_base_path)
        if p.exists():
            print("removing " + output_base_path)
            shutil.rmtree(output_base_path)

    def test_should_fail_on_missing_leading_slash(self):
        with self.assertRaises(ConfigurationError):
            items = {
                "P1": {
                    "endpoint": "x/",
                    "template": "page.html",
                },
            }

            generate(items, templates_by_lang, output_base_path)

    def test_should_not_accept_two_identical_page_endpoints(self):
        with self.assertRaises(ConfigurationError):
            items = {
                "P1": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
                "P2": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
            }

            generate(items, templates_by_lang, output_base_path)

    def test_should_not_accept_two_identical_static_endpoints(self):
        with self.assertRaises(ConfigurationError):
            statics = {
                "S1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
                "S2": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
            }

            generate(statics, templates_by_lang, output_base_path)

    def test_should_not_accept_two_identical_page_and_static_endpoints(self):
        with self.assertRaises(ConfigurationError):
            items = {
                "P1": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
                "S1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
            }

            generate(items, templates_by_lang, output_base_path)

    def test_should_not_accept_endpoints_with_invalid_characters(self):
        with self.assertRaises(ConfigurationError):
            items = {
                "P1": {
                    "endpoint": "/xyö",
                    "template": "page.html",
                },
            }

            generate(items, templates_by_lang, output_base_path)

    def test_should_not_accept_endpoints_with_space(self):
        with self.assertRaises(ConfigurationError):
            items = {
                "P1": {
                    "endpoint": "/xy zz",
                    "template": "page.html",
                },
            }

            generate(items, templates_by_lang, output_base_path)
