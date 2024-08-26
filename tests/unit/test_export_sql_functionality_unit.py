import pytest
import psycopg2


# Define the fixture for PostgreSQL connection and cursor
@pytest.fixture(scope="module")
def postgres_connection():
    """
    Fixture to set up and tear down a PostgreSQL database connection for testing.
    """
    # Retrieve connection details from environment variables, with defaults for local development
    db_host = "localhost"
    db_user = "postgres"
    db_password = "admin"
    db_name = "syslog"
    db_port = 5432

    # Establish a connection to the PostgreSQL server
    conn = psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        port=db_port
    )
    cursor = conn.cursor()

    # Ensure a clean state before running tests
    cursor.execute("DROP TABLE IF EXISTS syslog")

    yield conn  # Provide the fixture value (connection) to the test function

    # Clean up after tests
    cursor.execute("DROP TABLE IF EXISTS syslog")
    conn.close()


@pytest.fixture(scope="module")
def postgres_cursor(postgres_connection):
    """
    Fixture to provide a cursor for executing SQL queries.
    """
    cursor = postgres_connection.cursor()
    yield cursor
    cursor.close()


def test_create_syslog_table(postgres_cursor):

    # Create the syslog table
    create_syslog_table(postgres_cursor)

    # Verify that the table was created
    postgres_cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'syslog')")
    result = postgres_cursor.fetchone()
    assert result[0]  # Ensure the syslog table exists


def test_syslog_schema_fields(postgres_cursor):
    # Create the syslog table
    create_syslog_table(postgres_cursor)

    postgres_cursor.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'syslog';
        """)
    columns = postgres_cursor.fetchall()
    postgres_cursor.close()

    expected_columns = [
        ('id', 'integer', 'nextval(\'syslog_id_seq\'::regclass)', 'NO'),
        ('timestamp', 'character varying', None, 'NO'),
        ('hostname', 'character varying', None, 'NO'),
        ('process', 'character varying', None, 'NO'),
        ('pid', 'integer', None, 'YES'),  # Allowing NULL
        ('message', 'text', None, 'NO')
    ]

    assert len(columns) == len(expected_columns), "Schema does not have the expected number of columns"
    for col, expected in zip(columns, expected_columns):
        assert col == expected, f"Expected {expected} but got {col}"
