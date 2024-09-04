import json
from syslog_manager.utility import parse_syslog_line


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
