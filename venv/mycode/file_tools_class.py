"""
File: file_tools_class.py
Author: Gerard (Mick) Miller
Purpose: MyLogs - Create log files for all log severity levels and example of
Stack Trace.
 - FindTools has Unix-line find command.

Class: MyLogs
Methods:
    delete_file
    basic_config
    get_log_msg

Class: FindTools
Methods:
    find

File and Directory rules: (This info should be somewhere.  Since there are no high-level
    descriptive files this info here.
  ~ A Unix-like kernel is normally neutral about any byte value but
    \000 (ASCII: NUL) and \057 (ASCII: slash).  echo $'\057' OR echo $'\57'
  ~ Tests for: a-z, A-Z, 0-9, underscore (_), dash (-), period (.) and SPACE ( ).
    All but SPACE are user friendly in *NIX environment.  SPACE included for Windows.
  ~ Same rules for directory names.
"""

import sys
import unittest
import os
import fnmatch
import logging
import errno
import traceback


class MyLogs(unittest.TestCase):
    """ Methods to set log levels """

    def __init__(self, file_name, severity_level, my_dir):
        """ Initialize """
        super().__init__()  # call constructor to init parent class
        os.chdir = my_dir
        self.delete_file(file_name)
        self.basic_config(file_name, severity_level)

    @staticmethod
    def delete_file(file_name):
        """ Deletes file, if file doesn't exist no error """
        try:
            os.remove(file_name)
        except OSError as file_err:
            if file_err.errno != errno.ENOENT:  # no such file or directory
                raise  # re-raise exception if a different error occurred

    @staticmethod
    def basic_config(file_name, severity_level):
        """ config log file """

        log_level = severity_level
        log_format = (
            "%(asctime)s "
            + "%(filename)s "
            + "%(process)d-%(levelname)s - "
            + "%(message)s"
        )

        logging.basicConfig(
            filename=file_name,
            filemode="a",
            level=log_level,
            format=log_format,
        )

    @staticmethod
    def get_log_msg(*args):
        """ Returns log info from parameter """

        if len(args) != 1:
            result = "Wrong number of parameters - Use: OBJ.get_log_msg(SEVERITY_LEVEL)"
            logging.critical(" Critical: wrong number of parameters!")
            return result

        result = " Error in file_tools_class.get_log_msg: unexpected return value."

        if args[0] == "Critical":
            logging.critical(" This is a critical log entry.")
            result = " This is a critical test."
            # To give traceback & sys.exc content
            try:
                os.open("ThisFileDoesNotExist", 0)
            except FileNotFoundError:
                print("Traceback: ----------------\n", traceback.format_exc())
                logging.critical(traceback.format_exc())
                print("sys.exc: -----------------\n", sys.exc_info()[2])
                logging.critical(sys.exc_info()[2])
        elif args[0] == "Error":
            logging.error(" This is severity Error in log.")
            result = " This is an error test."
        elif args[0] == "Warning":
            logging.warning(" This is severity Warning in log.")
            result = " This is a warning test."
        elif args[0] == "Info":
            logging.info(" This is severity Info in log.")
            result = " This is an info test."
        elif args[0] == "Debug":
            logging.debug(" This is severity Debug in log.")
            result = " This is a debug test."

        if result == " Error in file_tools_class.get_log_msg: unexpected return value.":
            logging.critical(
                " Error in file_tools_class.get_log_msg: unexpected return value."
            )
        return result


class FindTools(unittest.TestCase):
    """ *NIX tools """

    def __init__(self, arg_0, arg_1):  # call constructor
        """ Initialize """
        super().__init__()  # call constructor to init parent class
        self.arg_0 = arg_0
        self.arg_1 = arg_1

    def find(self, *args):
        """
        Parameters:
            DIR to search in
            FILE to search for

        Returns:
            $PATH/FILE or error msg
        """

        if len(args) != 2:
            result = "Wrong number of parameters - Use: find(FILE, DIR)"
            return result
        self.arg_0 = args[0]
        self.arg_1 = args[1]
        os.chdir(self.arg_1)
        result = "File does not exist"
        for root, dirs, files in os.walk(self.arg_1):  # pylint: disable=unused-variable
            for name in files:
                if fnmatch.fnmatch(name, self.arg_0):
                    result = name
        return result
