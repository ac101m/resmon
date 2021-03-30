#!/usr/bin/env bash

#
# Uninstall the respondeer daemon
# Requires elevated privileges
#

# Constants
RESMON_INSTALL_DIR="/usr/local/resmon"
UNIT_FILE_PATH="/lib/systemd/system/resmon.responder.service"

# Stop and disable the responder
sudo systemctl stop resmon.responder.service
sudo systemctl disable resmon.responder.service

# Remove files
sudo rm -rf "$RESMON_INSTALL_DIR" "$UNIT_FILE_PATH"
