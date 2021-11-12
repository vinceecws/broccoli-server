#!/usr/bin/env python3

import threading
import logging
import multiprocessing
import os
import select
import signal
import socket
import sys
import time

class Server:

    def __init__(self, timeout, server_name, max_conn=10, logs_dir="logs/", logging_level=logging.INFO, log_console=False, encoding="utf-8"):
        self.timeout = timeout
        self.server_name = server_name
        self.max_conn = max_conn
        self.logs_path = os.path.join(logs_dir, server_name + ".log")
        self.logging_level = logging_level
        self.log_console = log_console
        self.encoding = encoding

        self.server_proc = None

        signal.signal(signal.SIGCHLD, self._forget_child_proc)

    def _close_main_sock(self):

        if self.sock is not None:
            logging.info("Closing main socket. All future incoming connections will be refused.")
            self.sock.close()
            self.sock = None

    def _terminate_all(self):

        logging.info("Closing active socket(s)")
        for conn in self.conn:
            if conn is not None:
                conn.close()

    def _start_conn_thread(self, idx, conn, host, port):

        self._conn_count += 1
        self.conn[idx] = conn

        with conn:
            logging.info(f"Started connection with: {host}:{port} on server {idx}")

            while True:
                try:
                    ready_to_read, _, _ = select.select([conn,], [conn,], [], 5)

                    if len(ready_to_read) > 0:
                        data = conn.recv(4096) # Receive

                        if not data:
                            break

                        logging.info(f"Received data: {data}")
                        data = self.decode_data(data).rstrip()
                        logging.debug(f"Decoded data: {data}")

                        response = self.receive_data(data)

                        logging.debug(f"Response code: {response}")
                        response = self.encode_data(response)
                        logging.debug(f"Encoded response: {response}")
                        conn.sendall(response) # Respond

                except UnicodeDecodeError as e: # Catches decoding error
                    logging.error(f"{e}")
                    conn.close()
                    break

                except (OSError, ValueError, select.error, socket.error) as e: # Catches all socket errors (incl. subclass of OSError) leading to closed socket
                    logging.error(f"{e}")
                    logging.error("Socket terminated prematurely")
                    break

            logging.info(f"Terminating connection with {host}:{port}")
            logging.info(f"Connection ended with: {host}:{port}")

        self.conn[idx] = None
        self._conn_count -= 1

        logging.info(f"Server {idx} will terminate now")

    def _run_server(self, host, port):

        signal.signal(signal.SIGINT, self._kill_server) # Ignored in child process
        signal.signal(signal.SIGTERM, self._kill_server)
        signal.signal(signal.SIGUSR1, self._kill_server)

        self.init_logger(log_console=self.log_console)

        self.kill = False
        self.conn = [None] * self.max_conn
        self._conn_count = 0

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:

            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
            self.sock.listen(5)
            logging.info(f"Server started at: {host}:{port}")

            while True:
                while self._conn_count >= self.max_conn: # No new connections should be accepted as long as there are no free slots
                    time.sleep(1)

                try:
                    if self.sock is None:
                        raise ConnectionAbortedError

                    logging.info("Listening for new connections...")
                    conn, addr = self.sock.accept()
                    conn.settimeout(self.timeout)

                    threading.Thread(target=self._start_conn_thread, args=(self._next_available_idx(), conn, addr[0], addr[1],)).start()

                except (OSError, ConnectionAbortedError) as e: # Raised when main socket is closed to prevent future incoming connections
                    logging.info("Main socket closed")
                    break

    def start(self, host, port):

        if not self.is_running():
            self.server_proc = multiprocessing.Process(target=self._run_server, args=(host, port,))
            self.server_proc.daemon = True
            self.server_proc.start()

    def stop(self, kill=False):

        if self.is_running():

            if kill:
                os.kill(self.server_proc.pid, signal.SIGUSR1)
            else:
                self.server_proc.terminate()

    def _kill_server(self, sig, frame):

        if sig == signal.SIGUSR1: # Kill immediately
            logging.info("Kill signal caught")
            logging.info("Main server will terminate immediately")
            logging.warning("Data corruption is possible due to premature termination")

            self._close_main_sock()

            if self._is_conn_active():
                self._terminate_all()

            logging.info("Main server will terminate now")
            sys.exit(0)

        elif sig == signal.SIGTERM: # Terminate after task completion
            logging.info("Terminate signal caught")

            self._close_main_sock()

            if not self._is_conn_active(): # No active connections, terminate immediately
                logging.info("No active socket(s)")

                logging.info("Main server will terminate now")
                sys.exit(0)

            logging.info("Active connection(s) found. Server will terminate after connection(s) timeout or task completion")
            self.kill = True

    def _forget_child_proc(self, sig, frame):

        if sig == signal.SIGCHLD and self.is_running():
            self.server_proc.close()
            self.server_proc = None

    def init_logger(self, log_console=False):

        logFormatter = logging.Formatter('%(asctime)s -> [%(name)s] %(levelname)s : %(message)s')
        rootLogger = logging.getLogger()
        rootLogger.setLevel(self.logging_level)

        fileHandler = logging.FileHandler(self.logs_path)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

        if log_console:
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)

    def _is_conn_active(self):
        # Checks if there is at least one element in self.conn is not None
        return any([conn for conn in self.conn if conn is not None])

    def _next_available_idx(self):
        # Finds the first element index in self.conn that is None, else return -1
        try:
            return self.conn.index(None)
        except ValueError:
            return -1

    def is_running(self):
        return self.server_proc is not None and self.server_proc.is_alive()

    def receive_data(self, data):
        return data

    def encode_data(self, data):
        '''
            Returns byte-string
        '''
        return data.encode(self.encoding)

    def decode_data(self, data):
        '''
            Returns String
        '''
        return data.decode(self.encoding)
