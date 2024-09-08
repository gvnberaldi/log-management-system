import csv
import json
from abc import ABC, abstractmethod

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from pycsvschema.checker import Validator

from syslog_manager.utility import parse_syslog_line


class SyslogExporter(ABC):
    def __init__(self, input_file):
        self.input_file = input_file
        self.parsed_data = []
        self._parse_syslog_line = parse_syslog_line
        self._read_and_parse_syslog()

    def _read_and_parse_syslog(self):
        with open(self.input_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parsed_line = self._parse_syslog_line(line.strip())
            if parsed_line:
                parsed_line['pid'] = int(parsed_line['pid']) if parsed_line['pid'] else None
                self.parsed_data.append(parsed_line)

    @abstractmethod
    def export(self, output_file):
        pass


class JSONSyslogExporter(SyslogExporter):
    def _create_schema(self):
        return {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time",
                              "pattern": "^[A-Za-z]{3}\\s+\\d{1,2}\\s+\\d{2}:\\d{2}:\\d{2}$"
                },
                "hostname": {"type": "string"},
                "process": {"type": "string"},
                "pid": {"type": ["integer", "null"]},
                "message": {"type": "string"}
            },
            "required": ["timestamp", "hostname", "process", "message"]
        }

    def _validate_data(self, file=None):
        schema = self._create_schema()
        for data in self.parsed_data:
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                raise ValueError(f"Invalid JSON data: {e.message}")

    def export(self, output_file):
        self._validate_data()
        with open(output_file, 'w') as f:
            json.dump(self.parsed_data, f, indent=4)


class CSVSyslogExporter(SyslogExporter):
    def _create_schema(self):
        return {
            'fields': [
                {
                    'name': 'timestamp', 'type': 'string', 'required': True,
                    'pattern': "^[A-Za-z]{3}\\s+\\d{1,2}\\s+\\d{2}:\\d{2}:\\d{2}$"
                },
                {'name': 'hostname', 'type': 'string', 'required': True},
                {'name': 'process', 'type': 'string', 'required': True},
                {'name': 'pid', 'type': 'number', 'required': False, 'nullable': True},
                {'name': 'message', 'type': 'string', 'required': True}
            ]
        }

    def _validate_data(self, file=None):
        schema = self._create_schema()
        v = Validator(csvfile=file, schema=schema)
        try:
            v.validate()
        except ValidationError as e:
            raise ValueError(f"Invalid CSV data: {e.message}")

    def export(self, output_file):
        csv_header = ['timestamp', 'hostname', 'process', 'pid', 'message']

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()
            writer.writerows(self.parsed_data)

        self._validate_data(output_file)


class SQLSyslogExporter(SyslogExporter):
    def export(self, output_file):
        with open(output_file, 'w') as f:
            f.write("""
                CREATE TABLE IF NOT EXISTS syslog (
                    id SERIAL PRIMARY KEY,
                    timestamp VARCHAR(255) NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    process VARCHAR(255) NOT NULL,
                    pid INTEGER,
                    message TEXT NOT NULL
                );
                """)
            for row in self.parsed_data:
                pid_value = row['pid'] if row['pid'] else 'NULL'
                f.write(f"INSERT INTO syslog (timestamp, hostname, process, pid, message) VALUES\n")
                f.write(
                    f"('{row['timestamp'].replace("'", "''")}', "
                    f"'{row['hostname'].replace("'", "''")}', "
                    f"'{row['process'].replace("'", "''")}', "
                    f"{pid_value}, "
                    f"'{row['message'].replace("'", "''")}');\n"
                )
