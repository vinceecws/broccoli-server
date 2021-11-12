#!/usr/bin/env python3

import signal
import os
import logging
from argparse import ArgumentParser
from config import *
from servers import TimeServer

time_server = None
terminate = False

def signal_handler(sig, frame):
    global time_server
    global terminate
    
    if terminate:
        time_server.stop(kill=True)

    else:
        time_server.stop(kill=False)
        terminate = True

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--max-conn", default=10, type=int)
    args = parser.parse_args()

    if args.debug:
        print("Starting time server in DEBUG mode")
        logging_level = logging.DEBUG
    else:
        print("Starting time server in NORMAL mode")
        logging_level = logging.INFO

    time_server = TimeServer(TIME_SERVER_SOCKET_TIMEOUT, "time_server", max_conn=args.max_conn, logs_dir=LOGS_DIR, logging_level=logging_level, encoding=ENCODING)
    time_server.start(HOST, TIME_SERVER_PORT)

    signal.signal(signal.SIGINT, signal_handler)

    while time_server.is_running():
        signal.pause()