import psycopg2


def get_db_connection():
    db_host = "localhost"
    db_user = "postgres"
    db_password = "admin"
    db_name = "syslog"
    db_port = 5432

    # Establishes a connection to the PostgreSQL database and returns the connection object.
    try:
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            dbname=db_name,
            port=db_port
        )
        return conn
    except Exception as e:
        print(f"Unable to connect to the database: {e}")
        raise


def get_db_cursor(conn):
    # Returns a cursor object from the given database connection.
    return conn.cursor()


def create_syslog_table(conn, cursor):
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
        print("Syslog table created successfully (if it didn't already exist).")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
