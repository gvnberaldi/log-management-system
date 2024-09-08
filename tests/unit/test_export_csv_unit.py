import csv
import os
import sys

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.exporter import CSVSyslogExporter


def test_export_syslog_to_csv_creates_csv_file(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_csv_file = tmp_path / "syslog.csv"

    # Write sample syslog content to the file
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    # Run the function that is being tested
    csv_exporter = CSVSyslogExporter(syslog_file)
    csv_exporter.export(output_csv_file)

    # Verify the output CSV file exists
    assert output_csv_file.exists()

    # Open and read the generated CSV file
    with output_csv_file.open('r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Define expected data in the CSV file
    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": "19939",  # In CSV, pid would be stored as a string initially
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        }
    ]

    # Verify that the CSV data matches the expected output
    assert rows == expected_data

    expected_headers = ["timestamp", "hostname", "process", "pid", "message"]
    assert reader.fieldnames == expected_headers


def test_export_syslog_to_csv_multiple_lines(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_csv_file = tmp_path / "syslog.csv"

    # Write multiple sample syslog content to the file
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:02 combo systemd[1]: Started Session 3 of user root.
Jun 14 15:16:03 combo kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:0c:29:68:22:3c:00:0c:29:68:22:5c:08:00 SRC=192.168.0.10 DST=192.168.0.1"""
    syslog_file.write_text(syslog_content)

    # Run the function that is being tested
    csv_exporter = CSVSyslogExporter(syslog_file)
    csv_exporter.export(output_csv_file)

    # Verify the output CSV file exists
    assert output_csv_file.exists()

    # Open and read the generated CSV file
    with output_csv_file.open('r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Define expected data in the CSV file
    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": "19939",
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        },
        {
            "timestamp": "Jun 14 15:16:02",
            "hostname": "combo",
            "process": "systemd",
            "pid": "1",
            "message": "Started Session 3 of user root."
        },
        {
            "timestamp": "Jun 14 15:16:03",
            "hostname": "combo",
            "process": "kernel",
            "pid": '',
            "message": "[UFW BLOCK] IN=eth0 OUT= MAC=00:0c:29:68:22:3c:00:0c:29:68:22:5c:08:00 SRC=192.168.0.10 DST=192.168.0.1"
        }
    ]

    # Verify that the CSV data matches the expected output
    assert rows == expected_data

    expected_headers = ["timestamp", "hostname", "process", "pid", "message"]
    assert reader.fieldnames == expected_headers


def test_export_syslog_to_csv_missing_pid(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_csv_file = tmp_path / "syslog.csv"

    # Write sample syslog content with missing PID to the file
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix): authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    # Run the function that is being tested
    csv_exporter = CSVSyslogExporter(syslog_file)
    csv_exporter.export(output_csv_file)

    # Verify the output CSV file exists
    assert output_csv_file.exists()

    # Open and read the generated CSV file
    with output_csv_file.open('r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Define expected data in the CSV file
    expected_data = [
        {
            "timestamp": "Jun 14 15:16:01",
            "hostname": "combo",
            "process": "sshd(pam_unix)",
            "pid": '',
            "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
        }
    ]

    # Verify that the CSV data matches the expected output
    assert rows == expected_data

    expected_headers = ["timestamp", "hostname", "process", "pid", "message"]
    assert reader.fieldnames == expected_headers


def test_export_syslog_to_csv_empty_file(tmp_path):
    # Create file paths using Path
    syslog_file = tmp_path / "syslog.log"
    output_csv_file = tmp_path / "syslog.csv"

    # Create an empty syslog file
    syslog_file.write_text("")

    # Run the function that is being tested
    csv_exporter = CSVSyslogExporter(syslog_file)
    csv_exporter.export(output_csv_file)

    # Verify the output CSV file exists
    assert output_csv_file.exists()

    # Open and read the generated CSV file
    with output_csv_file.open('r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Since the input file is empty, the CSV should have no rows
    assert rows == []

    # Verify the CSV file contains only the header
    expected_headers = ["timestamp", "hostname", "process", "pid", "message"]
    assert reader.fieldnames == expected_headers


