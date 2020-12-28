#!/bin/bash

echo "Creating directory"
rm -rf /opt/tally
mkdir /opt/tally

echo "Creating virtual env"
python3 -m venv /opt/tally/env/
source /opt/tally/env/bin/activate
pip install -r ../requirements.txt
# python -m pip install --upgrade pip
cp -r ../app /opt/tally

echo "Copying standard config file"
cp config-tally-only.json /opt/tally/config.json
echo "Do you want to install dual screen ? (Y/N)"
read dual_screen
if [ "$dual_screen" == "Y"]; then
echo "Copying dual screen config file"
cp config-dual-screen.json /opt/tally/config.json
fi
