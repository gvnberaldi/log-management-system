from syslog_manager.utility import parse_syslog_line


def export_syslog_to_sql(syslog_file_path, output_sql_file_path):
    with open(syslog_file_path, 'r') as f:
        syslog_content = f.readlines()

    with open(output_sql_file_path, 'w') as f:
        # Writing the CREATE TABLE statement at the beginning of the file
        f.write("""
                CREATE TABLE IF NOT EXISTS syslog (
                    id SERIAL PRIMARY KEY,
                    timestamp VARCHAR(255) NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    process VARCHAR(255) NOT NULL,
                    pid INTEGER,
                    message TEXT NOT NULL
                );
                """)

        for line in syslog_content:
            parsed_data = parse_syslog_line(line.strip())

            if not parsed_data:
                print(f"Skipping invalid line: {line.strip()}")
                continue

            # Constructing the SQL query based on whether pid is present
            pid_value = parsed_data['pid'] if parsed_data['pid'] else 'NULL'

            # Writing SQL insert statement to the file
            f.write(f"INSERT INTO syslog (timestamp, hostname, process, pid, message) VALUES\n")
            f.write(
                f"('{parsed_data['timestamp'].replace("'", "''")}', "
                f"'{parsed_data['hostname'].replace("'", "''")}', "
                f"'{parsed_data['process'].replace("'", "''")}', "
                f"{pid_value.replace("'", "''")}, "
                f"'{parsed_data['message'].replace("'", "''")}');\n"
            )

    print(f"SQL file successfully written to {output_sql_file_path}")

