import plotext as plt
from collections import defaultdict

from syslog_manager.utility import parse_syslog_line


def parse_log_timestamp(timestamp):
    """
    Extracts the hour from a syslog timestamp.
    Assumes the timestamp format is 'Jun 15 02:04:59'
    """
    try:
        month_day_time = timestamp.split(' ')
        hour = int(month_day_time[2].split(':')[0])
        return hour
    except (IndexError, ValueError):
        return None


def count_events_per_hour(log_file_path):
    """
    Counts the number of log events that occur for each hour of the day from a log file.
    """
    hourly_counts = defaultdict(int)

    with open(log_file_path, 'r') as file:
        for line in file:
            parsed_line = parse_syslog_line(line)
            if parsed_line:
                timestamp = parsed_line.get('timestamp')
                hour = parse_log_timestamp(timestamp)
                if hour is not None and 0 <= hour < 24:
                    hourly_counts[hour] += 1

    return hourly_counts


def generate_bar_chart(hourly_counts):
    """
    Generates a bar chart showing event frequency per hour using plotext.
    """
    hours = list(range(24))
    counts = [hourly_counts.get(hour, 0) for hour in hours]

    plt.bar(hours, counts, color='blue', width=0.6)
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Events')
    plt.title('Event Frequency by Hour')
    plt.xticks(hours)
    plt.show()
