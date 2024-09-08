import sys
import subprocess
from pathlib import Path


def test_cli_export_syslog_to_sql(tmp_path):
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_file.write_text(syslog_content)

    # Construct the path to the syslog_utils.py file, going two directories up
    script_path = Path(__file__).resolve().parents[2] / "syslog_manager" / "main.py"

    result = subprocess.run(
        [sys.executable, str(script_path), 'export', 'sql', str(syslog_file), str(output_sql_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert output_sql_file.exists()

    # The SQL file should contain the correct CREATE TABLE and INSERT statements
    expected_sql_content = """\
                CREATE TABLE IF NOT EXISTS syslog (
                    id SERIAL PRIMARY KEY,
                    timestamp VARCHAR(255) NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    process VARCHAR(255) NOT NULL,
                    pid INTEGER,
                    message TEXT NOT NULL
                );

                INSERT INTO syslog (timestamp, hostname, process, pid, message) VALUES
                ('Jun 14 15:16:01', 'combo', 'sshd(pam_unix)', 19939, 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4');
                """

    # Normalize the whitespace for comparison
    expected_lines = [line.strip() for line in expected_sql_content.strip().splitlines() if line.strip()]
    actual_lines = [line.strip() for line in output_sql_file.read_text().strip().splitlines() if line.strip()]

    assert expected_lines == actual_lines
