import argparse
import os
import sys
from datetime import datetime

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.export_to_json import export_syslog_to_json
from syslog_manager.export_to_sql import *
from syslog_manager.query_between_timestamps import query_syslog_between_timestamps
from syslog_manager.query_by_process import query_by_process
from syslog_manager.query_by_words import query_by_words
from syslog_manager.split_by_day import split_syslog_by_day
from syslog_manager.utility import get_db_connection, get_db_cursor


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

    # 'contains_words' command under 'query'
    contains_words_parser = query_subparsers.add_parser('contains_words', help='Query syslog data for messages containing specific words')
    contains_words_parser.add_argument('words', type=str, help='Comma-separated list of words to search for')

    # Split command
    split_parser = subparsers.add_parser('split', help='Split syslog file by day')
    split_parser.add_argument('input_file', type=str, help='Path to the syslog file')

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
        else:
            parser.print_help()

    elif args.command == 'query':
        if args.query_type == 'between':
            start_date = datetime.strptime(args.start_date, "%d/%m/%Y")
            end_date = datetime.strptime(args.end_date, "%d/%m/%Y")
            query_syslog_between_timestamps(args.input_file, start_date, end_date)
        elif args.query_type == 'from_process':
            query_by_process(args.input_file, args.process_name)
        elif args.query_type == 'contains_words':
            keywords = args.words.split(',')
            query_by_words(args.input_file, keywords)
        else:
            parser.print_help()

    elif args.command == 'split':
        split_syslog_by_day(args.input_file)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

