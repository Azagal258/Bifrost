#!/bin/bash

cd "$(dirname "$0")" || exit 1

source .venv/bin/activate
python script.py 2>&1 | tee run.log

echo
echo "Program finished. Press Enter to close."
read