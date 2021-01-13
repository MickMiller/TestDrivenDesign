"""
File: test_logging.py
Author: Gerard (Mick) Miller
Purpose: Test all logging levels.

All tests pass (only Expected Results) when the only message from test is:
    Wrong number of parameters - Use: find(FILE, DIR)

If any tests fail assert will print relevant info.
"""

import unittest
from mycode.file_tools_class import MyLogs


# noinspection SpellCheckingInspection
class TestLog(unittest.TestCase):
    """ find """

    def setUp(self):
        """ Instantiate class """

    def tearDown(self):
        """ Runs last and cleans up """

    @classmethod
    def test_log(cls):
        """
        log
        """

        my_dir = "C:\\Users\\a00530667\\PycharmProjects\\OBAuto\\venv\\mytest"

        my_debug_obj = MyLogs("file_tools_class_DEBUG.log", "DEBUG", my_dir)
        my_info_obj = MyLogs("file_tools_class_INFO.log", "INFO", my_dir)
        my_warning_obj = MyLogs("file_tools_class_WARNING.log", "WARNING", my_dir)
        my_error_obj = MyLogs("file_tools_class_ERROR.log", "ERROR", my_dir)
        my_critical_obj = MyLogs("file_tools_class_CRITICAL.log", "CRITICAL", my_dir)

        unittest.TestCase.assertIn(
            my_info_obj,
            " This is a debug test.",
            my_debug_obj.get_log_msg(
                "Debug",
            ),
            "debug log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_info_obj,
            "This is an info test.",
            my_info_obj.get_log_msg(
                "Info",
            ),
            "info log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_warning_obj,
            "This is a warning test.",
            my_warning_obj.get_log_msg(
                "Warning",
            ),
            "warning log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_error_obj,
            "This is an error test.",
            my_error_obj.get_log_msg(
                "Error",
            ),
            "error log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_critical_obj,
            "Wrong number of parameters - Use: OBJ.get_log_msg(SEVERITY_LEVEL)",
            my_critical_obj.get_log_msg("my_CRITICAL.log", "OneTooMany"),
            "Critical log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_critical_obj,
            "Wrong number of parameters - Use: OBJ.get_log_msg(SEVERITY_LEVEL)",
            my_critical_obj.get_log_msg(),
            "Critical log entry not As Expected!",
        )

        unittest.TestCase.assertIn(
            my_critical_obj,
            "Error in file_tools_class.get_log_msg: unexpected return value.",
            my_critical_obj.get_log_msg(
                "No matching severity level",
            ),
            "Error in file_tools_class.get_log_msg: unexpected return value.",
        )

        unittest.TestCase.assertIn(
            my_critical_obj,
            "This is a critical test.",
            my_critical_obj.get_log_msg(
                "Critical",
            ),
            "Critical log entry not As Expected!",
        )


if __name__ == "__main__":
    unittest.main()
