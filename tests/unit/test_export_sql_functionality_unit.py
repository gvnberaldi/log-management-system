import os
import sys

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.exporter import SQLSyslogExporter


def test_export_sql_creates_sql_file(tmp_path):
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    sql_exporter = SQLSyslogExporter(syslog_file)
    sql_exporter.export(output_sql_file)

    # Verify the output
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


def test_export_sql_ignores_invalid_lines(tmp_path):
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_content = """
    Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
    Invalid line without the correct format
    """
    syslog_file.write_text(syslog_content)

    sql_exporter = SQLSyslogExporter(syslog_file)
    sql_exporter.export(output_sql_file)

    # Verify the output
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

    print(expected_sql_content)

    # Normalize the whitespace for comparison
    expected_lines = [line.strip() for line in expected_sql_content.strip().splitlines() if line.strip()]
    actual_lines = [line.strip() for line in output_sql_file.read_text().strip().splitlines() if line.strip()]

    assert actual_lines == expected_lines


def test_export_sql_missing_pid(tmp_path):
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix): authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    sql_exporter = SQLSyslogExporter(syslog_file)
    sql_exporter.export(output_sql_file)

    # Verify the output
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
        ('Jun 14 15:16:01', 'combo', 'sshd(pam_unix)', NULL, 'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4');
        """

    # Normalize the whitespace for comparison
    expected_lines = [line.strip() for line in expected_sql_content.strip().splitlines() if line.strip()]
    actual_lines = [line.strip() for line in output_sql_file.read_text().strip().splitlines() if line.strip()]

    assert expected_lines == actual_lines