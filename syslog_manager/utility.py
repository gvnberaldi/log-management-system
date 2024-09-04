import re
import psycopg2
import threading

from jsonschema import validate, ValidationError


def parse_syslog_line(line):
    syslog_pattern = re.compile(
        r'^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) '
        r'(?P<hostname>\S+) '
        r'(?P<process>\S+?)'
        r'(?:\[(?P<pid>\d+)\])?: '
        r'(?P<message>.*)$'
    )

    match = syslog_pattern.match(line)
    if match:
        return match.groupdict()
    return None


def create_json_schema():
    # Define the JSON schema
    json_schema = {
        "type": "object",
        "properties": {
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "pattern": "^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{2} \\d{2}:\\d{2}:\\d{2}$",
                "description": "The date and time when the log was created"
            },
            "hostname": {
                "type": "string",
                "description": "The name of the machine that generated the log"
            },
            "process": {
                "type": "string",
                "description": "The process that generated the log"
            },
            "pid": {
                "type": ["integer", "null"],
                "description": "The process ID (optional)"
            },
            "message": {
                "type": "string",
                "description": "The actual log message"
            }
        },
        "required": ["timestamp", "hostname", "process", "message"]
    }
    return json_schema


def validate_json(json_schema, data):
    """
    Validate the provided data against the JSON schema.
    Raises ValueError if the data is invalid.
    """
    try:
        validate(instance=data, schema=json_schema)
    except ValidationError as e:
        raise ValueError(f"Invalid JSON data: {e.message}")


# Singleton pattern for managing the database connection
class DBConnectionManager:
    _connection = None
    _lock = threading.Lock()

    @staticmethod
    def get_connection():
        with DBConnectionManager._lock:
            if DBConnectionManager._connection is None:
                try:
                    DBConnectionManager._connection = psycopg2.connect(
                        host="localhost",
                        user="postgres",
                        password="admin",
                        dbname="syslog",
                        port=5432
                    )
                except Exception as e:
                    print(f"Unable to connect to the database: {e}")
                    raise
            return DBConnectionManager._connection


def get_db_connection():
    return DBConnectionManager.get_connection()


def get_db_cursor(conn):
    return conn.cursor()


def create_syslog_table(conn, cursor, output_sql_file=None):
    # Creates the syslog table in the PostgreSQL database with the appropriate schema.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS syslog (
        id SERIAL PRIMARY KEY,
        timestamp VARCHAR(255) NOT NULL,
        hostname VARCHAR(255) NOT NULL,
        process VARCHAR(255) NOT NULL,
        pid INTEGER,
        message TEXT NOT NULL
    );
    """

    try:
        # Get a cursor object to interact with the database
        # Ensure a clean state
        cursor.execute("DROP TABLE IF EXISTS syslog")
        # Create the syslog table
        cursor.execute(create_table_query)
        # Commit the transaction to the database
        conn.commit()

        if output_sql_file:
            with open(output_sql_file, 'w') as f:
                f.write(create_table_query.strip() + "\n")

        print("Syslog table created successfully (if it didn't already exist).")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
