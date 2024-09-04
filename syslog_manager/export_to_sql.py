from syslog_manager.utility import parse_syslog_line, create_syslog_table


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
