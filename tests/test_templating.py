import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite.gen import generate, add_dynamic_content_templates

content_path = str(Path(Path(__file__).parent, "content/test_templating"))
output_base_path = "temp/test_templating"


class TestTemplating(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_base_path)
        if p.exists():
            print("removing " + output_base_path)
            shutil.rmtree(output_base_path)

    def test_should_generate_basic_pages(self):
        pages = {}
        add_dynamic_content_templates(content_path + "/templates", pages)
        self.assertEqual(3, len(pages), "Expected to find three pages")
        self.assertEqual(
            True,
            pages["P1"]["bool-value"],
            "Expected special config variable to be set correctly",
        )
        templates_by_lang = [("lang", content_path + "/templates")]

        generate(pages, templates_by_lang, output_base_path)

        output_file = str(Path(Path(".").resolve(), output_base_path, "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title"), "P1")
        self.assertEqual(tree.findtext(".//div[@class='header']"), "page name is P1")

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "subpage/index.html")
        )
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "subpage/sub-no-trailing-slash")
        )
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_should_copy_static_files(self):
        statics = {
            "S1": {
                "endpoint": "/xyz",
                "source": Path(content_path, "templates/p1.html"),
            }
        }

        generate(statics, [], output_base_path)

        output_file = str(Path(Path(".").resolve(), output_base_path, "xyz"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )
