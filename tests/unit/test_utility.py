import pytest
import os
import sys
from unittest.mock import mock_open, patch, call

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.utility import parse_syslog_line


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
