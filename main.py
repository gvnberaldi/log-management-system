import argparse
import sys
from datetime import datetime

from export_to_json import export_syslog_to_json
from export_to_sql import *
from query_between_timestamps import query_syslog_between_timestamps
from query_by_process import query_by_process


def main():
    parser = argparse.ArgumentParser(description="Syslog export utility")
    subparsers = parser.add_subparsers(dest="command")

    # Export command
    export_parser = subparsers.add_parser('export', help='Export syslog data')
    export_parser.add_argument('format', choices=['json', 'sql'], help='Export format')
    export_parser.add_argument('input_file', type=str, help='Path to the syslog file')
    export_parser.add_argument('output_file', type=str, help='Path to the output file')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query syslog data')
    query_parser.add_argument('input_file', type=str, help='Path to the syslog file')
    query_subparsers = query_parser.add_subparsers(dest='query_type')

    # 'between' command under 'query'
    between_parser = query_subparsers.add_parser('between', help='Query syslog data between two timestamps')
    between_parser.add_argument('start_date', type=str, help='Start date (format: DD/MM/YYYY)')
    between_parser.add_argument('end_date', type=str, help='End date (format: DD/MM/YYYY)')

    # 'from_process' command under 'query'
    from_process_parser = query_subparsers.add_parser('from_process', help='Query syslog data from a specific process')
    from_process_parser.add_argument('process_name', type=str, help='Name of the process to filter by')

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
    elif args.command == 'query':
        if args.query_type == 'between':
            start_date = datetime.strptime(args.start_date, "%d/%m/%Y")
            end_date = datetime.strptime(args.end_date, "%d/%m/%Y")
            query_syslog_between_timestamps(args.input_file, start_date, end_date)
        elif args.query_type == 'from_process':
            query_by_process(args.input_file, args.process_name)
        else:
            parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

