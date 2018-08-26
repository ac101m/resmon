#!/usr/bin/env python3


import subprocess
import os
import sys
import socket
import signal
import atexit



# Class serves as an interface to an rm_respond instance running on a remote host.
class resmon_host:
	process = None		# Subprocess handle for ssh
	name = None			# Name of the remote host
	address = None		# IP address of the remote host
	socket = None		# Socket for communication with remote host
	port = None			# Port for communication with remote responder


	# Kills the remote response script
	def kill_remote_responder(self):
		if self.process is None:
			return
		else:
			self.process.kill()
			self.process = None


	# Starts the remote response script
	def start_remote_responder(self):

		# Get the path to the rm_respond applet, assumed to be in the same
		# directory, mounted at the same place in the filesystem on the remote host.
		pathname = os.path.dirname(sys.argv[0])
		abspath = os.path.abspath(pathname)

		# Open subprocess via ssh on remote, pipe everything into /dev/null.
		self.process = subprocess.Popen(
			['ssh', self.name, '%s/rm_respond.py %s %d > /dev/null' % (abspath, self.address, self.port)])

		# Register the child process with the at-exit signal
		atexit.register(self.kill_remote_responder)
		

	# Constructor
	def __init__(self, name, port):

		# Initialise hosts name and address (the same for now)
		self.name = name
		self.address = name
		self.port = port

		# Initialise the socket to be used for communication
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Start responder on the remote host via ssh
		self.start_remote_responder()
		


	# Placeholder
	def get_response(self, command):
		
		# Connect to the remote responder
		self.socket.connect((self.address, self.port))
		self.socket.sendall(command.encode('utf-8'))
		response = self.socket.recv(1024)
		self.socket.close()

		return '%s - %s' % (self.name, response)

		
