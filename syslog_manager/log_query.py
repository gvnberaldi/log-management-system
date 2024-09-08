import re
from abc import ABC, abstractmethod
from datetime import datetime
import json
import csv

from syslog_manager.utility import parse_syslog_line


class LogQuery(ABC):
    def __init__(self, input_file):
        self.input_file = input_file
        self.filtered_logs = []

    def _filter_by_timestamp(self, timestamp_str, start_date, end_date):
        # Convert the timestamp to a date object
        entry_timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S %Y").date()
        # Check if the entry timestamp is within the specified range
        return start_date <= entry_timestamp <= end_date

    def _process_name_patter(self, process_name):
        process_name_pattern = re.escape(process_name)
        return re.compile(rf'{process_name_pattern}')

    @abstractmethod
    def query_logs_between_timestamps(self, start_timestamp, end_timestamp):
        pass

    @abstractmethod
    def query_logs_by_process(self, process):
        pass

    @abstractmethod
    def query_logs_by_words(self, keywords):
        pass


class LogFileQuery(LogQuery):
    def __init__(self, input_file):
        super().__init__(input_file)
        self._parse_syslog_line = parse_syslog_line

    def query_logs_between_timestamps(self, start_timestamp, end_timestamp):
        try:
            with open(self.input_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    entry = self._parse_syslog_line(line)
                    if entry and self._filter_by_timestamp(f"{entry['timestamp']} {datetime.now().year}",
                                                           start_timestamp.date(), end_timestamp.date()):
                        self.filtered_logs.append(line.strip())
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_process(self, process):
        pattern = self._process_name_patter(process)
        try:
            with open(self.input_file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parsed_line = self._parse_syslog_line(line)
                    if parsed_line and pattern.match(parsed_line['process']):
                        self.filtered_logs.append(line.strip())
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_words(self, keywords):
        try:
            with open(self.input_file, 'r') as syslog_file:
                for line in syslog_file:
                    parsed_line = self._parse_syslog_line(line)
                    if parsed_line:
                        message = parsed_line['message']
                        if any(keyword in message for keyword in keywords):
                            self.filtered_logs.append(line.strip())
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)


class JSONFileQuery(LogQuery):
    def query_logs_between_timestamps(self, start_timestamp, end_timestamp):
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    timestamp = entry.get('timestamp')
                    if timestamp and self._filter_by_timestamp(f"{timestamp} {datetime.now().year}",
                                                               start_timestamp.date(), end_timestamp.date()):
                        self.filtered_logs.append(json.dumps(entry))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_process(self, process):
        pattern = self._process_name_patter(process)
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if 'process' in entry and pattern.match(entry['process']):
                        self.filtered_logs.append(json.dumps(entry))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_words(self, keywords):
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if 'message' in entry and any(keyword in entry['message'] for keyword in keywords):
                        self.filtered_logs.append(json.dumps(entry))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)


class CSVFileQuery(LogQuery):
    def query_logs_between_timestamps(self, start_timestamp, end_timestamp):
        try:
            with open(self.input_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamp = row.get('timestamp')
                    if timestamp and self._filter_by_timestamp(f"{timestamp} {datetime.now().year}",
                                                              start_timestamp.date(), end_timestamp.date()):
                        self.filtered_logs.append(str(row))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_process(self, process):
        pattern = self._process_name_patter(process)
        try:
            with open(self.input_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'process' in row and pattern.match(row['process']):
                        self.filtered_logs.append(str(row))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)

    def query_logs_by_words(self, keywords):
        try:
            with open(self.input_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'message' in row and any(keyword in row['message'] for keyword in keywords):
                        self.filtered_logs.append(str(row))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_file} does not exist.")
        except IOError as e:
            raise IOError(f"Error reading the file {self.input_file}: {e}")

        return "\n".join(self.filtered_logs)


# Factory method to instantiate the correct subclass based on the file type
def create_log_query(input_file):
    if input_file.suffix == '.log':
        return LogFileQuery(input_file)
    elif input_file.suffix == '.json':
        return JSONFileQuery(input_file)
    elif input_file.suffix == '.csv':
        return CSVFileQuery(input_file)
    else:
        raise ValueError("Unsupported file format. Supported formats are .log, .json, and .csv.")
