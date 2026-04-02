#!/bin/sh
set -e
python docker/wait_and_init.py
exec "$@"
