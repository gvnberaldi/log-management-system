import argparse

from export_to_json import export_syslog_to_json
from export_to_sql import *


def main():
    parser = argparse.ArgumentParser(description="Syslog export utility")
    subparsers = parser.add_subparsers(dest="command")

    # Export command
    export_parser = subparsers.add_parser('export', help='Export syslog data')
    export_parser.add_argument('format', choices=['json', 'sql'], help='Export format')
    export_parser.add_argument('input_file', type=str, help='Path to the syslog file')
    export_parser.add_argument('output_file', type=str, help='Path to the output file')

    args = parser.parse_args()

    if args.command == 'export':
        if args.format == 'json':
            export_syslog_to_json(args.input_file, args.output_file)
        elif args.format == 'sql':
            # Establish a database connection
            connection = get_db_connection()
            cursor = get_db_cursor(connection)

            try:
                export_syslog_to_sql(args.input_file, args.output_file, connection, cursor)
            finally:
                cursor.close()
                connection.close()


if __name__ == "__main__":
    main()

