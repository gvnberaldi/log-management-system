import re


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


def query_by_words(file_path, keywords):
    filtered_messages = []
    with open(file_path, 'r') as syslog_file:
        for line in syslog_file:
            parsed_line = parse_syslog_line(line)
            if parsed_line:
                message = parsed_line['message']
                if any(keyword in message for keyword in keywords):
                    filtered_messages.append(line.strip())

    # Print each filtered message
    for message in filtered_messages:
        print(message)

    return filtered_messages
