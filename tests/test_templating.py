import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate, create_site_config, InvalidReferenceError

content_path = str(Path(__file__).parent / "content/test_templating")
output_dir = "temp/test_templating"


class TestTemplating(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_dir)
        if p.exists():
            print("removing " + output_dir)
            shutil.rmtree(output_dir)

    def test_page_templates(self):
        # given a directory with a few page templates
        site_config = create_site_config(content_path + "/templates")
        self.assertEqual(3, len(site_config["item_config"]), "Expected to find three items")
        self.assertEqual(
            True,
            site_config["item_config"]["P1"]["bool-value"],
            "Expected special config variable to be set correctly",
        )

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

    def test_resources(self):
        site_config = {
            "item_config": {
                "S1": {
                    "endpoint": "/xyz",
                    "source": Path(content_path, "templates/p1.html"),
                }
            }
        }

        generate(site_config, output_dir)

        output_file = str(Path(Path(".").resolve(), output_dir, "xyz"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

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
