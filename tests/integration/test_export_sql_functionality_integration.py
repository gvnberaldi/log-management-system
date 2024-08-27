import pytest
import subprocess
from pathlib import Path

from export_to_sql import *


# Define the fixture for PostgreSQL connection and cursor
@pytest.fixture(scope="module")
def postgres_connection():
    """
    Fixture to set up and tear down a PostgreSQL database connection for testing.
    """
    conn = get_db_connection()
    yield conn  # Provide the fixture value (connection) to the test function
    conn.close()


@pytest.fixture(scope="module")
def postgres_cursor(postgres_connection):
    """
    Fixture to provide a cursor for executing SQL queries.
    """
    cursor = get_db_cursor(postgres_connection)
    # Ensure a clean state before running tests
    cursor.execute("DROP TABLE IF EXISTS syslog")
    yield cursor
    # Clean up after tests
    cursor.execute("DROP TABLE IF EXISTS syslog")
    cursor.close()


def test_cli_export_syslog_to_sql(tmp_path, postgres_cursor):
    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.json"

    syslog_file.write_text(syslog_content)

    # Construct the path to the syslog_utils.py file, going two directories up
    script_path = Path(__file__).resolve().parents[2] / "main.py"

    result = subprocess.run(
        ['python', str(script_path), 'export', 'sql', str(syslog_file), str(output_sql_file)],
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
    assert output_sql_file.read_text().strip() == expected_sql_content.strip()

    # Query the database to check if the data is correctly inserted
    postgres_cursor.execute('SELECT timestamp, hostname, process, pid, message FROM syslog')
    result = postgres_cursor.fetchone()

    expected_data = (
        'Jun 14 15:16:01', 'combo', 'sshd(pam_unix)', 19939,
        'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'
    )

    assert result == expected_data
