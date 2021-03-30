#!/usr/bin/env bash

#
# Install the responder daemon
# Requires elevated permissions
#

# Constants
RESMON_INSTALL_DIR="/usr/local/resmon"
UNIT_FILE_PATH="/lib/systemd/system/resmon.responder.service"
PORT="9867"

# Copy resmon files
sudo mkdir -p "$RESMON_INSTALL_DIR"
sudo cp ./rm_respond.py "$RESMON_INSTALL_DIR"

# Create the systemd unit file
sudo printf "[Unit]\n" | sudo tee "$UNIT_FILE_PATH"
sudo printf "Description=Remote responder for the resmon cluster monitor.\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "\n[Service]\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "User=$USER\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "Group=$USER\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "Type=simple\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "ExecStart=/usr/bin/python3 $RESMON_INSTALL_DIR/rm_respond.py 9867\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "\n[Install]\n" | sudo tee -a "$UNIT_FILE_PATH"
sudo printf "WantedBy=multi-user.target\n" | sudo tee -a "$UNIT_FILE_PATH"

# Ge the daemon running
sudo systemctl daemon-reload
sudo systemctl enable resmon.responder
sudo service resmon.responder start
