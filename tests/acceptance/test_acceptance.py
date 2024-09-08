import csv
import os
import subprocess
import sys
from pathlib import Path


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


    # Read and parse the CSV file
    with open(output_csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

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


def test_query_by_words_command_log():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the words to search for
    search_words = "failure,Accepted,abnormally"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "log", str(syslog_file), "contains_words", search_words
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_by_process_name_command_log():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the process name
    process_name = "sshd"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "log", str(syslog_file), "from_process", process_name
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_between_timestamp_command_log():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.log"

    # Define the timestamps
    start_date = "14/06/2024"
    end_date = "16/06/2025"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "log", str(syslog_file), "between", start_date, end_date
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_between_timestamp_command_json():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.json"

    # Define the timestamps
    start_date = "14/06/2024"
    end_date = "16/06/2025"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "json", str(syslog_file), "between", start_date, end_date
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the command succeeded
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    # Check if there was any error
    assert result.stderr == ""


def test_query_between_timestamp_command_csv():
    syslog_file = Path(__file__).resolve().parents[2] / "data" / "syslog_data.csv"

    # Define the timestamps
    start_date = "14/06/2024"
    end_date = "16/06/2025"

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "csv", str(syslog_file), "between", start_date, end_date
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
