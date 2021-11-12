#!/usr/bin/env python3

import logging
from util.data_util import *
from .server import Server

class DataServer(Server):

    def __init__(self, data_dir, timeout, server_name, max_conn=10, logs_dir="logs/", logging_level=logging.INFO, encoding="utf-8"):
        super().__init__(timeout, server_name, max_conn, logs_dir, logging_level, encoding)

        self.data_dir = data_dir
        self.init_header()

    def init_header(self):
        self.current_header = []

        header = read_header_file(self.data_dir).rstrip()
        if not header:
            self.current_header = []
        else:
            self.current_header = header.split(",")

    def receive_data(self, data):
        values = self.parse_data(data)
        if values is None:
            logging.debug("Response: 400 Bad Request")
            return "400"

        if not self.process_data(values):
            logging.debug("Response: 500 Internal Server Error")
            return "500"

        logging.debug("Response: 200 OK")
        return "200"

    def parse_data(self, data):
        try:
            values = dict([x.split(":") for x in data.split(",")])

        except ValueError as e:
            logging.error(f"{e}. Error in parsing data.")
            return None

        return values

    def process_data(self, data):

        # Update header, if any new column(s) are added
        header_diff = [key for key in data.keys() if key not in self.current_header]
        if (len(header_diff) > 0):
            logging.debug(f"Writing new column(s) to header file: {','.join(header_diff)}")
            self.current_header += header_diff
            if (not write_header_file(self.data_dir, self.current_header)):
                return False
            logging.debug(f"Current header is: {','.join(self.current_header)}")

        # In case new data does not have some columns in current_header, fill with empty string
        new_data = [str(data[key]) if key in data else "" for key in self.current_header]
        
        return append_data_file(self.data_dir, new_data)
