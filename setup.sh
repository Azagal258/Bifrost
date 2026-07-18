#!/bin/bash

cd "$(dirname "$0")" || exit 1

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete. Run:"
echo "python3 ~/Bifrost/script.py"