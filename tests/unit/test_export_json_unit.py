import json
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

from syslog_manager.exporter import JSONSyslogExporter


def test_export_syslog_to_json_creates_json_file(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    # Write sample syslog content to the file
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    json_exporter = JSONSyslogExporter(syslog_file)
    json_exporter.export(output_json_file)

    # Verify the output
    assert output_json_file.exists()

    with output_json_file.open('r') as f:
        data = json.load(f)

    # Example check for specific data
    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": 19939,
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        }
    ]

    assert data == expected_data


def test_export_syslog_to_json_with_multiple_lines(tmp_path):
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:02 combo sshd(pam_unix)[19940]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.5"""
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    syslog_file.write_text(syslog_content)

    json_exporter = JSONSyslogExporter(syslog_file)
    json_exporter.export(output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": 19939,
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        },
        {
            "timestamp": "Jun 14 15:16:02",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": 19940,
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.5"
        }
    ]

    assert data == expected_data


def test_export_syslog_to_json_with_missing_pid(tmp_path):
    syslog_content = "Jun 14 15:16:01 combo sshd(pam_unix): authentication failure"
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    syslog_file.write_text(syslog_content)

    json_exporter = JSONSyslogExporter(syslog_file)
    json_exporter.export(output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": None,
            "message": "authentication failure"
        }
    ]

    assert data == expected_data


def test_export_syslog_to_json_with_empty_file(tmp_path):
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    syslog_file.write_text("")

    json_exporter = JSONSyslogExporter(syslog_file)
    json_exporter.export(output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    assert data == []

