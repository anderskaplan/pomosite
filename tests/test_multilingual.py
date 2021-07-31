import os
import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree

from pomosite import generate, add_translation
from pomosite.translation import extract_translation_units, generate_dummy_translation

base_path = Path(__file__).parent
content_path = Path(base_path, "data/test_multilingual")
output_dir = "temp/test_multilingual"


class TestMultilingual(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.clear_output_dir()
        self.generate_dummy_translation()
        self.generate_site()

    @classmethod
    def clear_output_dir(self):
        p = Path(output_dir)
        if p.exists():
            print("removing " + output_dir)
            shutil.rmtree(output_dir)

    @classmethod
    def generate_dummy_translation(self):
        os.makedirs(str(base_path / "temp"), exist_ok=True)
        pot_file_path = str(base_path / "temp/test_multilingual.pot")
        extract_translation_units(str(content_path / "templates"), pot_file_path)
        po_file_path = str(base_path / "temp/dummy.po")
        generate_dummy_translation(pot_file_path, po_file_path)

    @classmethod
    def generate_site(self):
        site_config = {
            "item_config": {
                "START": {
                    "endpoint": "/",
                    "template": "start.html",
                },
                "OM-OSS": {
                    "endpoint": "/om-oss/",
                    "template": "om-oss.html",
                },
                "SCRIPT": {
                    "endpoint": "/script.php",
                    "template": "script.php",
                },
                "lim.jpeg": {
                    "endpoint": "/lim.jpeg",
                    "source": Path(content_path, "resources/lim.jpeg"),
                },
            },
            "template_dir": str(content_path / "templates"),
        }
        add_translation(
            "en",
            str(base_path / "temp/dummy.po"),
            str(base_path / "temp/translated-templates"),
            site_config,
        )
        generate(site_config, output_dir)

    def test_should_generate_pages_in_the_default_language(self):
        output_file = str(Path(Path.cwd(), output_dir, "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_dir, "om-oss/index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_dir, "script.php"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_should_generate_pages_in_other_language(self):
        output_file = str(Path(Path.cwd(), output_dir, "en", "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_dir, "om-oss", "en", "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_dir, "en", "script.php"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_should_have_the_right_content_on_pages_in_the_default_language(self):
        # "right content" means:
        # - html lang attribute is default language
        # - content in the default language
        # - links lead to pages in the default language
        output_file = str(Path(Path.cwd(), output_dir, "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.getroot().get("lang"), "sv")
        self.assertEqual(tree.findtext(".//title").strip(), "Mycket lim")
        self.assertEqual(tree.find(".//img").get("alt"), "Mycket lim-logga")
        self.assertEqual(tree.find(".//img").get("src"), "lim.jpeg")
        self.assertEqual(
            tree.findtext(".//a[@href='om-oss/#avsnitt']"),
            "Om oss/ett särskilt avsnitt",
        )
        self.assertEqual(tree.find(".//a[.='script']").get("href"), "script.php")

        output_file = str(Path(Path.cwd(), output_dir, "om-oss/index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title").strip(), "Om oss - Mycket lim")
        self.assertEqual(tree.find(".//img").get("src"), "../lim.jpeg")
        self.assertEqual(tree.find(".//a[.='script']").get("href"), "../script.php")

    def test_should_have_the_right_content_on_pages_in_other_language(self):
        # "right content" means:
        # - html lang attribute is other language
        # - content in the other language
        # - links lead to pages in the other language
        output_file = str(Path(Path.cwd(), output_dir, "en", "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.getroot().get("lang"), "şṽ")
        self.assertEqual(tree.findtext(".//title").strip(), "Ḿẏƈķḗŧ ŀīḿ")
        self.assertEqual(tree.find(".//img").get("alt"), "Ḿẏƈķḗŧ ŀīḿ-ŀǿɠɠȧ")
        self.assertEqual(tree.find(".//img").get("src"), "../lim.jpeg")
        self.assertEqual(
            tree.findtext(".//a[@href='../om-oss/en/#avsnitt']"),
            "Ǿḿ ǿşş/ett şäřşķīŀŧ ȧṽşƞīŧŧ",
        )
        self.assertEqual(tree.find(".//a[.='şƈřīƥŧ']").get("href"), "script.php")

        output_file = str(Path(Path.cwd(), output_dir, "om-oss", "en", "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title").strip(), "Ǿḿ ǿşş - Ḿẏƈķḗŧ ŀīḿ")
        self.assertEqual(tree.find(".//img").get("src"), "../../lim.jpeg")
        self.assertEqual(
            tree.find(".//a[.='şƈřīƥŧ']").get("href"), "../../en/script.php"
        )

    def test_should_switch_from_defult_language_to_other(self):
        output_file = str(Path(Path.cwd(), output_dir, "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.find(".//a[.='Svenska']").get("href"), "./")
        self.assertEqual(tree.find(".//a[.='English']").get("href"), "en/")

    def test_should_switch_from_other_language_to_default(self):
        output_file = str(Path(Path.cwd(), output_dir, "en", "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.find(".//a[.='Şṽḗƞşķȧ']").get("href"), "../")
        self.assertEqual(tree.find(".//a[.='Ḗƞɠŀīşħ']").get("href"), "./")
