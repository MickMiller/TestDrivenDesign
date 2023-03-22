"""
File: rdt_rs232_class.py
Author: Gerard (Mick) Miller
Purpose: run all tests on pmp module executable file
Methods:
    __init__(self, port="COM2", baud=2400):
    setUp(self):
    tearDown(self):
    ini_file_read(self):
    log_size_max_ae(self, log_size_max):
    baud_ae(self, baud):
    run_loop_or_time_ae(self, run_loop_or_time):
    stop_test_time_ae(self, stop_test_time):
    loops_through_commands_calc(self, loops_through_commands_ini):
    init_read(self, ini_list):
    command_read(self, ini_list):
    port_read(self, ini_list):
    header_read(self, ini_list, header_str):
    rs232_read(self, ini_list, rs232_str):
    init_gui(self, init_list, command_list, port_list, header_list_1, rs232_list):
    wait_for_button_press(
    button_intro_pressed(self):
    button_start_pressed(self):
    button_pause_pressed(self):
    button_stop_pressed(self):
    button_exit_pressed(self):
    exit_program(self, win):
    remove_comment(self, string_with_comment):
    stop_test_time_expired(self, init_list):
    test_tool_invoked(self):
    button_pressed_chk(self, win):
    create_output_files(self, init_list, header_list_1):
    cycle_run(
    output_file_size_chk(self, init_list, ferr_ptr, fout_ptr):
    command_list_run(  # pylint: disable=too-many-arguments
    create_objlist(self, com_port_list, rs232_list):
    del_objlist(self, obj_list):
"""
import os
import re
import unittest
import threading
from threading import Lock
from datetime import datetime
from typing import Any, Union
import time
import serial
import Src.config
from Src.obr_serial import WasteMsec

lock = Lock()


class RdtRS232Class(unittest.TestCase, Exception):
    """Read and write RS-232 COM port"""

    # pylint: disable=too-many-instance-attributes
    # Copied Production code - leaving as is
    def __init__(self, port, rs232_list):
        """Initialize RS-232 COM port"""
        super().__init__()
        self.obj_read = ReadClass()  # instantiate obj
        self.obj_write = WriteClass()  # instantiate obj
        self.port = port
        self.baud = 9600
        self.bytesize = rs232_list[1]
        self.parity = serial.PARITY_EVEN
        self.eos = "\r"
        self.timeout = 1
        self.stopbits = serial.STOPBITS_ONE
        self.xonxoff = False
        self.rtscts = False
        self.dtrdsr = False
        self.write_timeout = 0
        self.serobj = serial.Serial(
            port=self.port,
            baudrate=self.baud,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            bytesize=serial.SEVENBITS,
            xonxoff=False,
            rtscts=False,
            write_timeout=0,
        )

    def run_test(self, comm_port_list, in_file, ferr_ptr, fout_ptr):
        """Find and open .cmd file.  Loop through lines, 1 command to target per line"""

        ret_result = "unset"
        if ret_result == "unset":
            cmd_res_list = infile_read(in_file)
            if cmd_res_list == "FileNotFound":
                ret_result = "FileNotFound"
            else:  # Run command online
                threads = []
                for comm_port in comm_port_list:
                    x_thread = threading.Thread(target=self.cmd_type_run, args=(
                        comm_port, cmd_res_list, ferr_ptr, fout_ptr
                    ))
                    threads.append(x_thread)
                    x_thread.start()

                for thread in threads:
                    thread.join()

        return ret_result

    def run_test_old(self, comm_port, in_file, ferr_ptr, fout_ptr):
        """Find and open .cmd file.  Loop through lines, 1 command to target per line"""

        ret_result = "unset"
        if ret_result == "unset":
            cmd_res_list = infile_read(in_file)
            if cmd_res_list == "FileNotFound":
                ret_result = "FileNotFound"
            else:  # Run command online
                ret_result = self.cmd_type_run(
                    comm_port, cmd_res_list, ferr_ptr, fout_ptr
                )

        return ret_result

    # pylint: disable = too-many-branches
    def cmd_type_run(self, comm_port, cmd_res_list, ferr_ptr, fout_ptr):
        """cmd_res_list are contents of .cmd file
        each line is examined and may be sent out COM port
        Each line in cmd_es_list is: type of test, cmd, ER
        Returned is ret_result. ret_result not = "Pass" is saved so if one cmd in a
        file does not have Expected Results then anomaly description returned.
        """

        anomaly_description = "unset"
        ret_result = "unset"

        date = get_date()
        time_start = get_time()

        for line in cmd_res_list:
            cmd_type = line[0]
            cmd = "cmd_unset"
            if re.match(r"^\s*test_comment.*", cmd_type):
                pass
            else:
                cmd = line[1]
            Src.config.command_count += 1

            if len(line) == 0:
                ret_result = "Emptyfile"
            elif cmd_type == "test_in":
                ret_result = self.test_in(comm_port, line, ferr_ptr, fout_ptr)
            elif re.match(r"^\s*test_comment", cmd_type):
                ret_result = test_comment(line, fout_ptr)
            elif cmd_type == "test_equal":
                ret_result = self.test_equal(comm_port, line, ferr_ptr, fout_ptr)
            elif cmd_type == "test_sleep":
                ret_result = self.test_sleep(comm_port, line, fout_ptr)
            elif cmd_type == "read_to_clear_buffer":
                ret_result = self.send_cmd_ignore_response(cmd)
            elif cmd_type == "delay_sec":
                WasteMsec(float(cmd) * 1000)
                ret_result = "Pass"
            elif cmd_type == "test_limit":
                ret_result = self.test_limit(comm_port, line, ferr_ptr, fout_ptr)
            else:
                pc_print(
                    date,
                    time_start,
                    Src.config.command_count,
                    comm_port,
                    "",
                    "",
                    "fail in rdt_rs232_class.py: Command not found, expecting"
                    " test_in, ...",
                    False,
                    True,
                    ferr_ptr,
                )
                ret_result = "NoValidCommands"

            if ret_result != "Pass" and anomaly_description == "unset":
                anomaly_description = ret_result

        if anomaly_description in ["unset"]:
            return ret_result

        return anomaly_description

    def test_limit(self, comm_port, line, ferr_ptr, fout_ptr):
        """
        Values tested
        - below lower limit, ER=$E4 - invalid data argument
        - at lower limit, ER=lowerlimit in command line
        - at upper limit, ER=upperlimit in command line
        - above upper limit, ER=$E4 - invalid data argument
        """

        # Save initial value
        cmd_root = line[1]
        saved_initial_value = self.obj_write.rdt_write(
            cmd_root + "?", self.serobj, self.eos
        )

        below_lowerlimit_test = self.below_lower_limit(
            comm_port, line, ferr_ptr, fout_ptr
        )
        at_lowerlimit_test = self.at_lower_limit(comm_port, line, ferr_ptr, fout_ptr)
        at_upperlimit_test = self.at_upper_limit(comm_port, line, ferr_ptr, fout_ptr)
        above_upperlimit_test = self.above_upper_limit(
            comm_port, line, ferr_ptr, fout_ptr
        )

        # Restore initial value
        rdt_write_set_1 = re.sub(r"\$B", "", saved_initial_value)
        rdt_write_set_2 = re.sub(r".$", "", rdt_write_set_1)
        rdt_write_set = cmd_root + rdt_write_set_2
        self.obj_write.rdt_write(rdt_write_set, self.serobj, self.eos)

        if (
            below_lowerlimit_test == "Pass"
            and at_lowerlimit_test == "Pass"
            and at_upperlimit_test == "Pass"
            and above_upperlimit_test == "Pass"
        ):
            return "Pass"

        return "Fail"

    def below_lower_limit(self, comm_port, line, ferr_ptr, fout_ptr):
        """below lower limit, Expected Results=$E4 - invalid data argument"""
        # Unpack command line
        cmd_root = line[1]
        lowerlimit = line[2]
        comment = line[6]

        value_to_write = int(lowerlimit) - 1
        rdt_write_set = cmd_root + str(value_to_write)
        ret_val = self.obj_write.rdt_write(rdt_write_set, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()

        if ret_val == "$E4":
            below_lowerlimit_test = "Pass"
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                ret_val,
                ret_val,
                comment,
                False,
                True,
                fout_ptr,
            )
        else:
            below_lowerlimit_test = "test_below_lowerlimit Failed."
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                "Not $E4 - invalid data argument",
                ret_val,
                "test_below_lowerlimit",
                False,
                True,
                ferr_ptr,
            )

        return below_lowerlimit_test

    # pylint: disable=too-many-locals
    def at_lower_limit(self, comm_port, line, ferr_ptr, fout_ptr):
        """at lower limit, ER=lowerlimit in command line"""
        # Unpack command line
        cmd_root = line[1]
        lowerlimit = line[2]
        lowerlimit_expected_result = line[3]
        comment = line[6]

        value_to_write = lowerlimit
        rdt_write_set = cmd_root + value_to_write
        rdt_write_get = cmd_root + "?"
        self.obj_write.rdt_write(rdt_write_set, self.serobj, self.eos)
        ret_val = self.obj_write.rdt_write(rdt_write_get, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()

        if ret_val == lowerlimit_expected_result:
            at_lowerlimit_test = "Pass"
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                lowerlimit_expected_result,
                ret_val,
                comment,
                False,
                True,
                fout_ptr,
            )
        else:
            at_lowerlimit_test = "test_at_lowerlimit Failed."
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                lowerlimit_expected_result,
                comm_port,
                ret_val,
                "test at lower limit Failed",
                False,
                True,
                ferr_ptr,
            )

        return at_lowerlimit_test

    # pylint: disable=too-many-locals
    def at_upper_limit(self, comm_port, line, ferr_ptr, fout_ptr):
        """at upper limit, ER=upperlimit in command line"""
        # Unpack command line
        cmd_root = line[1]
        upperlimit = line[4]
        upperlimit_expected_result = line[5]
        rdt_write_get = cmd_root + "?"
        comment = line[6]

        value_to_write = upperlimit
        rdt_write_set = cmd_root + value_to_write
        self.obj_write.rdt_write(rdt_write_set, self.serobj, self.eos)
        ret_val = self.obj_write.rdt_write(rdt_write_get, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()

        if ret_val == upperlimit_expected_result:
            at_upperlimit_test = "Pass"
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                upperlimit_expected_result,
                ret_val,
                comment,
                False,
                True,
                fout_ptr,
            )
        else:
            at_upperlimit_test = "test at upperlimit Failed."
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                upperlimit_expected_result,
                ret_val,
                "test_at_upperlimit - Failed",
                False,
                True,
                ferr_ptr,
            )

        return at_upperlimit_test

    def above_upper_limit(self, comm_port, line, ferr_ptr, fout_ptr):
        """above upper limit, ER=$E4 - invalid data argument"""
        # Unpack command line
        cmd_root = line[1]
        upperlimit = line[4]
        comment = line[6]

        value_to_write = int(upperlimit) + 1
        rdt_write_set = cmd_root + str(value_to_write)
        ret_val = self.obj_write.rdt_write(rdt_write_set, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()

        if ret_val == "$E4":
            above_upperlimit_test = "Pass"
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                "$E4",
                ret_val,
                comment,
                False,
                True,
                fout_ptr,
            )
        else:
            above_upperlimit_test = "test above upperlimit Failed."
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                "$E4 - invalid data argument",
                ret_val,
                "test_above_upperlimit - Failed",
                False,
                True,
                ferr_ptr,
            )

        return above_upperlimit_test

    #
    # def read_to_clear_buffer(self, line, f_ptr):
    #     """Get and validate via expected results equal to actual results"""
    #
    #     cmd = line[1]
    #
    #     act_res = self.obj_write.rdt_write(cmd, self.serobj, self.eos)
    #
    #     date = get_date()
    #     time_start = get_time()
    #
    #     if "$B" in act_res:
    #         pc_print(
    #             date,
    #             time_start,
    #             Src.config.command_count,
    #             "$B",
    #             act_res,
    #             "",
    #             False,
    #             True,
    #             f_ptr,
    #         )
    #         ret_value = "Pass"
    #     else:
    #         pc_print(
    #             date,
    #             time_start,
    #             Src.config.command_count,
    #             "$B",
    #             act_res,
    #             "",
    #             False,
    #             True,
    #             f_ptr,
    #         )
    #         ret_value = "Fail"
    #
    #     return ret_value

    def test_in(self, comm_port, line, ferr_ptr, fout_ptr):
        """Get and validate via expected results equal to actual results"""

        cmd = line[1]
        exp_res = line[2]
        comment = line[3]

        act_res = self.obj_write.rdt_write(cmd, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()

        if exp_res in act_res:
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                exp_res,
                act_res,
                comment,
                False,
                True,
                fout_ptr,
            )
            ret_value = "Pass"
        else:
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                exp_res,
                act_res,
                comment,
                False,
                True,
                ferr_ptr,
            )
            ret_value = "Fail"

        return ret_value

    def test_sleep(self, comm_port, line, fout_ptr):
        """Sleep for number of mSec specified
           Assumed command (sleep) succeeds """

        time.sleep(int(line[1]) / 1000)

        date = get_date()
        time_start = get_time()
        # comment = line[3]

        pc_print(
            date,
            time_start,
            Src.config.command_count,
            comm_port,
            "sleep for" + line[1] + " mSec",  # "pass",  # exp_res,
            "pass",  # act_res,
            "",  # comment,
            False,
            True,
            fout_ptr,
        )

        return "Pass"

    def test_equal(self, comm_port, line, ferr_ptr, fout_ptr):
        """Get and validate via expected results equal to actual results.
        Note:  cmd setting value is not checked here.  For example cmd=A1 sets A to 1.
        Expected response is $B0, ie rdt replied that cmd=A1 succeeded.
        We are interested in if response to GET cmd is As Expected.
        """

        cmd = line[1]
        exp_res = line[2]
        comment = line[3]

        act_res = self.obj_write.rdt_write(cmd, self.serobj, self.eos)

        date = get_date()
        time_start = get_time()
        #lock = Lock()
        #lock.acquire()  # pylint: disable=consider-using-with
        if act_res == exp_res:
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                exp_res,
                act_res,
                comment,
                False,
                True,
                fout_ptr,
            )
            ret_value = "Pass"
        else:
            pc_print(
                date,
                time_start,
                Src.config.command_count,
                comm_port,
                exp_res,
                act_res,
                comment,
                False,
                True,
                ferr_ptr,
            )
            ret_value = "Fail"
        #lock.release()
        return ret_value

    def send_cmd_ignore_response(self, cmd):
        """Some commands have unreliable results (as of 20220311):
        change baud rate response can't be read since read is at old rate and
            response is(presumably) at new rate
        1st baud rate read command (#l1?) is one of:
            correct response
            no response
            $E4
        """

        self.obj_write.rdt_write(cmd, self.serobj, self.eos)
        return "Pass"


def cr_lf_remove(dest_line):
    """Remove <CR> and <LF> from strings"""

    dest_line2 = dest_line.replace("\r", "")
    dest_line3 = dest_line2.replace("\n", "")

    return dest_line3


def pc_print(
    test, p_or_f, cmd, comm_port, exp_res, act_res, comment, no_cr, console_print, f_ptr
):  # pylint: disable=too-many-arguments
    """Prints to console and file"""

    # Empty list is invalid format for string so can't be printed
    if not act_res:
        act_res = ""
    if not exp_res:
        exp_res = ""

    if no_cr is True:
        if console_print is True:
            print(
                f"{test:<52}{p_or_f:<15}{comm_port:<14}{cmd:<14}{exp_res:<22}{act_res:<15} "
                f"     {comment:<30}"
            )
        f_ptr.write(
            f"{test:<52}{p_or_f:<15}{comm_port:<14}{cmd:<14}{exp_res:<22}{act_res:<15}   "
            f"   {comment:<30}\n",
            End="",
        )
    else:
        if console_print is True:
            print(
                f"{test:<52}{p_or_f:<15}{comm_port:<14}{cmd:<14}{exp_res:<22}{act_res:<15} "
                f"     {comment:<30}"
            )
        f_ptr.write(
            f"{test:<52}{p_or_f:<15}{comm_port:<14}{cmd:<14}{exp_res:<22}{act_res:<15}   "
            f"   {comment:<30}\n"
        )

    f_ptr.flush()
    os.fsync(f_ptr.fileno())


def test_comment(line, f_ptr):
    """Prints comment"""

    comment_1 = re.sub("test_comment", "", line[0])
    comment_2 = ", ".join(line[1:])
    comment = comment_1 + comment_2

    date = get_date()
    time_start = get_time()

    pc_print(
        date, time_start, Src.config.command_count, "", "", "", comment, False, True, f_ptr
    )
    return "Pass"


def infile_read(file_name):
    """Given filename returns file contents in 2 by n list:
    - without blank lines
    - without comments
    """

    cmd_res_list = []

    file_path_2 = os.getcwd()
    file_path = file_path_2 + "\\Command\\" + file_name

    try:
        with open(file_path, "r", encoding="utf-8") as f_ptr:
            for rows in f_ptr:
                cmd_res = rows.partition("##")[0]
                cmd_res_2 = cmd_res.rstrip()
                comment = rows.partition("##")[2]
                comment_2 = comment.replace("\n", "")
                if cmd_res_2 != "":
                    cmd_res_3 = cmd_res_2 + "," + comment_2
                else:
                    cmd_res_3 = comment_2
                if cmd_res_3 != "":
                    cmd_res_list.append(cmd_res_3.split(","))
    except FileNotFoundError:
        cmd_res_list = "FileNotFound"

    return cmd_res_list


class ReadClass(unittest.TestCase, Exception):
    """Read:
     .ini files
     RS-232 COM port TBD does it do this?
     controller port
     EtherCAT TBD datagrams?

        Methods:
    read_file()
    """

    def __init__(self):
        """class ReadClass"""
        super().__init__()

    def read_file(self, file):
        """Read file"""

        # print("Inside rdt_rs232_class > read_file")  # DEBUG
        file_as_list = "unset"
        try:
            with open(file, "r", encoding="utf-8") as f_ptr:
                data = f_ptr.read()
                file_as_list = data.split("\n")
        except FileNotFoundError:
            self.assertNotEqual(
                "communications.ini file not found",
                "Trigger assert",
                "See .out for errors",
            )

        return file_as_list

    def port_read(self):
        """Read line from serial port"""

        try:
            # data = self.serobj.readline()
            return "data"
        except IOError:
            return "port_read error"


class WriteClass(unittest.TestCase, Exception):
    """Write files & RS-232 COM port"""

    def __init__(self):
        """WriteClass init"""
        super().__init__()

    def write_test_header(self, cmd_file, f_ptr):
        """See method name"""

        header = (
            "\nStart test: "
            + cmd_file  # noqa: W503
            + " vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n"
        )
        pc_print(header, "", "", "", "", "", "", False, True, f_ptr)

        pc_print(
            "CMD_TYPE",
            "P/F",
            "CMD",
            "COMM PORT",
            "ER",
            "AR",
            "COMMENT",
            False,
            True,
            f_ptr,
        )
        pc_print(
            "__________",
            "______",
            "______",
            "__________",
            "__________",
            "__________",
            "____________________",
            False,
            True,
            f_ptr,
        )

    def write_test_trailer(self, cmd_file, f_ptr):
        """See method name"""

        trailer = (
            "\nEnd   test: "
            + cmd_file  # noqa: W503
            + " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"  # noqa: W503
        )
        pc_print(trailer, "", "", "", "", "", "", False, True, f_ptr)

    def write_all_tests_header(self, f_ptr):
        """See method name"""

        as_1 = (
            "All tests start: "
            "v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v"
            "v=v=v=v=v=v=v=v=v=v=v="
        )
        pc_print(as_1, "", "", "", "", "", "", False, True, f_ptr)

    def write_cmd_not_tested(self, command_file, f_ptr):
        """See method name"""
        pc_print("\n" + command_file, "", "", "", "", "", "", False, True, f_ptr)

    def write_error_in_write_summary(self, command_file, console_print, f_ptr):
        """See method name"""
        pc_print(
            "Error running file: ",
            command_file,
            Src.config.command_count,
            "",
            "",
            "",
            "",
            False,
            console_print,
            f_ptr,
        )
        pc_print("", "", "", "", "", "", "", False, True, f_ptr)

    def port_write_with_checksum(self, arg_msg, serobj, eos):
        """Method called to write to port"""

        # with lock:
        lock.acquire()  # pylint: disable=consider-using-with
        try:
            lf_out_pak = "$" + checksum_gen(arg_msg) + eos
            lf_bin_pak = bytes(lf_out_pak, encoding="ISO-8859-1")
            serobj.flush()
            serobj.write(lf_bin_pak)
            WasteMsec(100)  # original value was problematic in XVS simulator, 100 OK
            exit_flag = 1
            maxreadcntr = 1
            while exit_flag:
                resp = serobj.read(512)
                if len(resp) >= 1:
                    exit_flag = 0
                maxreadcntr = maxreadcntr + 1
                # if maxreadcntr >= 50:
                if maxreadcntr >= 5:
                    exit_flag = 0
                if exit_flag == 1:
                    WasteMsec(100)
            # noinspection PyUnboundLocalVariable
            lf_slave_reply = resp.decode("ISO-8859-1")
        except IOError:
            lf_slave_reply = resp.decode("ISO-8859-1")
        lock.release()

        return lf_slave_reply

    def rdt_write(self, cmd_to_rdt, serobj, eos):
        """Send cmd via rdt and return result"""

        act_res_tmp = self.port_write_with_checksum(cmd_to_rdt, serobj, eos)
        act_res = cr_lf_remove(act_res_tmp)
        return act_res


def header_write(header_list_1, console_print, f_ptr):
    """Write headers for .log and .err files"""

    pc_print(
        header_list_1[0],
        header_list_1[1],
        header_list_1[2],
        header_list_1[3],
        header_list_1[4],
        header_list_1[5],
        header_list_1[6],
        False,
        console_print,
        f_ptr,
    )


def checksum_gen(arg_str_msg="@", f_ptr=None):
    """Generate Checksum"""

    msg = "checksum_gen: arg_str_msg is null string, no content."

    date = get_date()
    time_start = get_time()

    if len(arg_str_msg) < 1:
        pc_print(date, time_start, "", "", "", "", "\n" + msg, False, True, f_ptr)
        return "checksum_gen arg_str_msg in null"

    sum_area = 0
    for lf_char in arg_str_msg:
        lf_ascii = (
            ord(lf_char) & 0x7F
        )  # only 7 bit asciii since protocol is 7 data, even parity in use.
        sum_area += lf_ascii  # add char.
        sum_area = sum_area & 0xFF  # strip to byte, modulo 256

    lf_rez_sum: Union[int, Any] = 0x30 + (0x3F & (sum_area ^ (sum_area >> 6)))
    lf_new_msg = arg_str_msg + chr(lf_rez_sum)
    return lf_new_msg


def port_write(self, data):
    """Write serial port"""
    try:
        ret_val = self.serobj.write(data)
        return ret_val
    except IOError:
        self.serobj.close()
        return "Failed to write data to Serial port!"


def get_date_time():
    """Returns YYYY-MM-DD_HH-MM-SS"""

    date_time_1 = datetime.now()
    date_time_2 = str(date_time_1)
    date_time_3 = re.sub(" ", "_", date_time_2)
    date_time_4 = date_time_3.replace(":", "-")
    date_time = re.sub(r"\..*", "", date_time_4)
    return date_time


def get_date():
    """Returns YYYY/MM/DD"""

    now = datetime.now()
    date_now_1 = now.strftime("%m-%d-%y %H:%M:%S")
    # removes everything after <SPACE>
    date_now_2 = re.sub(r" .*", "", date_now_1)

    return date_now_2


def get_time():
    """Returns HHMMSS"""

    time_now_1 = datetime.now()
    time_now_2 = str(time_now_1)
    # removes numbers at start of string, DASHs up to and including SPACE
    time_now_3 = re.sub(r"^\d*-\d*-\d* ", "", time_now_2)
    # removes DOT to end of line
    time_now_4 = re.sub(r"\.\d*", "", time_now_3)

    return time_now_4
