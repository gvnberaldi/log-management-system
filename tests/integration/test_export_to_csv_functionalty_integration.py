import subprocess
import sys
from pathlib import Path
import csv

from syslog_manager.utility import validate_csv, create_csv_schema


def test_cli_export_syslog_to_csv(tmp_path):
    # Sample syslog content
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""

    # Paths for the input syslog file and the output CSV file
    syslog_file = tmp_path / "syslog.log"
    output_csv_file = tmp_path / "syslog.csv"

    # Write the syslog content to the input file
    syslog_file.write_text(syslog_content)

    # Construct the path to the main script (syslog_utils.py)
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Execute the CLI command for CSV export
    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'csv', str(syslog_file), str(output_csv_file)],
        capture_output=True,
        text=True
    )

    # Ensure the command ran successfully
    assert result.returncode == 0

    # Check that the output CSV file was created
    assert output_csv_file.exists()

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
