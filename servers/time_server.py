#!/usr/bin/env python3

import logging
from datetime import datetime, timezone, timedelta
from .server import Server

class TimeServer(Server):

    def __init__(self, timeout, server_name, max_conn=10, logs_dir="logs/", logging_level=logging.INFO, encoding="utf-8"):
        super().__init__(timeout, server_name, max_conn, logs_dir, logging_level, encoding)

        self.timezones = set(["local", "utc"])

    def receive_data(self, data):
        values = self.parse_data(data)
        if values is None:
            logging.debug("Response: 400 Bad Request")
            return "400"

        response = self.process_data(values)

        if not response >= 0:
            logging.debug("Response: 400 Bad Request")
            return "400"

        logging.debug("Response: 200 OK")
        return f"200 {response}"

    def parse_data(self, data):
        try:
            data = [x.split(":") for x in data.split(",")]
            values = {key: val for key, val in data}

        except ValueError as e:
            logging.error(f"{e}. Error in parsing data.")
            return None

        return values

    def process_data(self, data):
        if "timezone" not in data or data["timezone"] not in self.timezones:
            return -1

        try:
            if "offset_seconds" in data:
                offset = timedelta(seconds=int(data["offset_seconds"]))
            else:
                offset = timedelta()

        except ValueError as e:
            logging.error(f"{e}. Error in processing data.")
            return -1

        if data["timezone"] == "local":
            return (datetime.now().replace(tzinfo=timezone.utc) + offset).timestamp()
        else: # timezone == "utc"
            return (datetime.utcnow().replace(tzinfo=timezone.utc)+ offset).timestamp()
