#!/bin/bash
#By Pytel

# check if pip is installed
if ! [ -x "$(command -v pip)" ]; then
  echo 'Error: pip is not installed.' >&2
  exit 1
fi
# install required libraries
echo "Installing required libraries..."
pip install -r requirements.txt

# create config file
echo "Creating config file..."
python3 bot.py --config

# check if systemd is installed
if ! [ -x "$(command -v systemctl)" ]; then
  echo 'Error: systemctl is not installed.' >&2
  exit 1
fi

# change path to script
echo "Changing path to script..."
sed -i "s|<path>|$(pwd)|g" ./discordBashAccessor.service

# set up system service
echo "Setting up system service..."
cp ./discordBashAccessor.service /etc/systemd/system/discordBashAccessor.service
systemctl daemon-reload
systemctl enable discordBashAccessor.service
systemctl start discordBashAccessor.service

# check if service is running
if ! systemctl is-active --quiet discordBashAccessor.service; then
  echo 'Error: discordBashAccessor.service is not running.' >&2
  exit 1
fi

echo "Installation completed."