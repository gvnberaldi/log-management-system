import subprocess
import sys
from pathlib import Path


def test_cli_event_frequency_bar_chart(tmp_path):
    # Sample syslog content with events across different hours
    syslog_content = """Jun 15 00:01:00 combo sshd(pam_unix)[10001]: some message
Jun 15 01:15:30 combo sshd(pam_unix)[10002]: another message
Jun 15 01:45:10 combo sshd(pam_unix)[10003]: yet another message
Jun 15 02:05:22 combo sshd(pam_unix)[10004]: message here
Jun 15 14:20:43 combo sshd(pam_unix)[10005]: message for 14th hour
Jun 15 14:35:50 combo sshd(pam_unix)[10006]: another message for 14th hour
Jun 15 22:45:01 combo sshd(pam_unix)[10007]: message for 22nd hour
"""

    syslog_file = tmp_path / "syslog.log"
    syslog_file.write_text(syslog_content)

    # Expected output (only numerical part of the chart is checked here)
    expected_counts = {
        0: 1,
        1: 2,
        2: 1,
        14: 2,
        22: 1
    }

    # Run the CLI command to generate the bar chart
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"
    result = subprocess.run(
        [sys.executable, str(script_path), 'hourly_report', str(syslog_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    # Capture the output of the bar chart and verify numerical correctness
    output = result.stdout
    for hour, count in expected_counts.items():
        assert f"{hour:02d}:00" in output
        assert str(count) in output
