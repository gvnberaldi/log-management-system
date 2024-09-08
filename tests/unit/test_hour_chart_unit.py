import pytest

from syslog_manager.hourly_report import count_events_per_hour


def test_count_events_per_hour_with_sample_data(tmp_path):
    # Sample log lines with different hours
    syslog_content = """Jun 15 00:01:00 combo sshd(pam_unix)[10001]: some message
Jun 15 01:15:30 combo sshd(pam_unix)[10002]: another message
Jun 15 01:45:10 combo sshd(pam_unix)[10003]: yet another message
Jun 15 02:05:22 combo sshd(pam_unix)[10004]: message here
Jun 15 14:20:43 combo sshd(pam_unix)[10005]: message for 14th hour
Jun 15 14:35:50 combo sshd(pam_unix)[10006]: another message for 14th hour
Jun 16 14:35:50 combo sshd(pam_unix)[10006]: another message for 14th hour
Jun 17 22:10:01 combo sshd(pam_unix)[10007]: message for 22nd hour
Jun 18 02:10:01 combo sshd(pam_unix)[10007]: message for 22nd hour
"""

    syslog_file = tmp_path / "syslog.log"
    syslog_file.write_text(syslog_content)

    expected_counts = {
        0: 1,
        1: 2,
        2: 2,
        14: 3,
        22: 1
    }

    hourly_counts = count_events_per_hour(syslog_file)

    # Assert that the hourly_counts matches the expected counts
    for hour, count in expected_counts.items():
        assert hourly_counts.get(hour, 0) == count


def test_count_events_per_hour_with_empty_data(tmp_path):
    syslog_content = """"""

    syslog_file = tmp_path / "syslog.log"
    syslog_file.write_text(syslog_content)
    expected_counts = {}

    hourly_counts = count_events_per_hour(syslog_file)

    # Assert that the hourly_counts is empty as no log entries are present
    assert hourly_counts == expected_counts


def test_count_events_per_hour_with_no_hourly_data(tmp_path):
    # Log entries with no valid hour data (e.g., invalid timestamps)
    syslog_content = """Jun 14 25:01:00 combo sshd(pam_unix)[10001]: some message
Jun 15 26:15:30 combo sshd(pam_unix)[10002]: another message
Jun 16 -01:15:30 combo sshd(pam_unix)[10002]: another message
"""

    syslog_file = tmp_path / "syslog.log"
    syslog_file.write_text(syslog_content)
    expected_counts = {}

    hourly_counts = count_events_per_hour(syslog_file)

    # Assert that no events are counted as the timestamps are invalid
    assert hourly_counts == expected_counts


def test_count_events_per_hour_with_boundary_hours(tmp_path):
    syslog_content = """Jun 25 00:00:00 combo sshd(pam_unix)[10001]: some message
Jun 26 23:59:59 combo sshd(pam_unix)[10002]: another message
"""

    syslog_file = tmp_path / "syslog.log"
    syslog_file.write_text(syslog_content)

    expected_counts = {
        0: 1,
        23: 1
    }

    hourly_counts = count_events_per_hour(syslog_file)

    # Assert that the boundary hours are correctly counted
    for hour, count in expected_counts.items():
        assert hourly_counts.get(hour, 0) == count
