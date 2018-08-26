#!/usr/bin/env python3


import subprocess


# Class serves as an interface to an rm_respond instance running on a remote host.
class resmon_host:
	process = None			# Subprocess handle for ssh
	name = None				# Name of the remote host
	address = None			# IP address of the remote host
	socket = None			# Socket
	intialised = False		# Has this host object been initialised yet?

	# Constructor
	
