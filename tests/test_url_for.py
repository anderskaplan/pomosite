import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate

content_path = str(Path(Path(__file__).parent, "content/test_templating"))
template_dir_by_lang = [("lang", content_path + "/templates")]
output_base_path = "temp/test_url_for"


class TestUrlFor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_base_path)
        if p.exists():
            print("removing " + output_base_path)
            shutil.rmtree(output_base_path)

    def get_hrefs(self, path):
        self.assertTrue(Path(path).exists(), "Expected to find file: " + path)
        tree = ElementTree.parse(path)
        return [element.get("href") for element in tree.findall(".//a")]

    def get_first_a_href(self, path):
        hrefs = self.get_hrefs(path)
        self.assertTrue(len(hrefs) > 0, 'Expected to find element "a"')
        return hrefs[0]

    def test_should_reference_pages(self):
        item_config = {
            "P1": {
                "endpoint": "/",
                "template": "p1.html",
            },
            "P2": {
                "endpoint": "/subpage/",
                "template": "p1.html",
            },
            "P3": {
                "endpoint": "/subpage/sub-no-trailing-slash",
                "template": "p1.html",
            },
            "P4": {
                "endpoint": "/subpage/subsub/",
                "template": "p1.html",
            },
            "404-PAGE": {
                "endpoint": "/a/page/somewhere",
                "template": "special-page.html",
                "rooted-urls": True,
            },
        }

        generate(item_config, template_dir_by_lang, output_base_path)

        output_file = str(Path(Path(".").resolve(), output_base_path, "index.html"))
        self.assertEqual(self.get_first_a_href(output_file), "./", "link from P1 to P1")

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "subpage/index.html")
        )
        self.assertEqual(
            self.get_first_a_href(output_file), "../", "link from P2 to P1"
        )

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "subpage/sub-no-trailing-slash")
        )
        self.assertEqual(
            self.get_first_a_href(output_file), "../", "link from P3 to P1"
        )

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "subpage/subsub/index.html")
        )
        self.assertEqual(
            self.get_first_a_href(output_file), "../../", "link from P4 to P1"
        )

        output_file = str(
            Path(Path(".").resolve(), output_base_path, "a/page/somewhere")
        )
        hrefs = self.get_hrefs(output_file)
        self.assertEqual(hrefs[0], item_config["P1"]["endpoint"])
        self.assertEqual(hrefs[1], item_config["P2"]["endpoint"])
        self.assertEqual(hrefs[2], item_config["P3"]["endpoint"])
        self.assertEqual(hrefs[3], item_config["P4"]["endpoint"])
