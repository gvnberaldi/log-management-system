import re
from jsonschema import validate, ValidationError
from pycsvschema.checker import Validator


def parse_syslog_line(line):
    syslog_pattern = re.compile(
        r'^(?P<timestamp>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}) '
        r'(?P<hostname>\S+) '
        r'(?P<process>\S+?)'
        r'(?:\[(?P<pid>\d+)\])?: '
        r'(?P<message>.*)$'
    )

    match = syslog_pattern.match(line)
    if match:
        return match.groupdict()
    return None


def create_json_schema():
    # Define the JSON schema
    json_schema = {
        "type": "object",
        "properties": {
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "pattern": "^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{1,2}\\s+\\d{2}:\\d{2}:\\d{2}$",
                "description": "The date and time when the log was created"
            },
            "hostname": {
                "type": "string",
                "description": "The name of the machine that generated the log"
            },
            "process": {
                "type": "string",
                "description": "The process that generated the log"
            },
            "pid": {
                "type": ["integer", "null"],
                "description": "The process ID (optional)"
            },
            "message": {
                "type": "string",
                "description": "The actual log message"
            }
        },
        "required": ["timestamp", "hostname", "process", "message"]
    }
    return json_schema


def validate_json(json_schema, data):
    try:
        validate(instance=data, schema=json_schema)
    except ValidationError as e:
        raise ValueError(f"Invalid JSON data: {e.message}")


def create_csv_schema():
    schema = {
        'fields': [
            {
                'name': 'timestamp', 'type': 'string', 'required': True,
                'pattern': "^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{1,2}\\s+\\d{2}:\\d{2}:\\d{2}$",
            },
            {'name': 'hostname', 'type': 'string', 'required': True},
            {'name': 'process', 'type': 'string', 'required': True},
            {'name': 'pid', 'type': 'number', 'required': True, 'nullable': True},
            {'name': 'message', 'type': 'string', 'required': True}
        ]
    }
    return schema


def validate_csv(csv_schema, data):
    v = Validator(csvfile=data, schema=csv_schema)
    try:
        v.validate()
    except ValidationError as e:
        raise ValueError(f"Invalid CSV data: {e.message}")
