from collections import defaultdict

from syslog_manager.utility import parse_syslog_line


def count_event_per_process(syslog_file):

    num_event = defaultdict(lambda: 0)
    with open(syslog_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parsed_line = parse_syslog_line(line)
            if parsed_line:
                num_event[parsed_line['process']] += 1

    return num_event
