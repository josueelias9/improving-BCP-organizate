#!/usr/bin/env bash

set -e
set -x

# Let the DB start
PYTHONPATH="." python app/backend_pre_start.py

# Create initial data in DB
PYTHONPATH="." python app/init_data.py
