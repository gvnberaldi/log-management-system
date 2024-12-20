import json
import os
import sys

from syslog_manager.log_query import create_log_query

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)


def test_query_basic_log(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
"""
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)

    process_name = 'sshd'
    expected_output = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    assert result == expected_output.strip()


def test_query_non_existent_process(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)

    process_name = 'nonexistent_process'
    expected_output = ""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    assert result == expected_output


def test_query_special_characters(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(abc_def)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(a+b=c)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)

    process_name = 'sshd(a+b=c)'
    expected_output = """\
Jun 14 15:17:02 combo sshd(a+b=c)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    assert result == expected_output.strip()


def test_query_empty_log(tmp_path):
    syslog_data = """"""
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)

    process_name = 'sshd'
    expected_output = ""
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)
    assert result == expected_output


def test_query_process_name_included_in_another_word(tmp_path):
    syslog_data = """\
Jul 24 04:20:26 combo sshd[12345]: Authentication failure
Jul 24 04:21:30 combo kernel: session opened for user test by sshd
"""

    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)

    process_name = 'sshd'
    expected_output = """\
Jul 24 04:20:26 combo sshd[12345]: Authentication failure
"""

    # Call the function with the process name 'sshd'
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    # Check that the result matches the expected output
    assert result == expected_output.strip()


def test_query_process_name_with_different_case(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo SSHD(some_special_process)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(some_special_process)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(syslog_data)
    process_name = 'sshd(some_special_process)'  # Lowercase query, different case in log
    expected_output = """\
Jun 14 15:17:02 combo sshd(some_special_process)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)
    assert result == expected_output.strip()


def test_query_basic_json(tmp_path):
    syslog_data = [
        {"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939,
         "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"},
        {"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940,
         "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"},
        {"timestamp": "Jun 14 15:18:03", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 1 of user user1."},
        {"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941,
         "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"},
        {"timestamp": "Jun 16 10:00:00", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 2 of user user2."}
    ]

    temp_file = tmp_path / "syslog_data.json"
    with open(temp_file, 'w') as f:
        json.dump(syslog_data, f)

    process_name = 'sshd'
    expected_output = """\
{"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939, "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"}
{"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940, "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"}
{"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941, "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"}
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    assert result == expected_output.strip()


def test_query_syslog_between_basic_csv(tmp_path):
    syslog_data = """\
timestamp,hostname,process,pid,message
Jun 13 15:16:01,combo,sshd(pam_unix),19939,"authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
Jun 14 15:17:02,combo,sshd(pam_unix),19940,"Accepted password for user1 from 192.168.0.1 port 22 ssh2"
Jun 14 15:18:03,combo,systemd,1,"Started Session 1 of user user1."
Jun 15 15:19:04,combo,sshd(pam_unix),19941,"Failed password for user1 from 192.168.0.2 port 22 ssh2"
Jun 16 10:00:00,combo,systemd,1,"Started Session 2 of user user2."
"""

    temp_file = tmp_path / "syslog_data.csv"
    temp_file.write_text(syslog_data)

    process_name = 'sshd'

    expected_output = """\
{'timestamp': 'Jun 13 15:16:01', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19939', 'message': 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'}
{'timestamp': 'Jun 14 15:17:02', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19940', 'message': 'Accepted password for user1 from 192.168.0.1 port 22 ssh2'}
{'timestamp': 'Jun 15 15:19:04', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19941', 'message': 'Failed password for user1 from 192.168.0.2 port 22 ssh2'}
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_process(process_name)

    assert result == expected_output.strip()
