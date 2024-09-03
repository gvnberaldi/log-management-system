# Syslog Manager

Syslog Manager is a terminal-based tool for manipulating and querying syslog files. It allows you to export syslog data to JSON or SQL formats, perform simple and complex queries, and split syslog files by day.

## Features

1. **Export Syslog**
   - Export syslog data to a JSON file.
   - Export syslog data to an SQL database.

2. **Query Syslog**
   - Retrieve log messages between two timestamps.
   - Retrieve log messages originating from a specific process.
   - Retrieve log messages that contain specific terms.

3. **Split Syslog**
   - Split a syslog file into multiple files, each storing events for a single day.

## Installation

### Prerequisites

- Python 3.12

### From PyPi (Recommended)
You can install Syslog Manager directly from PyPI using pip:

   ```bash
   pip install syslog_manager
   ```

### From GitHub Release
Alternatively, you can download the .whl package from the GitHub Releases page and install it using pip:

   ```bash
   pip install path/to/syslog_manager-x.x.x-py3-none-any.whl
   ```
Replace path/to/ with the actual path to the downloaded .whl file.

## Usage

Once installed, the syslog_manager command is available in your terminal. Below are some examples of how to use it.

### Export Syslog

1. **Export to JSON:**

   ```bash
   syslog_manager export json /path/to/syslog.log /path/to/output.json
   ```
   
2. **Export to SQL:**

   ```bash
   syslog_manager export sql /path/to/syslog.log /path/to/output.sql
   ```
   
### Query Syslog

1. **Retrieve Log Messages Between Two Timestamps:**

   ```bash
   syslog_manager query /path/to/syslog.log between 01/01/2024 07/07/2024
   ```
   
2. **Retrieve Log Messages from a Specific Process:**

   ```bash
   syslog_manager query /path/to/syslog.log from_process process_name
   ```
   
3. **Retrieve Log Messages Containing Specific Terms:**

   ```bash
   syslog_manager query /path/to/syslog.log contains_words word1,word2,word3
   ```
   
### Split Syslog

1. **Split Syslog into Daily Files:**

   ```bash
   syslog_manager split /path/to/syslog.log
   ```