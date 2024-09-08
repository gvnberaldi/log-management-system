import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.split_by_day import split_syslog_by_day
from syslog_manager.count_event_per_process import count_event_per_process
from syslog_manager.exporter import JSONSyslogExporter, CSVSyslogExporter, SQLSyslogExporter
from syslog_manager.log_query import create_log_query


def main():
    parser = argparse.ArgumentParser(description="Syslog export utility")
    subparsers = parser.add_subparsers(dest="command")

    # Export command
    export_parser = subparsers.add_parser('export', help='Export syslog data')
    export_parser.add_argument('format', choices=['json', 'csv', 'sql'], help='Export format')
    export_parser.add_argument('input_file', type=str, help='Path to the syslog file')
    export_parser.add_argument('output_file', type=str, help='Path to the output file')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query syslog data')
    query_parser.add_argument('file_format', type=str, choices=['log', 'json', 'csv'],
                              help='Input file format (log, json, csv)')
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

    # Print number of event for each process
    events_counter = subparsers.add_parser('count_event_per_process', help='Export syslog data')
    events_counter.add_argument('input_file', type=str, help='Path to the syslog file')

    args = parser.parse_args()

    if args.command == 'export':
        input_file_extension = args.input_file.split('.')[-1]
        output_file_extension = args.output_file.split('.')[-1]
        if input_file_extension != 'log':
            raise ValueError(f"Input file format not supported: Expected .log, got {input_file_extension}")
        if output_file_extension != args.format:
            raise ValueError(f"File format mismatch: Expected {args.file_format}, got {output_file_extension}")
        if args.format == 'json':
            json_exporter = JSONSyslogExporter(args.input_file)
            json_exporter.export(args.output_file)
        elif args.format == 'csv':
            csv_exporter = CSVSyslogExporter(args.input_file)
            csv_exporter.export(args.output_file)
        elif args.format == 'sql':
            sql_exporter = SQLSyslogExporter(args.input_file)
            sql_exporter.export(args.output_file)
        else:
            parser.print_help()

    elif args.command == 'query':
        file_extension = args.input_file.split('.')[-1]
        # Check if the file extension matches the specified file format
        if file_extension != args.file_format:
            raise ValueError(f"File format mismatch: Expected {args.file_format}, got {file_extension}")
        if args.query_type == 'between':
            start_date = datetime.strptime(args.start_date, "%d/%m/%Y")
            end_date = datetime.strptime(args.end_date, "%d/%m/%Y")
            # Call the log query function based on the format
            log_query = create_log_query(Path(args.input_file))
            result = log_query.query_logs_between_timestamps(start_date, end_date)
            print(result)
        elif args.query_type == 'from_process':
            log_query = create_log_query(Path(args.input_file))
            result = log_query.query_logs_by_process(args.process_name)
            print(result)
        elif args.query_type == 'contains_words':
            keywords = args.words.split(',')
            # Call the log query function based on the format
            log_query = create_log_query(Path(args.input_file))
            result = log_query.query_logs_by_words(keywords)
            print(result)
        else:
            parser.print_help()

    elif args.command == 'split':
        input_file_extension = args.input_file.split('.')[-1]
        if input_file_extension != 'log':
            raise ValueError(f"Input file format not supported: Expected .log, got {input_file_extension}")
        split_syslog_by_day(args.input_file)

    elif args.command == 'count_event_per_process':
        input_file_extension = args.input_file.split('.')[-1]
        if input_file_extension != 'log':
            raise ValueError(f"Input file format not supported: Expected .log, got {input_file_extension}")
        num_event = count_event_per_process(args.input_file)
        for process, num_events in num_event.items():
            print(f'Events for process {process}: {num_events}')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

