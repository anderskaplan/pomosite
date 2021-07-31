import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite import generate

content_path = str(Path(Path(__file__).parent, "data/test_templating"))
output_dir = "temp/test_url_for"


class TestUrlFor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_dir)
        if p.exists():
            print("removing " + output_dir)
            shutil.rmtree(output_dir)

    def get_hrefs(self, path):
        self.assertTrue(Path(path).exists(), "Expected to find file: " + path)
        tree = ElementTree.parse(path)
        return [element.get("href") for element in tree.findall(".//a")]

    def get_first_a_href(self, path):
        hrefs = self.get_hrefs(path)
        self.assertTrue(len(hrefs) > 0, 'Expected to find element "a"')
        return hrefs[0]

    def test_should_reference_pages(self):
        site_config = {
            "item_config": {
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
            },
            "template_dir": content_path + "/templates",
        }

        generate(site_config, output_dir)

        output_file = str(Path(Path(".").resolve(), output_dir, "index.html"))
        self.assertEqual(self.get_first_a_href(output_file), "./", "link from P1 to P1")

        output_file = str(Path(Path(".").resolve(), output_dir, "subpage/index.html"))
        self.assertEqual(
            self.get_first_a_href(output_file), "../", "link from P2 to P1"
        )

        output_file = str(
            Path(Path(".").resolve(), output_dir, "subpage/sub-no-trailing-slash")
        )
        self.assertEqual(
            self.get_first_a_href(output_file), "../", "link from P3 to P1"
        )

        output_file = str(
            Path(Path(".").resolve(), output_dir, "subpage/subsub/index.html")
        )
        self.assertEqual(
            self.get_first_a_href(output_file), "../../", "link from P4 to P1"
        )

        output_file = str(Path(Path(".").resolve(), output_dir, "a/page/somewhere"))
        hrefs = self.get_hrefs(output_file)
        item_config = site_config["item_config"]
        self.assertEqual(hrefs[0], item_config["P1"]["endpoint"])
        self.assertEqual(hrefs[1], item_config["P2"]["endpoint"])
        self.assertEqual(hrefs[2], item_config["P3"]["endpoint"])
        self.assertEqual(hrefs[3], item_config["P4"]["endpoint"])
