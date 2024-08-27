import os
import sys

import pytest

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the project path relative to the script directory
# For example, if the project path is two directories up from the script:
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))

# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from export_to_json import *


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

