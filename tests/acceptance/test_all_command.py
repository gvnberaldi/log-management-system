import csv
import os
import subprocess
import sys

import pytest
from pathlib import Path

from jsonschema.exceptions import ValidationError

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.export_to_json import *
from syslog_manager.utility import create_json_schema, validate_json, create_csv_schema, validate_csv


def test_export_syslog_to_json():
    # Path to the real syslog file in the project directory
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"
    output_json_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.json"

    # Path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the export command
    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'json', str(syslog_file), str(output_json_file)],
        capture_output=True,
        text=True
    )

    # Check if command was successful
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""
    assert output_json_file.exists(), "Output JSON file does not exist"

    # Read and validate the JSON output
    with open(output_json_file, 'r') as f:
        data = json.load(f)

    # Define the expected JSON schema
    json_schema = create_json_schema()

    # Validate JSON data against the schema
    for entry in data:
        try:
            validate_json(json_schema, entry)
        except ValidationError as e:
            pytest.fail(f"JSON data is invalid: {e}")


def test_export_syslog_to_csv(tmp_path):
    # Path to the real syslog file in the project directory
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"
    output_csv_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.csv"

    # Construct the path to the main script (syslog_utils.py)
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Execute the CLI command for CSV export
    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'csv', str(syslog_file), str(output_csv_file)],
        capture_output=True,
        text=True
    )

    # Check if command was successful
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""
    assert output_csv_file.exists(), "Output JSON file does not exist"

    # Validate the CSV against the schema
    csv_schema = create_csv_schema()
    validate_csv(csv_schema, output_csv_file)

    # Read and parse the CSV file
    with open(output_csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Define the expected data from the syslog input
    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": "19939",
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        }
    ]

    # Verify that the rows match the expected output
    assert rows == expected_data

    expected_headers = ["timestamp", "hostname", "process", "pid", "message"]
    assert reader.fieldnames == expected_headers


def test_export_syslog_to_sql():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"
    output_sql_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.sql"

    # Path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the export command
    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'sql', str(syslog_file), str(output_sql_file)],
        capture_output=True,
        text=True
    )

    # Check if command was successful
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""
    assert output_sql_file.exists(), "Output SQL file does not exist"


def test_query_by_words_command():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the words to search for
    search_words = "failure,Accepted,abnormally"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", str(syslog_file), "contains_words", search_words
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_by_process_name_command():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the process name
    process_name = "sshd"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", str(syslog_file), "from_process", process_name
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_between_timestamp_command():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the timestamps
    start_date = "14/06/2024"
    end_date = "16/06/2025"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", str(syslog_file), "between", start_date, end_date
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_split_by_day_command():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "split", str(syslog_file)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""
