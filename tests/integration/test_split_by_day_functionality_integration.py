import subprocess
import sys
from pathlib import Path


def write_syslog_to_temp_file(tmp_path, syslog_data):
    """Helper function to write syslog data to a temporary file."""
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')
    return temp_file


def test_cli_split_command(tmp_path):
    # Create a temporary syslog file with entries spanning multiple days
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
Jun 16 15:18:03 combo systemd[1]: Started Session 1 of user user1.
"""
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Construct the path to the main.py file
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    # Run the split command using subprocess
    result = subprocess.run(
        [
            sys.executable, str(script_path), "split", str(temp_file)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Check if the output files are created and their contents are correct
    output_file_day_1 = tmp_path / 'syslog-2024-06-13.log'
    output_file_day_2 = tmp_path / 'syslog-2024-06-14.log'
    output_file_day_3 = tmp_path / 'syslog-2024-06-15.log'
    output_file_day_4 = tmp_path / 'syslog-2024-06-16.log'

    assert output_file_day_1.exists(), f"{output_file_day_1} should exist"
    assert output_file_day_2.exists(), f"{output_file_day_2} should exist"
    assert output_file_day_3.exists(), f"{output_file_day_3} should exist"
    assert output_file_day_4.exists(), f"{output_file_day_4} should exist"

    with open(output_file_day_1, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert lines[0] == "Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4\n"

    with open(output_file_day_2, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert lines[0] == "Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2\n"
        assert lines[1] == "Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.\n"

    with open(output_file_day_3, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert lines[0] == "Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2\n"

    with open(output_file_day_4, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert lines[0] == "Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.\n"
        assert lines[1] == "Jun 16 15:18:03 combo systemd[1]: Started Session 1 of user user1.\n"

    # Ensure the command ran without errors
    assert result.returncode == 0
    assert result.stderr == ""
