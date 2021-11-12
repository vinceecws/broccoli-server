#!/usr/bin/env python3

'''
	General config
'''
HOST = "192.168.1.169"
ENCODING = "utf-8"
LOGS_DIR = "./logs/"

'''
	Data server config
'''
DATA_SERVER_PORT = 13000
DATA_SERVER_SOCKET_TIMEOUT = 30 # In seconds
DATA_DIR = "./data/sensor_data/"

'''
	Time server config
'''
TIME_SERVER_PORT = 13001
TIME_SERVER_SOCKET_TIMEOUT = 30 # In seconds

'''
	Log server config
'''
LOG_SERVER_PORT = 13002
LOG_SERVER_SOCKET_TIMEOUT = 30 # In seconds
LOG_DATA_DIR = "./data/log_data/"