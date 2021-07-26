import unittest
from pathlib import Path
import shutil
from xml.etree import ElementTree
from pomosite.gen import generate
from pomosite.translate import translate_page_templates

base_path = Path(__file__).parent
content_path = Path(base_path, "content/test_multilingual")
output_base_path = "temp/test_multilingual"


class TestMultilingual(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        p = Path(output_base_path)
        if p.exists():
            print("removing " + output_base_path)
            shutil.rmtree(output_base_path)
        pages = {
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
                "source": Path(content_path, "static/lim.jpeg"),
            },
        }
        translate_page_templates(
            str(Path(content_path, "templates")),
            str(Path(base_path, "temp/pseudo.po")),
            str(Path(output_base_path, "templates-ploc")),
        )
        templates_by_lang = [
            ("sv", str(Path(content_path, "templates"))),
            ("en", str(Path(output_base_path, "templates-ploc"))),
        ]
        generate(pages, templates_by_lang, output_base_path)

    def test_should_generate_pages_in_the_default_language(self):
        output_file = str(Path(Path.cwd(), output_base_path, "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_base_path, "om-oss/index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_base_path, "script.php"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_should_generate_pages_in_other_language(self):
        output_file = str(Path(Path.cwd(), output_base_path, "en", "index.html"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(
            Path(Path.cwd(), output_base_path, "om-oss", "en", "index.html")
        )
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

        output_file = str(Path(Path.cwd(), output_base_path, "en", "script.php"))
        self.assertTrue(
            Path(output_file).is_file(), "Expected to find file: " + output_file
        )

    def test_should_have_the_right_content_on_pages_in_the_default_language(self):
        # "right content" means:
        # - html lang attribute is default language
        # - content in the default language
        # - links lead to pages in the default language
        output_file = str(Path(Path.cwd(), output_base_path, "index.html"))
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

        output_file = str(Path(Path.cwd(), output_base_path, "om-oss/index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title").strip(), "Om oss - Mycket lim")
        self.assertEqual(tree.find(".//img").get("src"), "../lim.jpeg")
        self.assertEqual(tree.find(".//a[.='script']").get("href"), "../script.php")

    def test_should_have_the_right_content_on_pages_in_other_language(self):
        # "right content" means:
        # - html lang attribute is other language
        # - content in the other language
        # - links lead to pages in the other language
        output_file = str(Path(Path.cwd(), output_base_path, "en", "index.html"))
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

        output_file = str(
            Path(Path.cwd(), output_base_path, "om-oss", "en", "index.html")
        )
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.findtext(".//title").strip(), "Ǿḿ ǿşş - Ḿẏƈķḗŧ ŀīḿ")
        self.assertEqual(tree.find(".//img").get("src"), "../../lim.jpeg")
        self.assertEqual(
            tree.find(".//a[.='şƈřīƥŧ']").get("href"), "../../en/script.php"
        )

    def test_should_switch_from_defult_language_to_other(self):
        output_file = str(Path(Path.cwd(), output_base_path, "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.find(".//a[.='Svenska']").get("href"), "./")
        self.assertEqual(tree.find(".//a[.='English']").get("href"), "en/")

    def test_should_switch_from_other_language_to_default(self):
        output_file = str(Path(Path.cwd(), output_base_path, "en", "index.html"))
        tree = ElementTree.parse(output_file)
        self.assertEqual(tree.find(".//a[.='Şṽḗƞşķȧ']").get("href"), "../")
        self.assertEqual(tree.find(".//a[.='Ḗƞɠŀīşħ']").get("href"), "./")
