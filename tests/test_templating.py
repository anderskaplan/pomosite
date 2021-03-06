import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import (
    generate,
    create_site_config,
    add_resources,
    InvalidReferenceError,
    ConfigurationError,
)

content_path = str(Path(__file__).parent / "data/test_templating")
output_dir = "temp/test_templating"


class TestTemplating(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_dir)
        if p.exists():
            print("removing " + output_dir)
            shutil.rmtree(output_dir)

    def test_create_site_config(self):
        site_config = create_site_config(content_path + "/templates", "temp")
        self.assertEqual(
            3, len(site_config["item_config"]), "Expected to find three items"
        )
        self.assertEqual(
            True,
            site_config["item_config"]["P1"]["bool_value"],
            "Expected special config variable to be set correctly",
        )

    def test_generate_templates(self):
        # given a directory with page templates
        site_config = create_site_config(content_path + "/templates", "temp")

        # when generating the site
        generate(site_config, output_dir)

        # then the expected output files appear where they are supposed to
        output_file = str(Path(".").resolve() / output_dir / "index.html")
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title"), "P1")
        self.assertEqual(tree.findtext(".//div[@class='header']"), "page name is P1")

        output_file = str(Path(".").resolve() / output_dir / "subpage/index.html")
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(
            Path(".").resolve() / output_dir / "subpage/sub-no-trailing-slash"
        )
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_access_config_variables_from_template(self):
        site_config = create_site_config(content_path + "/templates", "temp")
        generate(site_config, output_dir)
        output_file = str(Path(".").resolve() / output_dir / "index.html")
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//blockquote"), "True")

    def test_generate_resources(self):
        site_config = {
            "item_config": {
                "S1": {
                    "endpoint": "/xyz",
                    "source": str(Path(content_path, "templates/p1.html")),
                }
            }
        }

        generate(site_config, output_dir)

        output_file = str(Path(Path(".").resolve(), output_dir, "xyz"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_add_resources(self):
        site_config = {"item_config": {}}
        add_resources(str(Path(content_path) / "resources"), site_config)

        item_config = site_config["item_config"]
        self.assertEqual(3, len(item_config))
        self.assertTrue("lim.jpeg" in item_config)
        self.assertTrue("a.css" in item_config)
        self.assertFalse("b.php" in item_config)

    def test_invalid_resource_id(self):
        # given a page template with a url_for() call to a non-existent item
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xyz",
                    "template": "invalid-ref.html",
                }
            },
            "template_dir": content_path + "/templates",
        }

        # when generating the site
        # then the appropriate exception is raised
        with self.assertRaises(InvalidReferenceError):
            generate(site_config, output_dir)

    def test_items_cannot_be_both_templates_and_static_resources(self):
        site_config = {
            "item_config": {
                "P1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/p1.html"),
                    "template": "p1.html",
                }
            },
            "template_dir": content_path + "/templates",
        }
        with self.assertRaises(ConfigurationError):
            generate(site_config, output_dir)
