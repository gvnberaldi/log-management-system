from datetime import datetime
from syslog_manager.utility import parse_syslog_line


def query_syslog_between_timestamps(syslog_file, start_date, end_date):
    # Convert string dates to datetime.date objects
    start_date = start_date.date()
    end_date = end_date.date()
    filtered_logs = []
    with open(syslog_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            entry = parse_syslog_line(line)
            if entry:
                # Construct the full timestamp string with the current year
                full_timestamp_str = f"{entry['timestamp']} {datetime.now().year}"
                entry_timestamp = datetime.strptime(full_timestamp_str, "%b %d %H:%M:%S %Y").date()
                if start_date <= entry_timestamp <= end_date:
                    filtered_logs.append(line.strip())

    # Output to stdout
    if filtered_logs:
        print("\n".join(filtered_logs))

    # Return the result
    return "\n".join(filtered_logs)
