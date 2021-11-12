#!/usr/bin/env bash

function new() {
    if [[ $# -eq 0 ]]; then
        open -a "Terminal" "$PWD"
    else
        open -a "Terminal" "$@"
    fi
}

open -a Terminal ~/Desktop/broccoli-server/start_time_server.py