#!/usr/bin/env python3

import logging
from os import path

def read_header_file(data_dir):
    if not path.exists(path.join(data_dir, "header.csv")):
        write_header_file(data_dir, []) # Create header file first if it does not exist
        
    try:
        with open(path.join(data_dir, "header.csv"), "r") as f:
            return f.readline()

    except OSError as e:
        logging.error(f"{e}. Error reading header file.")
        return None

def write_header_file(data_dir, header):
    try:
        with open(path.join(data_dir, "header.csv"), "w+") as f:
            f.write(",".join(header))
            f.write("\n")

    except OSError as e:
        logging.error(f"{e}. Error writing to header file.")
        return False

    return True

def append_data_file(data_dir, data):
    try:
        with open(path.join(data_dir, f"data.csv"), "a+") as f:
            f.write(",".join(data))
            f.write("\n")

    except OSError as e:
        logging.error(f"{e}. Error appending to data file.")
        return False

    return True

def append_log_data_file(log_data_dir, log_data):
    try:
        with open(path.join(log_data_dir, f"data.log"), "a+") as f:
            f.write(log_data)
            f.write("\n")

    except OSError as e:
        logging.error(f"{e}. Error appending to log data file.")
        return False

    return True
