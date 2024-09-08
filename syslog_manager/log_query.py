from abc import ABC, abstractmethod
from datetime import datetime
import json
import csv

from syslog_manager.utility import parse_syslog_line


class LogQuery(ABC):
    def __init__(self, input_file, start_date, end_date):
        self.input_file = input_file
        self.start_date = start_date.date()
        self.end_date = end_date.date()
        self.filtered_logs = []

    def query_logs_between_timestamps(self):
        self.parse_file()
        return "\n".join(self.filtered_logs)

    def filter_by_timestamp(self, timestamp_str):
        # Convert the timestamp to a date object
        entry_timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S %Y").date()
        # Check if the entry timestamp is within the specified range
        return self.start_date <= entry_timestamp <= self.end_date

    @abstractmethod
    def parse_file(self):
        pass


class LogFileQuery(LogQuery):
    def __init__(self, input_file, start_date, end_date):
        super().__init__(input_file, start_date, end_date)
        self._parse_syslog_line = parse_syslog_line

    def parse_file(self):
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                entry = self._parse_syslog_line(line)
                if entry and self.filter_by_timestamp(f"{entry['timestamp']} {datetime.now().year}"):
                    self.filtered_logs.append(line.strip())


class JSONFileQuery(LogQuery):
    def parse_file(self):
        with open(self.input_file, 'r') as f:
            data = json.load(f)
            for entry in data:
                timestamp = entry.get('timestamp')
                if timestamp and self.filter_by_timestamp(f"{timestamp} {datetime.now().year}"):
                    self.filtered_logs.append(json.dumps(entry))


class CSVFileQuery(LogQuery):
    def parse_file(self):
        with open(self.input_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp = row.get('timestamp')
                if timestamp and self.filter_by_timestamp(f"{timestamp} {datetime.now().year}"):
                    self.filtered_logs.append(str(row))


# Factory method to instantiate the correct subclass based on the file type
def create_log_query(input_file, start_date, end_date):
    if input_file.suffix == '.log':
        return LogFileQuery(input_file, start_date, end_date)
    elif input_file.suffix == '.json':
        return JSONFileQuery(input_file, start_date, end_date)
    elif input_file.suffix == '.csv':
        return CSVFileQuery(input_file, start_date, end_date)
    else:
        raise ValueError("Unsupported file format. Supported formats are .log, .json, and .csv.")
