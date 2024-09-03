import re

import psycopg2

import threading

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


def parse_syslog_line(line):
    match = re.match(
        r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+) (?P<hostname>\w+) (?P<process>[^\[]+)(\[(?P<pid>\d+)\])?: (?P<message>.+)',
        line
    )
    if match:
        return {
            'timestamp': match.group('timestamp'),
            'hostname': match.group('hostname'),
            'process': match.group('process').strip(),
            'pid': int(match.group('pid')) if match.group('pid') else None,
            'message': match.group('message').strip()
        }
    return None


def export_syslog_to_sql(syslog_file_path, output_sql_file_path, conn, cursor):
    create_syslog_table(conn, cursor, output_sql_file_path)

    with open(syslog_file_path, 'r') as f:
        syslog_content = f.readlines()

    with open(output_sql_file_path, 'a') as f:
        for line in syslog_content:
            parsed_data = parse_syslog_line(line.strip())

            if not parsed_data:
                print(f"Skipping invalid line: {line.strip()}")
                continue

            # Constructing the SQL query with parameters to avoid syntax issues
            insert_query = """
            INSERT INTO syslog (timestamp, hostname, process, pid, message) VALUES
            (%s, %s, %s, %s, %s);
            """
            values = (
                parsed_data['timestamp'],
                parsed_data['hostname'],
                parsed_data['process'],
                parsed_data['pid'],
                parsed_data['message']
            )
            # Constructing the SQL query based on whether pid is present
            pid_value = parsed_data['pid'] if parsed_data['pid'] is not None else 'NULL'
            try:
                f.write(f"INSERT INTO syslog (timestamp, hostname, process, pid, message) VALUES\n")
                f.write(
                    f"('{parsed_data['timestamp'].replace('\'', '\'\'')}', '{parsed_data['hostname'].replace('\'', '\'\'')}', '{parsed_data['process'].replace('\'', '\'\'')}', {pid_value}, '{parsed_data['message'].replace('\'', '\'\'')}');\n")
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"An error occurred while inserting data: {e}")
                conn.rollback()
                continue

    conn.commit()
