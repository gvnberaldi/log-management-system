import pytest


def write_syslog_to_temp_file(tmp_path, syslog_data):
    """Helper function to write syslog data to a temporary file."""
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')
    return temp_file


@pytest.fixture
def sample_syslog_data():
    return """Jun 14 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:16:02 combo sshd(pam_unix)[19940]: Accepted password for root from 218.188.2.4 port 22 ssh2
Jun 14 15:16:03 combo sshd(pam_unix)[19941]: Failed password for invalid user admin from 218.188.2.4 port 22 ssh2"""


def test_single_keyword(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, ["failure"])
    assert len(result) == 1
    assert "authentication failure" in result[0]


def test_multiple_keywords(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, ["failure", "Accepted", "password"])
    assert len(result) == 3
    assert "authentication failure" in result[0]
    assert "Accepted password" in result[1]
    assert "Failed password" in result[2]


def test_no_keywords(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, ["nonexistent"])
    assert len(result) == 0


def test_empty_keywords(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, [])
    assert len(result) == 0


def test_common_word(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, ["password"])
    assert len(result) == 2
    assert "Accepted password" in result[0]
    assert "Failed password" in result[1]


def test_message_with_multiple_keywords(tmp_path, sample_syslog_data):
    temp_file = write_syslog_to_temp_file(tmp_path, sample_syslog_data)
    result = query_by_words(temp_file, ["invalid", "user", "admin"])
    assert len(result) == 1
    assert ["invalid", "user", "admin"] in result[0]
