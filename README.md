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
- Required Python packages (see `requirements.txt`)

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/gvnberaldi/rdm_exam.git

2. **Navigate to the Project Directory:**

   ```bash
   cd rdm_exam

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt

## Usage

### Export Syslog

1. **Export to JSON:**

   ```bash
   python main.py export json /path/to/syslog.log /path/to/output.json

2. **Export to SQL:**

   ```bash
   python main.py export sql /path/to/syslog.log /path/to/output.sql

### Query Syslog

1. **Retrieve Log Messages Between Two Timestamps:**

   ```bash
   python main.py query /path/to/syslog.log between 01/01/2024 07/07/2024

2. **Retrieve Log Messages from a Specific Process:**

   ```bash
   python main.py query /path/to/syslog.log from_process process_name

3. **Retrieve Log Messages Containing Specific Terms:**

   ```bash
   python main.py query /path/to/syslog.log contains_words word1,word2,word3

### Split Syslog

1. **Split Syslog into Daily Files:**

   ```bash
   python main.py split /path/to/syslog.log
