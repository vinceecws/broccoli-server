#!/usr/bin/env python3

import signal
import os
import logging
from argparse import ArgumentParser
from config import *
from servers import DataServer

data_server = None

def signal_handler(sig, frame):
    global data_server
    
    print("Terminating after task completion")
    data_server.stop(kill=False)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--log-console", action="store_true")
    parser.add_argument("--max-conn", default=10, type=int)
    args = parser.parse_args()

    if args.debug:
        print("Starting data server in DEBUG mode")
        logging_level = logging.DEBUG
    else:
        print("Starting data server in NORMAL mode")
        logging_level = logging.INFO

    data_server = DataServer(
        DATA_DIR, 
        DATA_SERVER_SOCKET_TIMEOUT, 
        "data_server", 
        max_conn=args.max_conn, 
        logs_dir=LOGS_DIR, 
        logging_level=logging_level, 
        log_console=args.log_console, 
        encoding=ENCODING)

    data_server.start(HOST, DATA_SERVER_PORT)

    signal.signal(signal.SIGINT, signal_handler)

    while data_server.is_running():
        signal.pause()
