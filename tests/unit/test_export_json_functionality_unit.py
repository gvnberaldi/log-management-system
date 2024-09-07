from unittest.mock import mock_open, patch, call

import pytest
import json
from syslog_manager.export_to_json import *
from syslog_manager.utility import create_json_schema, validate_json


def test_export_syslog_to_json():
    # Mock data for the input file
    mock_lines = [
        "Sep 1 12:34:56 myhost process[1234]: Test log message 1\n",
        "Sep 1 12:34:57 myhost process: Test log message 2\n"
    ]

    # Expected parsed data
    mock_parsed_lines = [
        {'timestamp': 'Sep 1 12:34:56', 'hostname': 'myhost', 'process': 'process', 'pid': 1234,
         'message': 'Test log message 1'},
        {'timestamp': 'Sep 1 12:34:57', 'hostname': 'myhost', 'process': 'process', 'pid': None,
         'message': 'Test log message 2'}
    ]

    # Mocked output file content (JSON format)
    expected_output = json.dumps(mock_parsed_lines, indent=4)

    # Mock open, readlines, and parse_syslog_line
    mock_open_func = mock_open(read_data=''.join(mock_lines))

    with patch('builtins.open', mock_open_func), \
            patch('syslog_manager.export_to_json.parse_syslog_line', side_effect=mock_parsed_lines) as mock_parse:
        output_file = "mock_output.json"

        # Call the function under test
        export_syslog_to_json("mock_input.log", output_file)

        # Check that parse_syslog_line was called with the correct input lines
        expected_calls = [call("Sep 1 12:34:56 myhost process[1234]: Test log message 1\n"),
                          call("Sep 1 12:34:57 myhost process: Test log message 2\n")]
        mock_parse.assert_has_calls(expected_calls, any_order=False)

        # Check if open was called with the correct input and output files
        mock_open_func.assert_called_with(output_file, 'w')

        # Ensure data was written in the expected JSON format
        # Get all the write calls and collect the written data
        write_calls = mock_open_func().write.call_args_list
        written_data = ''.join(call.args[0] for call in write_calls)

        # Assert that the final written data matches the expected JSON
        assert written_data == expected_output


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

