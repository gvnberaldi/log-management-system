import csv

from syslog_manager.utility import parse_syslog_line


def export_syslog_to_csv(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Prepare the data for CSV export
    parsed_data = []
    for line in lines:
        parsed_line = parse_syslog_line(line)
        if parsed_line:
            # Ensure that 'pid' is either an integer or None
            parsed_line['pid'] = int(parsed_line['pid']) if parsed_line['pid'] else None
            parsed_data.append(parsed_line)

    # Define the CSV header
    csv_header = ['timestamp', 'hostname', 'process', 'pid', 'message']

    # Write to CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)

        # Write the header
        writer.writeheader()

        # Write the rows
        for row in parsed_data:
            writer.writerow(row)
