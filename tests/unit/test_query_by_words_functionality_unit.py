import json

import pytest
import os
import sys

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the project path relative to the script directory
project_path = os.path.abspath(os.path.join(script_dir, '..', '..'))
# Add the project path to sys.path
if project_path not in sys.path:
    sys.path.append(project_path)

from syslog_manager.log_query import create_log_query


@pytest.fixture
def sample_syslog_data():
    return """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:02 combo sshd(pam_unix)[19940]: Accepted password for root from 218.188.2.4 port 22 ssh2
Jun 14 15:16:03 combo sshd(pam_unix)[19941]: Failed password for invalid user admin from 218.188.2.4 port 22 ssh2"""


def test_single_keyword_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["failure"])

    assert "authentication failure" in result


def test_multiple_keywords_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)
    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["failure", "Accepted", "password"])

    assert "authentication failure" in result
    assert "Accepted password" in result
    assert "Failed password" in result


def test_no_keywords_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["nonexistent"])

    assert len(result) == 0
    assert result == ""


def test_empty_keywords_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words([])

    assert len(result) == 0
    assert result == ""


def test_common_word_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["password"])

    assert "Accepted password" in result
    assert "Failed password" in result


def test_message_with_multiple_keywords_log(tmp_path, sample_syslog_data):
    temp_file = tmp_path / "syslog_data.log"
    temp_file.write_text(sample_syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["invalid", "admin"])
    assert all(word in result for word in ["invalid", "admin"])


def test_single_keyword_json(tmp_path, sample_syslog_data):
    syslog_data = [
        {"timestamp": "Jun 13 15:16:01", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19939,
         "message": "authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"},
        {"timestamp": "Jun 14 15:17:02", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19940,
         "message": "Accepted password for user1 from 192.168.0.1 port 22 ssh2"},
        {"timestamp": "Jun 14 15:18:03", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 1 of user user1."},
        {"timestamp": "Jun 15 15:19:04", "hostname": "combo", "process": "sshd(pam_unix)", "pid": 19941,
         "message": "Failed password for user1 from 192.168.0.2 port 22 ssh2"},
        {"timestamp": "Jun 16 10:00:00", "hostname": "combo", "process": "systemd", "pid": 1,
         "message": "Started Session 2 of user user2."}
    ]

    temp_file = tmp_path / "syslog_data.json"
    with open(temp_file, 'w') as f:
        json.dump(syslog_data, f)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["failure"])

    assert "authentication failure" in result


def test_single_keyword_csv(tmp_path, sample_syslog_data):
    syslog_data = """\
timestamp,hostname,process,pid,message
Jun 13 15:16:01,combo,sshd(pam_unix),19939,"authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4"
Jun 14 15:17:02,combo,sshd(pam_unix),19940,"Accepted password for user1 from 192.168.0.1 port 22 ssh2"
Jun 14 15:18:03,combo,systemd,1,"Started Session 1 of user user1."
Jun 15 15:19:04,combo,sshd(pam_unix),19941,"Failed password for user1 from 192.168.0.2 port 22 ssh2"
Jun 16 10:00:00,combo,systemd,1,"Started Session 2 of user user2."
"""

    temp_file = tmp_path / "syslog_data.csv"
    temp_file.write_text(syslog_data)

    log_query = create_log_query(temp_file)
    result = log_query.query_logs_by_words(["failure"])

    assert "authentication failure" in result
