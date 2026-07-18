#!/bin/bash

# moves wherever the user saved the code
cd "$(dirname "$0")" || exit 1

# starts venv
source .venv/bin/activate
python script.py 2>&1 | tee run.log

# Prompts infos to user
echo
echo "Program finished."
read -r -p "Press Enter to close..."