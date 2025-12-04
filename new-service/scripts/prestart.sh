#!/usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Create initial data in DB
python app/init_data.py
