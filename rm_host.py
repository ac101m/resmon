#!/usr/bin/env python3


import subprocess
import os
import sys
import socket
import atexit
import time
import shlex
import curses
from math import ceil

from rm_stat import resmon_stat
from utils import vec2



# constants
SOCK_CONNECT_TRY_LIMIT = 20
SOCK_CONNECT_TRY_DELAY = 0.1


# Host status constants
RM_HOST_ONLINE = 0
RM_HOST_CONNECTION_LOST = 1
RM_HOST_OFFLINE = 2



# Class serves as an interface to an rm_respond instance running on a remote host.
class resmon_host:

	# General stuff
	process = None				# Subprocess handle for ssh
	name = None					# Name of the remote host
	address = None				# IP address of the remote host
	port = None					# Port for communication with remote responder

	# Host connection status
	status = RM_HOST_OFFLINE
	status_trycount = 0

	# Stat struct
	stat = None


	# Constructor
	def __init__(self, name, port):

		# Initialise hosts name and address (the same for now)
		self.name = name
		self.address = name
		self.port = port

		# Get remote responder output and initialise stats
		self.update(0.1)


	# Send request and recieve response
	def send_request(self, request, timeout = 1):

		# Open the socket and send the command
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(timeout)
		s.connect((self.address, self.port))
		s.sendall(request.encode('utf-8'))

		# Recieve the response in a loop
		response = ''
		while True:
			buf = s.recv(2048).decode('utf-8')
			if len(buf) == 0: break
			else:
				response = '%s%s' % (response, buf)

		# Close the socket and return the response
		s.close()
		return response


	# Update CPU utilisation
	def update(self, timeout = 1):

		# Try to get the data
		try:
			stat_raw = self.send_request('REQUEST_STAT', timeout)
		except:
			self.status = RM_HOST_OFFLINE
			return

		# Update stats, initialise if not initialised already
		if self.stat == None:
			self.stat = resmon_stat(stat_raw)
		else:
			self.stat.update(stat_raw)

		# Indicate that we are online!
		self.status = RM_HOST_ONLINE


	# Renders host status seen at top of window
	def render_status(self, screen, position, width):

		# Start by displaying name
		screen.move(position.y, position.x)
		screen.addstr(self.name + ' - ')

		# Print the status of the connection
		if self.status == RM_HOST_ONLINE:
		 	screen.addstr('CONNECTED', curses.color_pair(3))
		elif self.status == RM_HOST_OFFLINE:
		 	screen.addstr('OFFLINE', curses.color_pair(2))
		else:
		 	screen.addstr('? UNKONWN ?')

		# Return the number of lines used
		return 1


	# Render the host
	def render(self, screen, position, width):

		# Render the host status
		lines = self.render_status(screen, position, width)

		# Only render stats if the host is online or pending
		if self.status != RM_HOST_OFFLINE:
			lines = self.stat.render(screen, vec2(position.x, position.y), width)

		# Return the number of lines used on this host
		return vec2(width, lines)


	# Destructor, cleans up subprocess
	def __del__(self):

		# Clean up the remote responder process
		if self.process is not None:
			self.send_request('REQUEST_STOP')
			self.process.wait()
