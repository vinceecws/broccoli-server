#!/usr/bin/env python3

import signal
import os
import logging
import time
from argparse import ArgumentParser
from config import *
from servers import DataServer, LogServer, TimeServer

data_server = None
log_server = None
time_server = None

def signal_handler(sig, frame):
    global data_server
    global log_server
    global time_server

    data_server.stop(kill=False)
    log_server.stop(kill=False)
    time_server.stop(kill=False)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--log-console", action="store_true")
    parser.add_argument("--max-conn", default=10, type=int)
    args = parser.parse_args()

    if args.debug:
        print("Starting all servers in DEBUG mode")
        logging_level = logging.DEBUG
    else:
        print("Starting all servers in NORMAL mode")
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

    log_server = LogServer(
        LOG_DATA_DIR, 
        LOG_SERVER_SOCKET_TIMEOUT, 
        "log_server", 
        max_conn=args.max_conn, 
        logs_dir=LOGS_DIR, 
        logging_level=logging_level, 
        log_console=args.log_console, 
        encoding=ENCODING)

    time_server = TimeServer(
        TIME_SERVER_SOCKET_TIMEOUT, 
        "time_server", 
        max_conn=args.max_conn, 
        logs_dir=LOGS_DIR, 
        logging_level=logging_level, 
        log_console=args.log_console, 
        encoding=ENCODING)

    data_server.start(HOST, DATA_SERVER_PORT)
    log_server.start(HOST, LOG_SERVER_PORT)
    time_server.start(HOST, TIME_SERVER_PORT)

    print("All servers started")

    signal.signal(signal.SIGINT, signal_handler)

    while any([data_server.is_running(), log_server.is_running(), time_server.is_running()]):
        signal.pause()