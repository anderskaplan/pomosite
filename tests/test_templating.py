import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate, add_page_templates_dir, InvalidReferenceError

content_path = str(Path(__file__).parent / "content/test_templating")
output_base_path = "temp/test_templating"


class TestTemplating(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_base_path)
        if p.exists():
            print("removing " + output_base_path)
            shutil.rmtree(output_base_path)

    def test_page_templates(self):
        # given a directory with a few page templates
        item_config = {}
        add_page_templates_dir(content_path + "/templates", item_config)
        self.assertEqual(3, len(item_config), "Expected to find three items")
        self.assertEqual(
            True,
            item_config["P1"]["bool-value"],
            "Expected special config variable to be set correctly",
        )
        template_dir_by_lang = [("lang", content_path + "/templates")]

        # when generating the site
        generate(item_config, template_dir_by_lang, output_base_path)

        # then the expected output files appear where they are supposed to
        output_file = str(Path(".").resolve() / output_base_path / "index.html")
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title"), "P1")
        self.assertEqual(tree.findtext(".//div[@class='header']"), "page name is P1")

        output_file = str(Path(".").resolve() / output_base_path / "subpage/index.html")
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(
            Path(".").resolve() / output_base_path / "subpage/sub-no-trailing-slash"
        )
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_resources(self):
        item_config = {
            "S1": {
                "endpoint": "/xyz",
                "source": Path(content_path, "templates/p1.html"),
            }
        }

        generate(item_config, [], output_base_path)

        output_file = str(Path(Path(".").resolve(), output_base_path, "xyz"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_invalid_resource_id(self):
        # given a page template with a url_for() call to a non-existent item
        item_config = {
            "P1": {
                "endpoint": "/xyz",
                "template": "invalid-ref.html",
            }
        }

        # when generating the site
        # then the appropriate exception is raised
        with self.assertRaises(InvalidReferenceError):
            template_dir_by_lang = [("lang", content_path + "/templates")]
            generate(item_config, template_dir_by_lang, output_base_path)
