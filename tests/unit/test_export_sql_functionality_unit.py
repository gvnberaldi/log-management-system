import pytest

from syslog_manager.export_to_sql import *


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


def test_create_syslog_table(postgres_connection, postgres_cursor):

    # Create the syslog table
    create_syslog_table(postgres_connection, postgres_cursor)

    # Verify that the table was created
    postgres_cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'syslog')")
    result = postgres_cursor.fetchone()
    assert result[0]  # Ensure the syslog table exists


def test_syslog_schema_fields(postgres_connection, postgres_cursor):
    # Create the syslog table
    create_syslog_table(postgres_connection, postgres_cursor)

    postgres_cursor.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'syslog';
        """)
    columns = postgres_cursor.fetchall()

    expected_columns = [
        ('id', 'integer', 'nextval(\'syslog_id_seq\'::regclass)', 'NO'),
        ('timestamp', 'character varying', None, 'NO'),
        ('hostname', 'character varying', None, 'NO'),
        ('process', 'character varying', None, 'NO'),
        ('pid', 'integer', None, 'YES'),  # Allowing NULL
        ('message', 'text', None, 'NO')
    ]

    # Convert both actual and expected columns to sets for comparison, ignoring order
    assert set(columns) == set(expected_columns), f"Schema mismatch. Expected: {expected_columns}, Got: {columns}"


def test_export_sql_creates_sql_file(tmp_path, postgres_connection, postgres_cursor):
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_content = """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"""
    syslog_file.write_text(syslog_content)

    export_syslog_to_sql(str(syslog_file), str(output_sql_file), postgres_connection, postgres_cursor)

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

    # Query the database to check if the data is correctly inserted
    postgres_cursor.execute('SELECT timestamp, hostname, process, pid, message FROM syslog')
    result = postgres_cursor.fetchone()

    expected_data = (
        'Jun 14 15:16:01', 'combo', 'sshd(pam_unix)', 19939,
        'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'
    )

    assert result == expected_data


def test_export_sql_ignores_invalid_lines(tmp_path, postgres_connection, postgres_cursor):
    syslog_file = tmp_path / "syslog.log"
    output_sql_file = tmp_path / "syslog.sql"

    syslog_content = """
    Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
    Invalid line without the correct format
    """
    syslog_file.write_text(syslog_content)

    export_syslog_to_sql(str(syslog_file), str(output_sql_file), postgres_connection, postgres_cursor)

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
    print(output_sql_file.read_text().strip())
    print(expected_sql_content.strip())

    # Normalize the whitespace for comparison
    expected_lines = [line.strip() for line in expected_sql_content.strip().splitlines() if line.strip()]
    actual_lines = [line.strip() for line in output_sql_file.read_text().strip().splitlines() if line.strip()]

    assert expected_lines == actual_lines

    # Query the database to check if the data is correctly inserted
    postgres_cursor.execute('SELECT timestamp, hostname, process, pid, message FROM syslog')
    result = postgres_cursor.fetchone()

    expected_data = (
        'Jun 14 15:16:01', 'combo', 'sshd(pam_unix)', 19939,
        'authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4'
    )

    assert result == expected_data
