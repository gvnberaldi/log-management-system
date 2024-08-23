from jsonschema import validate, ValidationError
import json
import re


def create_json_schema():
    # Define the JSON schema
    json_schema = {
        "type": "object",
        "properties": {
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "pattern": "^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{2} \\d{2}:\\d{2}:\\d{2}$",
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
    """
    Validate the provided data against the JSON schema.
    Raises ValueError if the data is invalid.
    """
    try:
        validate(instance=data, schema=json_schema)
    except ValidationError as e:
        raise ValueError(f"Invalid JSON data: {e.message}")


def parse_syslog_line(line):
    syslog_pattern = re.compile(
        r'^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) '
        r'(?P<hostname>\S+) '
        r'(?P<process>\S+?)'
        r'(?:\[(?P<pid>\d+)\])?: '
        r'(?P<message>.*)$'
    )

    match = syslog_pattern.match(line)
    if match:
        return match.groupdict()
    return None


def export_syslog_to_json(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    parsed_data = []
    for line in lines:
        parsed_line = parse_syslog_line(line)
        if parsed_line:
            parsed_line['pid'] = int(parsed_line['pid']) if parsed_line['pid'] else None
            parsed_data.append(parsed_line)

    with open(output_file, 'w') as f:
        json.dump(parsed_data, f, indent=4)
