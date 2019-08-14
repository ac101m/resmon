#!/bin/sh

#
# Simple shell script to install the remote responder
# Must be run with elevated privileges
#

# Cop
mkdir ~/.resmon/
sudo cp ./rm_respond.py ~/.resmon

# Create the systemd file
DFILE="/lib/systemd/system/resmon.responder.service"
sudo echo "[Unit]" > $DFILE
sudo echo "Description=Remote responder for the resmon cluster monitor." >> $DFILE
sudo echo "[Service]" >> $DFILE
sudo echo "Type=simple" >> $DFILE
sudo echo "ExecStart=/usr/bin/python3 /home/ac/.resmon/rm_respond.py 9867" >> $DFILE
sudo echo "[Install]" >> $DFILE
sudo echo "WantedBy=multi-user.target" >> $DFILE

# Set up the systemd service
sudo systemctl daemon-reload
sudo systemctl enable resmon.responder
sudo service resmon.responder start
