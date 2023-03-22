"""
File: test_rdt_rs232.py
Author: Gerard (Mick) Miller
Purpose: On-Board cryopump module automated tests over RS232 link.
Use: In Pycharm window "Edit Run/Sanity Configuration" run "RDT_Tool RS232" OR
     In Bash window:
        IC: cd PROJECT so Test/test_rdt_rs232.py and Src/rdt_rs232_class.py
        Invoke: Scripts/python Test/test_rdt_rs232.py
        Results: See Results/
"""

import sys
import os
import re
import tkinter as tk
import unittest
from tkinter import messagebox
from typing import TextIO
import threading
from copy import deepcopy
import Src.rdt_rs232_class


RS232_DIR_orig = os.getcwd()
RS232_DIR = os.getcwd() + "/Config"


class MyException(unittest.TestCase, Exception):
    """Needed for MyException if user enters invalid filename"""


# pylint: disable=too-many-public-methods disable=too-many-instance-attributes
class TestRDT(unittest.TestCase):
    """
    Runs commands in Src/rdt_tool.ini
    """

    def setUp(self):
        """Define buttons"""
        self.button_intro_flg = False
        self.button_start_flg = False
        self.button_pause_flg = False
        self.button_stop_flg = False
        self.button_exit_flg = False

    def tearDown(self):
        """Runs last and cleans up"""

    def ini_file_read(self):
        """Read init.ini file from disk to list ini_list"""

        file_ini = RS232_DIR_orig + "/Src/rdt_tool.ini"
        with open(file_ini, "r", encoding="utf-8") as i_ptr:
            ini_list = list(i_ptr.read().splitlines())

        init_list = self.init_read(ini_list)  # File prefixes, log file size, baud, ...
        preconfig_list = self.preconfig_read(ini_list)  # Preconfigure commands
        command_list = self.command_read(ini_list)  # Test commands
        port_list = self.port_read(ini_list)  # COM ports
        header_list_1 = self.header_read(ini_list, "HEADER1")
        rs232_list = self.rs232_read(ini_list, "RS232")  # Baud rate, Data bits, ...

        ini_file_list = (
            init_list,
            preconfig_list,
            command_list,
            port_list,
            header_list_1,
            rs232_list,
        )

        return ini_file_list

    def log_size_max_ae(self, log_size_max):
        """If log_size_max not As Expected exit"""

        if not re.match(r"[0-9]", log_size_max):
            print(
                "log_size_max read from file: " + log_size_max,
                "init.ini log_size_max not as expected",
            )
            sys.exit()

    def baud_ae(self, baud):
        """If baud not As Expected exit"""

        baud = int(baud)
        if baud not in (2400, 9600, 19200, 28400):
            print(
                "baud read from file: " + str(baud),
                "baud not (2400 or 9600 or 19200 or 38400)",
            )
            sys.exit()

    def run_loop_or_time_ae(self, run_loop_or_time):
        """If run_or_loop_time not As expected abort"""

        if run_loop_or_time not in ("loop", "time"):
            print(
                "run_loop_or_time read from disk: " + run_loop_or_time,
                "init.ini run_loop_or_time",
            )
            sys.exit()

    def stop_test_time_ae(self, stop_test_time):
        """If stp_test_time not As Expected exit"""

        stop_test_time_str = str(stop_test_time)
        str_len = len(stop_test_time_str)
        # If only integers in time only_int = True
        non_int = re.search(r"\D", stop_test_time_str)
        if str_len != 6:
            print(
                "stop_test_time read from disk: "
                + stop_test_time_str
                + " length is not 6"
            )
            sys.exit()

        if non_int:
            print(
                "stop_test_time read from disk: "
                + stop_test_time_str
                + "value is not integer"
            )
            sys.exit()

    def loops_through_commands_calc(self, loops_through_commands_ini):
        """Interpret loops_through_commands_ini"""

        match = re.search(r"\D", loops_through_commands_ini)  # Any letters in field
        if match:
            loops_through_commands = -1
        elif loops_through_commands_ini == 0:
            loops_through_commands = -1
        else:
            loops_through_commands = int(loops_through_commands_ini)

        return loops_through_commands

    def init_read(self, ini_list):
        """From input_list extract INIT parameters"""

        line_to_read = 1  # Start at 1 since 0 is INIT
        log_prefix = self.remove_comment(ini_list[line_to_read])
        err_prefix = self.remove_comment(ini_list[line_to_read + 1])
        log_size_max = self.remove_comment(ini_list[line_to_read + 2])
        self.log_size_max_ae(log_size_max)  # If log_size_max not As Expected abort

        baud = self.remove_comment(ini_list[line_to_read + 3])
        self.baud_ae(baud)

        run_loop_or_time = self.remove_comment(ini_list[line_to_read + 4])
        self.run_loop_or_time_ae(run_loop_or_time)

        stop_test_time = self.remove_comment(ini_list[line_to_read + 5])
        self.stop_test_time_ae(stop_test_time)

        loops_through_commands_ini = self.remove_comment(ini_list[line_to_read + 6])
        loops_through_commands = self.loops_through_commands_calc(
            loops_through_commands_ini
        )

        line_to_read = 7

        init_list = [
            log_prefix,
            err_prefix,
            log_size_max,
            baud,
            run_loop_or_time,
            stop_test_time,
            loops_through_commands,
        ]

        return init_list

    def command_read(self, ini_list):
        """From input_list extract COMMAND parameters"""

        i = 0
        while not re.match("COMMAND", ini_list[i]):
            i += 1

        i += 1
        command_list = []

        while not re.match("PORT", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                line_w_comment = ini_list[i]
                command_list_candidate = self.remove_comment(line_w_comment)
                if command_list_candidate == "":
                    pass
                else:
                    command_list.append(self.remove_comment(line_w_comment))
                i += 1

        return command_list

    def preconfig_read(self, ini_list):
        """From input_list extract PRECONFIG_COMMAND parameters"""

        i = 0
        while not re.match("PRECONFIG_COMMAND", ini_list[i]):
            i += 1

        i += 1
        preconfig_list = []

        while not re.match("COMMAND", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                line_w_comment = ini_list[i]
                preconfig_list_candidate = self.remove_comment(line_w_comment)
                if preconfig_list_candidate == "":
                    pass
                else:
                    preconfig_list.append(self.remove_comment(line_w_comment))
                i += 1

        return preconfig_list

    def port_read(self, ini_list):
        """From input_list extract PORT parameters"""
        i = 0
        while not re.match("PORT", ini_list[i]):
            i += 1

        i += 1
        port_list = []

        while not re.match("HEADER", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                line_w_comment = ini_list[i]
                port_list.append(self.remove_comment(line_w_comment))
                i += 1

        return port_list

    def header_read(self, ini_list, header_str):
        """From input_list extract HEADER parameters"""

        i = 0
        while not re.match(header_str, ini_list[i]):
            i += 1

        i += 1
        header_list = []

        while not re.match("RS232", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                line_w_comment = ini_list[i]
                header_list.append(self.remove_comment(line_w_comment))
                i += 1

        return header_list

    def rs232_read(self, ini_list, rs232_str):
        """From input_list extract RS232 parameters"""

        i = 0
        while not re.match(rs232_str, ini_list[i]):
            i += 1

        i += 1
        rs232_list = []

        while not re.match("PORT_LOG", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                line_w_comment = ini_list[i]
                rs232_list.append(self.remove_comment(line_w_comment))
                i += 1

        return rs232_list

    def port_log_read(self, ini_list, port_log_end):
        """From input_list extract PORT_LOG either True of False
        True means create .err and .log files based on port
        False means create 2 files: .err and .log"""

        port_log_flg = "unset"
        i = 0
        while not re.match(port_log_end, ini_list[i]):
            i += 1

        i += 1

        while not re.match("END_OF_LIST", ini_list[i]):
            if re.fullmatch("", ini_list[i]):
                i += 1
            else:
                port_log_flg = ini_list[i]

        return port_log_flg

    def init_gui(self):
        """Setup GUI"""

        # pylint: disable = attribute-defined-outside-init
        self.intro_msg = """
        Reliability Demonstration Testing (RDT) tool.\n
        Sends RS-232 & EtherCAT messages to 1 or more controllers with 2 or more pumps\n
        Initialization files:
            init.ini with:
              - communication init eg Baud rate, ...\n
            commands.ini with:
              - commands to run eg PowerResetAck.cmd"""

        # Create window
        win = tk.Tk()  # Root window object
        #
        width = 400  # width for the Tk root
        height = 210  # height for the Tk root
        # get screen width and height
        width_of_screen = win.winfo_screenwidth()  # width of the screen
        height_of_screen = win.winfo_screenheight()  # height of the screen
        #
        # calculate x and y coordinates for the Tk win window
        x_dim = (width_of_screen / 2) - (width / 2)
        x_dim = x_dim - 600  # positive number moves window to right
        y_dim = (height_of_screen / 2) - (height / 2)
        y_dim = y_dim - 200  # moves window up
        #
        # set the dimensions of the screen and where it is placed
        # pylint: disable = consider-using-f-string
        win.geometry("%dx%d+%d+%d" % (width, height, x_dim, y_dim))
        win.title("Reliability Demonstration Testing (RDT) tool")  # Create title

        # Create Widget button Intro
        self.button_intro = tk.Button(  # pylint: disable = attribute-defined-outside-init
            win,
            text="Intro",
            bg="#00FFFF",  # Cyan
            # pylint: disable = unnecessary-lambda
            command=lambda: self.button_intro_pressed(),  # pylint: disable = unnecessary-lambda
            height=2,
            width=10,
        )
        self.button_intro.pack()

        # Create Widget button Start
        self.button_start = tk.Button(  # pylint: disable = attribute-defined-outside-init
            win,
            text="Start",
            bg="#00FF00",  # Lime
            # pylint: disable = unnecessary-lambda
            command=lambda: self.button_start_pressed(),
            height=2,
            width=10,
        )
        self.button_start.pack()

        # Create Widget button Pause
        self.button_pause = tk.Button(  # pylint: disable = attribute-defined-outside-init
            win,
            text="Pause",
            bg="#F4A460",  # Sandy brown
            # pylint: disable = unnecessary-lambda
            command=lambda: self.button_pause_pressed(),
            height=2,
            width=10,
        )
        self.button_pause.pack()

        # Create Widget button Stop
        self.button_stop = tk.Button(  # pylint: disable = attribute-defined-outside-init
            win,
            text="Stop",
            bg="tomato",
            # pylint: disable = unnecessary-lambda
            command=lambda: self.button_stop_pressed(),
            height=2,
            width=10,
        )
        self.button_stop.pack()

        # Create Widget button Exit tool
        self.button_exit = tk.Button(  # pylint: disable = attribute-defined-outside-init
            win,
            text="Exit tool",
            bg="deeppink",
            # pylint: disable = unnecessary-lambda
            command=lambda: self.button_exit_pressed(),
            height=2,
            width=10,
        )
        self.button_exit.pack()

        return win

    # pylint: disable=too-many-arguments
    def wait_for_button_press(self, win, ini_file_list, obj_list, ferr_ptr, fout_ptr):
        """Main loop waiting for button Start press"""

        # There are 3 loops from largest to smallest:
        # 1) tool invocation run, creates GUI & runs through 0 or more Cycles
        #    See method test_tool_invoked()
        # 2) Cycle run which is 0 or more times through commands in .ini COMMAND
        #    .log & .err files created
        #    new cycle if button Start pressed
        #    Started by method cycle_run()
        # 3) Command loop that reads init.ini and runs 1 time commands in COMMAND
        #    See method command_list_run()

        while not self.button_start_flg:
            win.update()
            if self.button_intro_flg is True:
                messagebox.showinfo("Introduction message", self.intro_msg)
                self.button_intro_flg = False
            if self.button_exit_flg is True:
                self.exit_program(win)
            if self.button_stop_flg is True:
                self.button_stop_flg = False
            while self.button_start_flg:
                self.button_start_flg = False
                self.cycle_run(win, ini_file_list, obj_list, ferr_ptr, fout_ptr)

    def button_intro_pressed(self):
        """Create GUI message box"""
        if self.button_intro_flg is True:
            self.button_intro_flg = False
        else:
            self.button_intro_flg = True

    def button_start_pressed(self):
        """Set exit flag"""

        self.button_start_flg = True

    def button_pause_pressed(self):
        """If self.button_pause_flg = True"""

        self.button_pause.flash()
        if self.button_pause_flg is True:
            self.button_pause_flg = False
        else:
            self.button_pause_flg = True

    def button_stop_pressed(self):
        """Set exit flag"""

        self.button_stop.flash()
        self.button_stop_flg = True

    def button_exit_pressed(self):
        """Set exit flag"""

        self.button_exit_flg = True

    def exit_program(self, win):
        """Button <Exit program> pressed"""

        # Do what must be done to exit
        self.button_intro.destroy()
        self.button_start.destroy()
        self.button_pause.destroy()
        self.button_stop.destroy()
        self.button_exit.destroy()
        win.destroy()
        sys.exit(0)

    def remove_comment(self, string_with_comment):
        """Remove:
        Substitute "blank" for:
         line starts with "##" return empty string or
         "<SPACE><SPACE>## to end of line" or
         from "\t##" to end of line
        """
        #
        if "" == re.sub(r"##.*$", "", string_with_comment):
            ret_value = ""
        else:
            ret_value = re.sub(r"\s+##.*$", "", string_with_comment)

        return ret_value

    def stop_test_time_expired(self, ini_file_list):
        """To continue or not based on later than "time to stop tests" in rdt_tool.ini"""

        time_now = Src.rdt_rs232_class.get_time()
        if (  # pylint: disable=simplifiable-if-statement
            ini_file_list[0][4] == "time" and time_now > ini_file_list[0][5]
        ):
            time_expired = True
        else:
            time_expired = False

        return time_expired

    def test_tool_invoked(self):
        """init_gui then wait for button press"""
        ini_file_list = self.ini_file_read()

        win = self.init_gui()
        obj_list, ferr_ptr, fout_ptr = self.preconfig_run(win, ini_file_list)

        win.update()
        self.wait_for_button_press(win, ini_file_list, obj_list, ferr_ptr, fout_ptr)

    def button_pressed_chk(self, win):
        """If button pressed respond to pause, stop or exit"""
        win.update()
        if self.button_exit_flg is True:
            self.exit_program(win)
        if self.button_stop_flg is True:
            self.button_pause_flg = False
        while self.button_pause_flg is True:
            win.update()
            if self.button_exit_flg is True:
                self.exit_program(win)
            if self.button_stop_flg is True:
                self.button_pause_flg = False
                break

    def create_output_files(self, ini_file_list):
        """See method title"""

        fmt_datetime = Src.rdt_rs232_class.get_date_time()
        file_log = (
            RS232_DIR_orig + "/Result/" + ini_file_list[0][0] + fmt_datetime + ".log"
        )
        file_err = (
            RS232_DIR_orig + "/Result/" + ini_file_list[0][1] + fmt_datetime + ".err"
        )
        ferr_ptr = open(  # pylint: disable=consider-using-with
            file_err, "a", encoding="utf-8"
        )
        fout_ptr = open(  # pylint: disable=consider-using-with
            file_log, "a", encoding="utf-8"
        )

        Src.rdt_rs232_class.header_write(ini_file_list[4], True, ferr_ptr)
        Src.rdt_rs232_class.header_write(ini_file_list[4], False, fout_ptr)

        return ferr_ptr, fout_ptr

    # pylint: disable=too-many-arguments
    def cycle_run(self, win, ini_file_list, obj_list, ferr_ptr, fout_ptr):
        """Runs commands_list number of times in rdt_tool.ini"""

        # Create new output files if they don't exist (PRECONFIG creates files only on 1st run)
        if ferr_ptr not in locals():
            ferr_ptr, fout_ptr = self.create_output_files(ini_file_list)
            fout_ptr: TextIO

        num_of_cycles = ini_file_list[0][6]
        run_forever_flg = False
        if num_of_cycles != 0:
            run_forever_flg = False
        else:  # read from .ini
            run_forever_flg = True

        file_list_command = 2  # from rdt_tool.ini read COMMAND (!= PRECONFIG_COMMAND)
        while run_forever_flg is True:
            ferr_ptr, fout_ptr = self.command_list_run(
                win, obj_list, ini_file_list, file_list_command, ferr_ptr, fout_ptr
            )

        while run_forever_flg is False and num_of_cycles > 0:
            ferr_ptr, fout_ptr = self.command_list_run(
                win, obj_list, ini_file_list, file_list_command, ferr_ptr, fout_ptr
            )
            num_of_cycles -= 1
            if self.button_stop_flg:
                num_of_cycles = 0

        ferr_ptr.close()
        fout_ptr.close()

    def preconfig_run(self, win, ini_file_list):
        """Runs preconfig_list once per tool invocation
        creates obj_list, ferr_ptr and fout_ptr"""

        obj_list = self.create_objlist(ini_file_list[3], ini_file_list[5])
        ferr_ptr, fout_ptr = self.create_output_files(ini_file_list)
        fout_ptr: TextIO

        pre_ini_file_list = deepcopy(ini_file_list)
        pre_ini_file_list[0][6] = 1  # Run commands 1 time
        # change COMMAND to PRECONFIG_COMMAND
        pre_ini_file_command = 1
        ferr_ptr, fout_ptr = self.command_list_run(
            win, obj_list, pre_ini_file_list, pre_ini_file_command, ferr_ptr, fout_ptr
        )

        return obj_list, ferr_ptr, fout_ptr

    def output_file_size_chk(self, ini_file_list, ferr_ptr, fout_ptr):
        """If file size above limit in .ini file save old files and start new ones."""

        size_limit = ini_file_list[0][2]

        file_log = fout_ptr.name

        size_file = os.path.getsize(file_log)

        if size_file >= int(size_limit):
            ferr_ptr.close()
            fout_ptr.close()
            file_name_err = ferr_ptr.name
            file_name_log = fout_ptr.name

            if re.search((".*log$"), file_log):

                new_file_err = file_name_err + "_1"
                ferr_ptr = open(  # pylint: disable=consider-using-with
                    new_file_err, "a", encoding="utf-8"
                )
                new_file_log = file_name_log + "_1"
                fout_ptr = open(  # pylint: disable=consider-using-with
                    new_file_log, "a", encoding="utf-8"
                )
            else:
                file_out_number = int(re.sub(r".*_", "", file_name_log))
                file_out_number += 1

                file_err_name = re.sub(r"\d*$", "", file_name_err)
                new_file_err = file_err_name + str(file_out_number)
                ferr_ptr = open(  # pylint: disable=consider-using-with
                    new_file_err, "a", encoding="utf-8"
                )
                file_out_name = re.sub(r"\d*$", "", file_name_log)
                new_file_log = file_out_name + str(file_out_number)
                fout_ptr = open(  # pylint: disable=consider-using-with
                    new_file_log, "a", encoding="utf-8"
                )

        return ferr_ptr, fout_ptr

    #
    # # pylint: disable=too-many-arguments
    # def pre_command_list_run(
    #     self,
    #     obj_list,
    #     ini_file_list,
    #     ferr_ptr,
    #     fout_ptr,
    # ):
    #     """Execute all commands in ini_file_list[pre_config] (ini_file_list[1]) on every port"""
    #
    #     index = 0
    #     cmd_len = len(ini_file_list[1])
    #     os.chdir(RS232_DIR_orig)
    #
    #     while index < cmd_len:  # runs 1 line from commands.ini for every port
    #         # Loop through commands.ini running .cmd files, eg PowerResetAct.cmd
    #         command = ini_file_list[1][index]
    #         if command == "":  # If list has empty line we're done
    #             break
    #         obj_list[index].run_test(ini_file_list[3], command, ferr_ptr, fout_ptr)
    #         # port_len = len(ini_file_list[3])
    #         # j = 0  # Loop through COM ports with 1 command
    #         # while j < port_len:  # runs command for every port
    #         #     obj_list[j].run_test(ini_file_list[3], command, ferr_ptr, fout_ptr)
    #         #     j += 1
    #         index += 1
    #
    #     return ferr_ptr, fout_ptr

    # pylint: disable=too-many-arguments disable=too-many-locals
    def command_list_run(
        self,
        win,
        obj_list,
        ini_file_list,
        ini_file_command,
        ferr_ptr,
        fout_ptr,
    ):
        """Execute all commands in command_init once on every port AND
        check for:
         - pause execution
         - stop execution of this cycle
         - exit from tool
         - start new output files since current ones above limit in rdt_tool.ini"""

        comport_index = 0
        index = 0
        # port_len = len(ini_file_list[3])
        cmd_len = len(ini_file_list[ini_file_command])
        os.chdir(RS232_DIR_orig)

        num_comports = len(ini_file_list[3])

        threads = []

        while index < cmd_len:  # runs 1 line from commands.ini for every port
            # Loop through commands.ini running .cmd files, eg PowerResetAct.cmd
            command = ini_file_list[ini_file_command][index]
            if command == "":
                break

            threads.clear()
            while comport_index < num_comports:
                x_thread = threading.Thread(
                    target=obj_list[comport_index].run_test_old,
                    args=(ini_file_list[3][comport_index], command, ferr_ptr, fout_ptr),
                )
                comport_index += 1
                threads.append(x_thread)
                x_thread.start()

            for thread in threads:
                thread.join()

            self.button_pressed_chk(win)
            if self.button_stop_flg:
                index = cmd_len

            # if time expired return False
            time_expired = self.stop_test_time_expired(ini_file_list)
            if time_expired is True:
                index = cmd_len
                self.button_stop_flg = True
            else:
                index += 1

            # if output files too large save old and make new ones
            ferr_ptr, fout_ptr = self.output_file_size_chk(
                ini_file_list, ferr_ptr, fout_ptr
            )

        return ferr_ptr, fout_ptr

    def create_objlist(self, com_port_list, rs232_list):
        """
        :param rs232_list:
        :param com_port_list: Create objects based on COM port and put in list
        :return: com_port_list
        """
        num_of_ports = len(com_port_list)
        obj_list = list()  # pylint: disable=use-list-literal
        # Create Thread List
        # thread_list = list()  # pylint: disable=use-list-literal
        for i in range(num_of_ports):
            comm_port = com_port_list[i]

            obj_list.append(
                Src.rdt_rs232_class.RdtRS232Class(comm_port, rs232_list)
            )  # Instantiate obj

            # Thraed creation Src.rdt_rs232_class.RdtRS232Class.run_test()
            # thread_list.append(x_thread) # Thread_list

            i = i + 1

        return obj_list  # , thread_list

    def del_objlist(self, obj_list):
        """
        :param obj_list: Delete objects based on COM port and put in list
        :return: com_port_list
        """

        i = 0
        for i in range(len(obj_list)):  # pylint: disable=consider-using-enumerate
            del obj_list[i]
            i = i + 1


if __name__ == "__main__":
    unittest.main()
