import pytest

from syslog_manager.utility import parse_syslog_line
from syslog_manager.utility import create_json_schema, validate_json


def test_valid_syslog_line_with_pid():
    line = "Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
    expected = {
        'timestamp': 'Jun 14 15:16:01',
        'hostname': 'combo',
        'process': 'sshd(pam_unix)',
        'pid': '19939',
        'message': 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'
    }
    assert parse_syslog_line(line) == expected


def test_valid_syslog_line_without_pid():
    line = "Jun 14 15:16:01 combo sshd(pam_unix): authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
    expected = {
        'timestamp': 'Jun 14 15:16:01',
        'hostname': 'combo',
        'process': 'sshd(pam_unix)',
        'pid': None,
        'message': 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'
    }
    assert parse_syslog_line(line) == expected


def test_invalid_syslog_line_format():
    line = "This is not a syslog line"
    assert parse_syslog_line(line) is None


def test_invalid_timestamp_format():
    line = "2024-09-04 12:34:56 combo sshd: authentication failure"
    assert parse_syslog_line(line) is None


def test_empty_line():
    line = ""
    assert parse_syslog_line(line) is None


@pytest.mark.parametrize("line, expected", [
    ("Jul 20 12:00:00 myhost myproc[12345]: test message", {
        'timestamp': 'Jul 20 12:00:00',
        'hostname': 'myhost',
        'process': 'myproc',
        'pid': '12345',
        'message': 'test message'
    }),
    ("Aug 30 08:59:59 yourhost yourproc: another test message", {
        'timestamp': 'Aug 30 08:59:59',
        'hostname': 'yourhost',
        'process': 'yourproc',
        'pid': None,
        'message': 'another test message'
    }),
    ("Dec 31 23:59:59 hostname process: message without pid", {
        'timestamp': 'Dec 31 23:59:59',
        'hostname': 'hostname',
        'process': 'process',
        'pid': None,
        'message': 'message without pid'
    })
])
def test_various_cases(line, expected):
    assert parse_syslog_line(line) == expected


def test_valid_json():
    # Placeholder for valid JSON data
    valid_data = {
        "timestamp": "Jun 14 15:16:01",
        "hostname": "localhost",
        "process": "sshd",
        "pid": 1234,
        "message": "User login successful"
    }

    # This should pass without any issues
    json_schema = create_json_schema()  # create_json_schema function will be implemented later
    validate_json(json_schema, valid_data)  # validate_json function will be implemented later


def test_invalid_json_missing_fields():
    # Placeholder for invalid JSON data missing required fields
    invalid_data_missing_fields = {
        "timestamp": "2024-08-21T14:30:00Z",
        "hostname": "localhost",
        "process": "sshd",
        # 'message' is missing
    }

    json_schema = create_json_schema()
    # This should raise a ValueError due to missing required fields
    with pytest.raises(ValueError):
        validate_json(json_schema, invalid_data_missing_fields)


def test_invalid_json_bad_format():
    # Placeholder for invalid JSON data with incorrect timestamp format
    invalid_data_bad_format = {
        "timestamp": "invalid-timestamp",
        "hostname": "localhost",
        "process": "sshd",
        "pid": 1234,
        "message": "User login successful"
    }

    json_schema = create_json_schema()
    # This should raise a ValueError due to invalid timestamp format
    with pytest.raises(ValueError):
        validate_json(json_schema, invalid_data_bad_format)
