import os
import sys
from datetime import datetime

from syslog_manager.query_between_timestamps import query_syslog_between_timestamps


def write_syslog_to_temp_file(tmp_path, syslog_data):
    """Helper function to write syslog data to a temporary file."""
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')
    return temp_file


def test_query_syslog_between_basic(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
"""

    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""

    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == expected_output.strip()


def test_query_syslog_between_no_matches(tmp_path):
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 16 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == ""  # No matches expected


def test_query_syslog_between_edge_case_start_end_file_timestamp(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Start date is the day before the log entries
    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    # End date is the day after the log entries
    end_date = datetime.strptime("15/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""

    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == expected_output.strip()


def test_query_syslog_between_start_after_end_timestamp(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Start date is after the end date
    start_date = datetime.strptime("15/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    # Expected output should be an empty string since the range is invalid
    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == ""


def test_query_syslog_between_same_timestamp(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:01 combo sshd(pam_unix)[19940]: Accepted password for user2 from 192.168.0.5 port 22 ssh2
Jun 14 15:16:01 combo systemd[1]: Started Session 2 of user user2.
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:01 combo sshd(pam_unix)[19940]: Accepted password for user2 from 192.168.0.5 port 22 ssh2
Jun 14 15:16:01 combo systemd[1]: Started Session 2 of user user2.
"""

    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == expected_output.strip()


def test_query_syslog_between_edge_case_overlap_timestamp(tmp_path):
    syslog_data = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Start date is the day before the log entries
    start_date = datetime.strptime("13/06/2024", "%d/%m/%Y")
    # End date is the day after the log entries
    end_date = datetime.strptime("16/06/2024", "%d/%m/%Y")

    expected_output = """\
Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 15 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
"""

    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == expected_output.strip()


def test_query_syslog_between_empty_file(tmp_path):
    # Create an empty syslog file
    empty_syslog = ""
    temp_file = write_syslog_to_temp_file(tmp_path, empty_syslog)

    start_date = datetime.strptime("14/06/2024", "%d/%m/%Y")
    end_date = datetime.strptime("14/06/2024", "%d/%m/%Y")

    # The expected output should be an empty string because there are no entries in the file
    result = query_syslog_between_timestamps(temp_file, start_date, end_date)
    assert result == ""  # No log entries expected
