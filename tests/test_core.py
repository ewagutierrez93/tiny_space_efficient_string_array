"""Tests for tiny_space_efficient_string_array."""

import unittest

from tiny_space_efficient_string_array import SpaceEfficientStringArray


class TestConstruction(unittest.TestCase):
    def test_empty(self):
        a = SpaceEfficientStringArray([])
        self.assertEqual(len(a), 0)
        self.assertEqual(list(a), [])

    def test_single_empty_string(self):
        a = SpaceEfficientStringArray([""])
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], "")
        self.assertEqual(list(a), [""])

    def test_simple_strings(self):
        a = SpaceEfficientStringArray(["alpha", "beta", "gamma"])
        self.assertEqual(len(a), 3)
        self.assertEqual(a[0], "alpha")
        self.assertEqual(a[1], "beta")
        self.assertEqual(a[2], "gamma")

    def test_tuple_accepted(self):
        a = SpaceEfficientStringArray(("x", "y"))
        self.assertEqual(list(a), ["x", "y"])

    def test_rejects_non_list(self):
        with self.assertRaises(TypeError):
            SpaceEfficientStringArray("abc")

    def test_rejects_non_str_element(self):
        with self.assertRaises(TypeError):
            SpaceEfficientStringArray(["ok", 42])

    def test_rejects_bytes_element(self):
        # bytes are explicitly not str; the check should catch them.
        with self.assertRaises(TypeError):
            SpaceEfficientStringArray([b"bytes"])


class TestIndexing(unittest.TestCase):
    def test_positive_index(self):
        a = SpaceEfficientStringArray(["one", "two", "three"])
        self.assertEqual(a[0], "one")
        self.assertEqual(a[1], "two")
        self.assertEqual(a[2], "three")

    def test_negative_index(self):
        a = SpaceEfficientStringArray(["one", "two", "three"])
        self.assertEqual(a[-1], "three")
        self.assertEqual(a[-2], "two")
        self.assertEqual(a[-3], "one")

    def test_duplicate_strings(self):
        a = SpaceEfficientStringArray(["x", "x", "x"])
        self.assertEqual(len(a), 3)
        for i in range(3):
            self.assertEqual(a[i], "x")

    def test_index_out_of_range_positive(self):
        a = SpaceEfficientStringArray(["only"])
        with self.assertRaises(IndexError):
            _ = a[1]

    def test_index_out_of_range_negative(self):
        a = SpaceEfficientStringArray(["only"])
        with self.assertRaises(IndexError):
            _ = a[-2]

    def test_long_first_element(self):
        a = SpaceEfficientStringArray(["verylongstring", "b"])
        self.assertEqual(a[0], "verylongstring")
        self.assertEqual(a[1], "b")


class TestIteration(unittest.TestCase):
    def test_iter_all(self):
        a = SpaceEfficientStringArray(["p", "q", "r"])
        self.assertEqual(list(a), ["p", "q", "r"])

    def test_iter_empty(self):
        a = SpaceEfficientStringArray([])
        self.assertEqual(list(a), [])

    def test_iter_with_empty_strings_interleaved(self):
        a = SpaceEfficientStringArray(["", "a", "", "b", ""])
        self.assertEqual(list(a), ["", "a", "", "b", ""])


class TestContains(unittest.TestCase):
    def test_present(self):
        a = SpaceEfficientStringArray(["cat", "dog"])
        self.assertIn("cat", a)
        self.assertIn("dog", a)

    def test_absent(self):
        a = SpaceEfficientStringArray(["cat", "dog"])
        self.assertNotIn("fish", a)

    def test_non_str_not_in(self):
        a = SpaceEfficientStringArray(["cat"])
        self.assertNotIn(42, a)


class TestEquality(unittest.TestCase):
    def test_equal(self):
        a = SpaceEfficientStringArray(["a", "b"])
        b = SpaceEfficientStringArray(["a", "b"])
        self.assertEqual(a, b)

    def test_not_equal_content(self):
        a = SpaceEfficientStringArray(["a", "b"])
        b = SpaceEfficientStringArray(["a", "c"])
        self.assertNotEqual(a, b)

    def test_not_equal_length(self):
        a = SpaceEfficientStringArray(["a", "b"])
        b = SpaceEffifiedStringArray(["a"]) if False else SpaceEfficientStringArray(["a"])
        self.assertNotEqual(a, b)

    def test_not_equal_to_plain_list(self):
        a = SpaceEfficientStringArray(["a", "b"])
        self.assertNotEqual(a, ["a", "b"])


class TestRepr(unittest.TestCase):
    def test_repr_format(self):
        a = SpaceEfficientStringArray(["ab", "cd"])
        r = repr(a)
        self.assertIn("2 elements", r)
        self.assertIn("4 chars", r)


class TestEmptyStringElements(unittest.TestCase):
    def test_all_empty(self):
        a = SpaceEfficientStringArray(["", "", ""])
        self.assertEqual(len(a), 3)
        self.assertEqual(list(a), ["", "", ""])

    def test_leading_empty(self):
        a = SpaceEfficientStringArray(["", "x"])
        self.assertEqual(a[0], "")
        self.assertEqual(a[1], "x")

    def test_trailing_empty(self):
        a = SpaceEfficientStringArray(["x", ""])
        self.assertEqual(a[0], "x")
        self.assertEqual(a[1], "")


if __name__ == "__main__":
    unittest.main()
