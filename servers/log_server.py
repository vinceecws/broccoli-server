#!/usr/bin/env python3

import logging
import os
from datetime import datetime
from util.data_util import *
from .server import Server

class LogServer(Server):

    def __init__(self, log_data_dir, timeout, server_name, max_conn=10, logs_dir="logs/", logging_level=logging.INFO, log_console=False, encoding="utf-8"):
        super().__init__(
            timeout, 
            server_name, 
            max_conn=max_conn, 
            logs_dir=logs_dir, 
            logging_level=logging_level, 
            log_console=log_console, 
            encoding=encoding)

        self.log_data_dir = log_data_dir
        
        os.makedirs(os.path.dirname(self.log_data_dir), exist_ok=True) # Recursively create directory if it does not exist yet

    def receive_data(self, data):

        if not self.process_data(data):
            logging.debug("Response: 500 Internal Server Error")
            return "500"

        logging.debug("Response: 200 OK")
        return "200"

    def process_data(self, data):
        return append_log_data_file(self.log_data_dir, data)
