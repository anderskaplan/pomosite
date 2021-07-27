import unittest
from pomosite.templating import make_relative_url


class TestMakeRelativeUrl(unittest.TestCase):
    def test_should_map_self(self):
        self.assertEqual(make_relative_url("/", "/"), "./")
        self.assertEqual(make_relative_url("/x", "/x"), "x")
        self.assertEqual(make_relative_url("/x/", "/x/"), "./")
        self.assertEqual(make_relative_url("/x/y", "/x/y"), "y")
        self.assertEqual(make_relative_url("/x/y/", "/x/y/"), "./")

    def test_should_map_parent_to_child(self):
        self.assertEqual(make_relative_url("/", "/x"), "x")
        self.assertEqual(make_relative_url("/", "/x/"), "x/")
        self.assertEqual(make_relative_url("/", "/x/y"), "x/y")
        self.assertEqual(make_relative_url("/", "/x/y/"), "x/y/")

    def test_should_map_child_to_parent(self):
        self.assertEqual(make_relative_url("/x", "/"), "./")
        self.assertEqual(make_relative_url("/x/", "/"), "../")
        self.assertEqual(make_relative_url("/x/y", "/"), "../")
        self.assertEqual(make_relative_url("/x/y/", "/"), "../../")
        self.assertEqual(make_relative_url("/x/y/", "/x/"), "../")

    def test_should_map_child_to_sibling(self):
        self.assertEqual(make_relative_url("/x/y", "/x/z"), "z")
        self.assertEqual(make_relative_url("/x/y/", "/x/z/"), "../z/")
