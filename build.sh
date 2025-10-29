#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

# Create instance folder and config if they don't exist
mkdir -p instance

# Run any database migrations or initialization if needed
python run.py