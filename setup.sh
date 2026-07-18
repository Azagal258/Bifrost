#!/bin/bash

# moves wherever the user saved the code
cd "$(dirname "$0")" || exit 1

# updates the code
git pull

# starts venv
python3 -m venv .venv
source .venv/bin/activate

# installs packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# makes run executable
chmod +x ./run.sh

# Prompts infos to user
echo "Setup/Update complete."
echo "You can now run the script by double-clicking run.sh"
read -r -p "Press Enter to close..."