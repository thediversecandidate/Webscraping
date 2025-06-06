#!/usr/bin/env bash
# Simple setup script for running tests locally
set -e

python3 -m venv .venv
. .venv/bin/activate

pip install --upgrade pip
pip install -r django/derrick/requirements.txt
