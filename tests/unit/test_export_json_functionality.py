import pytest
import subprocess
import json
from export_to_json import create_json_schema, validate_json


def test_export_syslog_to_json_creates_json_file(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    # Write sample syslog content to the file
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    # Run the function that is being tested
    export_syslog_to_json(syslog_file, output_json_file)

    # Verify the output
    assert output_json_file.exists()

    with output_json_file.open('r') as f:
        data = json.load(f)

    # Define the expected schema
    json_schema = create_json_schema()

    # Validate JSON data against the schema
    for entry in data:
        try:
            validate_json(json_schema, entry)
        except ValueError as e:
            pytest.fail(f"JSON data is invalid: {e}")

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

    export_syslog_to_json(syslog_file, output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    # Define the expected schema
    json_schema = create_json_schema()

    # Validate JSON data against the schema
    for entry in data:
        try:
            validate_json(json_schema, entry)
        except ValueError as e:
            pytest.fail(f"JSON data is invalid: {e}")

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

    export_syslog_to_json(syslog_file, output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    # Define the expected schema
    json_schema = create_json_schema()

    # Validate JSON data against the schema
    for entry in data:
        try:
            validate_json(json_schema, entry)
        except ValueError as e:
            pytest.fail(f"JSON data is invalid: {e}")

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

    export_syslog_to_json(syslog_file, output_json_file)

    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    assert data == []


def test_cli_export_syslog_to_json(tmp_path):
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    syslog_file.write_text(syslog_content)

    result = subprocess.run(
        ['python3', 'main.py', 'export', 'json', str(syslog_file), str(output_json_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert output_json_file.exists()

    with open(output_json_file, 'r') as f:
        data = json.load(f)

    # Define the expected schema
    json_schema = create_json_schema()

    # Validate JSON data against the schema
    for entry in data:
        try:
            validate_json(json_schema, entry)
        except ValueError as e:
            pytest.fail(f"JSON data is invalid: {e}")

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
