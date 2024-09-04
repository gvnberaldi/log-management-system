from syslog_manager.utility import parse_syslog_line


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
