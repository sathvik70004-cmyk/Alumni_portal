#!/usr/bin/env bash
# exit on error
set -o errexit

# Ensure Python 3.11 is being used (more stable than 3.13)
PYTHON_VERSION=$(python --version)
echo "Using Python version: $PYTHON_VERSION"

# Upgrade pip and install build essentials first
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# Clean any existing builds
rm -rf build dist *.egg-info || true

# Install dependencies
python -m pip install -r requirements.txt --no-cache-dir

# Create instance folder and config if they don't exist
mkdir -p instance

# Initialize the application
python run.py