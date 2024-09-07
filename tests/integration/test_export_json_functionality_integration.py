import json
import sys
import subprocess
from pathlib import Path


def test_cli_export_syslog_to_json(tmp_path):
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file = tmp_path / "syslog.log"
    output_json_file = tmp_path / "syslog.json"

    syslog_file.write_text(syslog_content)

    # Construct the path to the syslog_utils.py file, going two directories up
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'json', str(syslog_file), str(output_json_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
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
        }
    ]

    assert data == expected_data