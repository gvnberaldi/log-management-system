import json
from datetime import datetime
import os
import sys

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.log_query import create_log_query


def test_query_syslog_between_basic_log(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
"""

    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == expected_output.strip()


def test_query_syslog_between_no_matches_log(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 16 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == ""  # No matches expected


def test_query_syslog_between_edge_case_start_end_file_timestamp_log(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    # Start date is the day before the log entries
    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    # End date is the day after the log entries
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == expected_output.strip()


def test_query_syslog_between_start_after_end_timestamp_log(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    # Start date is after the end date
    start_date = datetime.strptime("15/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    # Expected output should be an empty string since the range is invalid
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == ""


def test_query_syslog_between_same_timestamp_log(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:01 combo sshd(pam_unix)[19940]: Accepted password for user2 from 192.168.0.5 port 22 ssh2
Jun 14 15:16:01 combo systemd[1]: Started Session 2 of user user2.
"""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:01 combo sshd(pam_unix)[19940]: Accepted password for user2 from 192.168.0.5 port 22 ssh2
Jun 14 15:16:01 combo systemd[1]: Started Session 2 of user user2.
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == expected_output.strip()


def test_query_syslog_between_edge_case_overlap_timestamp_log(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data)

    # Start date is the day before the log entries
    start_date = datetime.strptime("13/06/2024", "%d/%m/%Y")
    # End date is the day after the log entries
    end_date = datetime.strptime("16/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == expected_output.strip()


def test_query_syslog_between_empty_file_log(tmp_path):
    # Create an empty syslog file
    empty_syslog = ""
    # Specify a filename with the .log extension
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(empty_syslog)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    # The expected output should be an empty string because there are no entries in the file
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == ""  # No log entries expected


def test_query_syslog_between_basic_json(tmp_path):
    syslog_data = [
        {"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939, "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"},
        {"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940, "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"},
        {"timestamp": "Jun 14 15:18:03", "hostname": "combo", "process": "systemd", "pid": 1, "message": "Started Session 1 of user user1."},
        {"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941, "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"},
        {"timestamp": "Jun 16 10:00:00", "hostname": "combo", "process": "systemd", "pid": 1, "message": "Started Session 2 of user user2."}
    ]

    temp_file = tmp_path / "syslog.json"
    with open(temp_file, 'w') as f:
        json.dump(syslog_data, f)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
{"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940, "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"}
{"timestamp": "Jun 14 15:18:03", "hostname": "combo", "process": "systemd", "pid": 1, "message": "Started Session 1 of user user1."}
{"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941, "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"}
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

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

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
{'timestamp': 'Jun 14 15:17:02', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19940', 'message': 'Accepted password for user1 from 192.168.0.1 port 22 ssh2'}
{'timestamp': 'Jun 14 15:18:03', 'hostname': 'combo', 'process': 'systemd', 'pid': '1', 'message': 'Started Session 1 of user user1.'}
{'timestamp': 'Jun 15 15:19:04', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19941', 'message': 'Failed password for user1 from 192.168.0.2 port 22 ssh2'}
"""

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_between_timestamps(start_date, end_date)

    assert result == expected_output.strip()
