#!/usr/bin/env python3


import subprocess
import os
import sys
import socket
import atexit
import time
import shlex

from rm_stat import *



# constants
SOCK_CONNECT_TRY_LIMIT = 20
SOCK_CONNECT_TRY_DELAY = 0.1



# Class serves as an interface to an rm_respond instance running on a remote host.
class resmon_host:

	# General stuff
	process = None		# Subprocess handle for ssh
	name = None			# Name of the remote host
	address = None		# IP address of the remote host
	port = None			# Port for communication with remote responder

	# Stat struct	
	stat = None


	# Constructor
	def __init__(self, name, port):

		# Initialise hosts name and address (the same for now)
		self.name = name
		self.address = name
		self.port = port

		# Start responder on the remote host via ssh
		self.start_remote_responder()

		# Check that the remote responder responds
		self.test_remote_responder()

		# Get remote responder output and initialise stats
		self.stat = resmon_stat(self.send_request('REQUEST_STAT'))


	# Starts the responder script on the remote host
	def start_remote_responder(self):

		# Get the path to the rm_respond applet, assumed to be in the same
		# directory, mounted at the same place in the filesystem on the remote host.
		pathname = os.path.dirname(sys.argv[0])
		abspath = os.path.abspath(pathname)

		# Open subprocess via ssh on remote, pipe everything into /dev/null.
		command = 'ssh %s %s/rm_respond.py %s %d' % (self.address, abspath, self.name, self.port)
		#self.process = subprocess.Popen(shlex.split(command), 
		#								stdout = subprocess.DEVNULL,
		#								stderr = subprocess.DEVNULL)

		
	# Repeatedly try to ping the remote responder until it succeeds
	def test_remote_responder(self):
		trycount = 0
		while True:
			try:
				if self.send_request('REQUEST_PING') != 'REQUEST_PING_ACK':
					print('Failed to initialise remote host responder - response invalid.')
					sys.exit(1)
				else:
					break
			except ConnectionRefusedError:
				if trycount == SOCK_CONNECT_TRY_LIMIT:
					print('Failed to initialise remote host responder - connection timeout.')
					sys.exit(1)
				else:
					time.sleep(SOCK_CONNECT_TRY_DELAY)
					trycount = trycount + 1


	# Send request and recieve response
	def send_request(self, request):
		
		# Open the socket and send the command
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
	def update(self):
		
		# Request data from remote responder and update host stats
		stat_raw = self.send_request('REQUEST_STAT')
		self.stat.update(stat_raw)


	# Destructor, cleans up subprocess
	def __del__(self):

		# Clean up the remote responder process
		if self.process is not None:
			self.send_request('REQUEST_STOP')
			self.process.wait()

