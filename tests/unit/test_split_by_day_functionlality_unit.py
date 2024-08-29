
def write_syslog_to_temp_file(tmp_path, syslog_data):
    """Helper function to write syslog data to a temporary file."""
    temp_file = tmp_path / "syslog.log"
    temp_file.write_text(syslog_data, encoding='utf-8', newline='')
    return temp_file


def test_split_syslog_by_day(tmp_path):
    # Sample syslog data spanning two days
    syslog_data = """\
Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4
Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2
Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.
Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2
Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.
Jun 16 15:18:03 combo systemd[1]: Started Session 1 of user user1.
"""

    # Write the syslog data to a temporary file using the helper function
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Run the splitter function
    split_syslog_by_day(temp_file)

    # Verify that the correct output files were created
    output_file_day_1 = tmp_path / 'syslog-2023-06-13.log'
    output_file_day_2 = tmp_path / 'syslog-2023-06-14.log'
    output_file_day_3 = tmp_path / 'syslog-2023-06-15.log'
    output_file_day_4 = tmp_path / 'syslog-2023-06-16.log'

    assert output_file_day_1.exists(), f"{output_file_day_1} should exist"
    assert output_file_day_2.exists(), f"{output_file_day_2} should exist"
    assert output_file_day_3.exists(), f"{output_file_day_3} should exist"
    assert output_file_day_4.exists(), f"{output_file_day_4} should exist"

    # Check contents of the logs file
    with open(output_file_day_1, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # Two log entries for June 14th
        assert lines[0] == "Jun 13 15:16:01 combo sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4\n"

    with open(output_file_day_2, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2  # Two log entries for June 14th
        assert lines[0] == "Jun 14 15:17:02 combo sshd(pam_unix)[19940]: Accepted password for user1 from 192.168.0.1 port 22 ssh2\n"
        assert lines[1] == "Jun 14 15:18:03 combo systemd[1]: Started Session 1 of user user1.\n"

    with open(output_file_day_3, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # One log entry for June 15th
        assert lines[0] == "Jun 15 15:19:04 combo sshd(pam_unix)[19941]: Failed password for user1 from 192.168.0.2 port 22 ssh2\n"

    with open(output_file_day_4, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2  # Two log entries for June 14th
        assert lines[0] == "Jun 16 10:00:00 combo systemd[1]: Started Session 2 of user user2.\n"
        assert lines[1] == "Jun 16 15:18:03 combo systemd[1]: Started Session 1 of user user1.\n"


def test_split_syslog_empty_file(tmp_path):
    # Empty syslog data
    syslog_data = ""

    # Write the syslog data to a temporary file using the helper function
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Run the splitter function
    split_syslog_by_day(temp_file)

    # Verify that no output files are created
    output_files = list(tmp_path.glob('syslog-*.log'))
    assert len(output_files) == 0, "No output files should be created for an empty syslog"


def test_split_syslog_across_months(tmp_path):
    # Syslog data spanning across two months
    syslog_data = """\
Jun 30 23:59:59 combo sshd(pam_unix)[10000]: Log entry at the end of June
Jul 01 00:00:01 combo sshd(pam_unix)[10001]: Log entry at the start of July
Jul 01 12:34:56 combo sshd(pam_unix)[10002]: Another July log entry
"""

    # Write the syslog data to a temporary file using the helper function
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Run the splitter function
    split_syslog_by_day(temp_file)

    # Verify that two output files are created, one for each month
    output_file_jun_30 = tmp_path / 'syslog-2023-06-30.log'
    output_file_jul_01 = tmp_path / 'syslog-2023-07-01.log'

    assert output_file_jun_30.exists(), f"{output_file_jun_30} should exist"
    assert output_file_jul_01.exists(), f"{output_file_jul_01} should exist"

    # Check contents of the June 30 log file
    with open(output_file_jun_30, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # One log entry for June 30th
        assert lines[0] == "Jun 30 23:59:59 combo sshd(pam_unix)[10000]: Log entry at the end of June\n"

    # Check contents of the July 01 log file
    with open(output_file_jul_01, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2  # Two log entries for July 1st
        assert lines[0] == "Jul 01 00:00:01 combo sshd(pam_unix)[10001]: Log entry at the start of July\n"
        assert lines[1] == "Jul 01 12:34:56 combo sshd(pam_unix)[10002]: Another July log entry\n"


def test_split_syslog_across_year_end(tmp_path):
    # Syslog data at the end of one year and the start of the next
    syslog_data = """\
Dec 31 23:59:59 combo sshd(pam_unix)[10000]: Log entry at the end of December
Jan 01 00:00:01 combo sshd(pam_unix)[10001]: Log entry at the start of January
"""

    # Write the syslog data to a temporary file using the helper function
    temp_file = write_syslog_to_temp_file(tmp_path, syslog_data)

    # Run the splitter function
    split_syslog_by_day(temp_file)

    # Verify that two output files are created, one for each year-end day
    output_file_dec_31 = tmp_path / 'syslog-2023-12-31.log'
    output_file_jan_01 = tmp_path / 'syslog-2023-01-01.log'

    assert output_file_dec_31.exists(), f"{output_file_dec_31} should exist"
    assert output_file_jan_01.exists(), f"{output_file_jan_01} should exist"

    # Check contents of the December 31 log file
    with open(output_file_dec_31, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # One log entry for December 31st
        assert lines[0] == "Dec 31 23:59:59 combo sshd(pam_unix)[10000]: Log entry at the end of December\n"

    # Check contents of the January 01 log file
    with open(output_file_jan_01, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # One log entry for January 1st
        assert lines[0] == "Jan 01 00:00:01 combo sshd(pam_unix)[10001]: Log entry at the start of January\n"
