import json
import subprocess
from pathlib import Path
import sys


def test_cli_query_process_name_command_log(tmp_path):
    # Create a temporary syslog file
    syslog_data = """\
Jun 13 15:16:01 combo kernel: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
"""

    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')

    # Define the expected output
    expected_output = """\
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
"""

    # Construct the path to the syslog_utils.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "log", str(temp_file), "from_process", "sshd"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the output matches expected
    assert result.stdout.strip() == expected_output.strip()
    assert result.returncode == 0

    # Check if there was any error
    assert result.stderr == ""


def test_cli_query_process_name_command_json(tmp_path):
    # Create a temporary syslog file
    syslog_data = [
        {"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939,
         "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"},
        {"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940,
         "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"},
        {"timestamp": "Jun 14 15:18:03", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 1 of user user1."},
        {"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941,
         "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"},
        {"timestamp": "Jun 16 10:00:00", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 2 of user user2."}
    ]

    temp_file = tmp_path / "syslog.json"
    with open(temp_file, 'w') as f:
        json.dump(syslog_data, f)

    # Define the expected output
        expected_output = """\
{"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939, "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"}
{"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940, "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"}
{"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941, "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"}
"""

    # Construct the path to the syslog_utils.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "json", str(temp_file), "from_process", "sshd"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the output matches expected
    assert result.stdout.strip() == expected_output.strip()
    assert result.returncode == 0

    # Check if there was any error
    assert result.stderr == ""


def test_cli_query_process_name_command_csv(tmp_path):
    # Create a temporary syslog file
    syslog_data = """\
timestamp,hostname,process,pid,message
Jun 13 15:16:01,combo,sshd(pam_unix),19939,"authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
Jun 14 15:17:02,combo,sshd(pam_unix),19940,"Accepted password for user1 from 192.168.0.1 port 22 ssh2"
Jun 14 15:18:03,combo,systemd,1,"Started Session 1 of user user1."
Jun 15 15:19:04,combo,sshd(pam_unix),19941,"Failed password for user1 from 192.168.0.2 port 22 ssh2"
Jun 16 10:00:00,combo,systemd,1,"Started Session 2 of user user2."
"""

    temp_file = tmp_path / "syslog.csv"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')

    # Define the expected output
    expected_output = """\
{'timestamp': 'Jun 13 15:16:01', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19939', 'message': 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'}
{'timestamp': 'Jun 14 15:17:02', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19940', 'message': 'Accepted password for user1 from 192.168.0.1 port 22 ssh2'}
{'timestamp': 'Jun 15 15:19:04', 'hostname': 'combo', 'process': 'sshd(pam_unix)', 'pid': '19941', 'message': 'Failed password for user1 from 192.168.0.2 port 22 ssh2'}
"""

    # Construct the path to the syslog_utils.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "query", "csv", str(temp_file), "from_process", "sshd"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Verify the output matches expected
    assert result.stdout.strip() == expected_output.strip()
    assert result.returncode == 0

    # Check if there was any error
    assert result.stderr == ""
