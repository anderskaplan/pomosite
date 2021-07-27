import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate, ConfigurationError

content_path = str(Path(Path(__file__).parent, "content/test_templating"))
template_dir_by_lang = [("lang", content_path + "/templates")]
output_dir = "temp/test_validation"


class TestConfigValidation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_dir)
        if p.exists():
            print("removing " + output_dir)
            shutil.rmtree(output_dir)

    def test_should_fail_on_missing_leading_slash(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "x/",
                    "template": "page.html",
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)

    def test_should_not_accept_two_identical_page_endpoints(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
                "P2": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)

    def test_should_not_accept_two_identical_static_endpoints(self):
        site_config = {
            "item_config": {
                "S1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
                "S2": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)

    def test_should_not_accept_two_identical_page_and_static_endpoints(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xyz",
                    "template": "page.html",
                },
                "S1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/page.html"),
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)

    def test_should_not_accept_endpoints_with_invalid_characters(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xyö",
                    "template": "page.html",
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)

    def test_should_not_accept_endpoints_with_space(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xy zz",
                    "template": "page.html",
                },
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, template_dir_by_lang, output_dir)
