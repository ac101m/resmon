#!/bin/sh

#
# Simple shell script to install the remote responder
# Must be run with elevated privileges
#

# Install in /usr/local/resmon
RESMON_INSTALL_DIR="/usr/local/resmon"

# Copy resmon files
sudo mkdir -p "$RESMON_INSTALL_DIR"
sudo cp ./rm_respond.py "$RESMON_INSTALL_DIR"

# Create the systemd unit file
DFILE="/lib/systemd/system/resmon.responder.service"
sudo printf "[Unit]\n" | sudo tee "$DFILE"
sudo printf "Description=Remote responder for the resmon cluster monitor.\n" | sudo tee -a "$DFILE"
sudo printf "\n[Service]\n" | sudo tee -a "$DFILE"
sudo printf "User=$USER\n" | sudo tee -a "$DFILE"
sudo printf "Group=$USER\n" | sudo tee -a "$DFILE"
sudo printf "Type=simple\n" | sudo tee -a "$DFILE"
sudo printf "ExecStart=/usr/bin/python3 $RESMON_INSTALL_DIR/rm_respond.py 9867\n" | sudo tee -a "$DFILE"
sudo printf "\n[Install]\n" | sudo tee -a "$DFILE"
sudo printf "WantedBy=multi-user.target\n" | sudo tee -a "$DFILE"

# Ge the daemon running
sudo systemctl daemon-reload
sudo systemctl enable resmon.responder
sudo service resmon.responder start
