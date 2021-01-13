"""
File: test_logging.py
Author: Gerard (Mick) Miller
Purpose: Unix tools rewritten in Python

All tests pass (only Expected Results) even if error condition, eg:
if wrong number of parameters Expected Results are:

    Wrong number of parameters - Use: find(FILE, DIR)

If any tests fail assert will print relevant info.

Docstrings use:
    import file_tools_class

    print(file_tools_class.__doc__)
    print(file_tools_class.FindTools.__doc__)
    print(file_tools_class.FindTools.find.__doc__)

"""

import unittest

import os

from mycode.file_tools_class import FindTools


# noinspection SpellCheckingInspection
class TestFindTools(unittest.TestCase):
    """ find """

    def setUp(self):
        """ Instantiate class """

    def tearDown(self):
        """ Runs last and cleans up """

    @classmethod
    def test_find(cls):
        """
        Test for Unix-like find command.
        See file README_Unix.txt and README_FIND.txt
        """

        my_obj = FindTools("pattern", "DIR")

        os.chdir("C:\\Users\\a00530667\\PycharmProjects\\OBAuto\\venv\\TestTools\\Find")

        unittest.TestCase.assertIn(
            my_obj,
            "C:\\Users\\a00530667\\PycharmProjects\\OBAuto\\venv\\TestTools\\Find",
            os.getcwd(),
            "Not in correct dir.",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "Wrong number of parameters - Use: find(FILE, DIR)",
            my_obj.find("aB_InFind.txt"),
            "Error message didn't find 'File does not exist'",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "Wrong number of parameters - Use: find(FILE, DIR)",
            my_obj.find("aB_InFind.txt", "OK parameter", "Too many parameters"),
            "Error message didn't find 'File does not exist'",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "File does not exist",
            my_obj.find("File does not exist", "."),
            "Error message didn't find 'File does not exist'",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "aB_InFind.txt",
            my_obj.find("aB_InFind.txt", "."),
            "Error message didn't find 'File does not exist'",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_InDirsub.txt",
            my_obj.find("file_InDirsub.txt", "."),
            "Error message didn't find 'File does not exist'",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_ ThisFileHasSpace.txt",
            my_obj.find("file_ ThisFileHasSpace.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_0123456789-.txt",
            my_obj.find("file_0123456789-.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_abcdefghijklmnopqrstuvwxyz.txt",
            my_obj.find("file_abcdefghijklmnopqrstuvwxyz.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_ABCDEFGHIJKLMNOPQRSTUVWXYZ_2.txt",
            my_obj.find("file_ABCDEFGHIJKLMNOPQRSTUVWXYZ_2.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_ABCDEFGHIJKLMNOPQRSTUVWXYZ_2.txt",
            my_obj.find("file_ABCDEFGHIJKLMNOPQRSTUVWXYZ??.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_ABCDEFGHIJKLMNOPQRSTUVWXYZ_2.txt",
            my_obj.find("file_A*BCDEFGHIJKLMNOPQRSTUVWXYZ??.txt", "."),
            "Error message didn't find FILE",
        )

        unittest.TestCase.assertIn(
            my_obj,
            "file_ABCDEFGHIJKLMNOPQRSTUVWXYZ_2.txt",
            my_obj.find("file_A*Z*", "."),
            "Error message didn't find FILE",
        )


if __name__ == "__main__":
    unittest.main()
