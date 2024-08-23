import argparse

from export_to_json import export_syslog_to_json


def main():
    parser = argparse.ArgumentParser(description="Syslog to JSON export utility")
    subparsers = parser.add_subparsers(dest="command")

    # Export command
    export_parser = subparsers.add_parser('export', help='Export syslog data')
    export_parser.add_argument('format', choices=['json'], help='Export format')
    export_parser.add_argument('input_file', type=str, help='Path to the syslog file')
    export_parser.add_argument('output_file', type=str, help='Path to the output file')

    args = parser.parse_args()

    if args.command == 'export' and args.format == 'json':
        export_syslog_to_json(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
