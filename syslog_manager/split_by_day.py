import os
from datetime import datetime

from syslog_manager.utility import parse_syslog_line


def split_syslog_by_day(file_path):
    """Splits the syslog file by day into separate files."""
    logs_by_day = {}

    with open(file_path, 'r') as file:
        for line in file:
            entry = parse_syslog_line(line)
            if entry:
                # Construct the full timestamp string with the current year
                full_timestamp_str = f"{entry['timestamp']} {datetime.now().year}"
                log_date = datetime.strptime(full_timestamp_str, "%b %d %H:%M:%S %Y").date()
                log_date_str = log_date.strftime('%Y-%m-%d')

                # Store the log line under the correct date
                if log_date_str not in logs_by_day:
                    logs_by_day[log_date_str] = []
                logs_by_day[log_date_str].append(line)

    # Write logs to separate files by day
    output_dir = os.path.dirname(file_path)

    for log_date_str, logs in logs_by_day.items():
        output_file = os.path.join(output_dir, f'syslog-{log_date_str}.log')
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.writelines(logs)
