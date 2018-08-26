#!/usr/bin/env python3


import argparse
import subprocess
import sys
import os
import socket
import time

import rm_host


# Constants
COMM_PORT = 9867


# Builds the command line parameter parser
def build_option_parser():

	# Brief description of script
	parser = argparse.ArgumentParser(description = 'Monitor CPU usage of remote hosts.')

	# Add address information to the arguments
	parser.add_argument('-a', '--addresses', nargs = '+', required = False,
						help = 'List of remote hosts to monitor. Must be accessible by passworldess ssh.')

	# Return the constructed parser
	return parser


# Start remote processes
def start_remote_processes(hosts):

	# Get absolute path to child process script
	# Assumes working directory matches on all hosts (eg: shared drive)
	pathname = os.path.dirname(sys.argv[0])
	abspath = os.path.abspath(pathname)

	# Run the child script on each process, passing the desired port
	print('Starting child processes...')
	processes = []
	for i in range(0, len(hosts)):
		print('%s:%d - ' % (hosts[i], COMM_PORT), end = ''); sys.stdout.flush()
		command = '%s/resmon_respond.py %s %d > /dev/null' % (abspath, hosts[i], COMM_PORT)
		processes.append(
			subprocess.Popen(
				['ssh', '%s' % hosts[i], command],
				shell = False,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE))

		print('Success.')

	# Return the connected processes so that we can use them later
	return processes


# Send a command and get a response
def perform_command(socket, command):
	print('Sending command %s' % command)
	socket.sendall(bytearray(command, 'utf-8'))
	response = socket.recv(1024)
	return response


# Main routine
def main():

	# Add parser options and parse command line arguments
	parser = build_option_parser()
	args = parser.parse_args()

	# Open an ssh connection to each of the hosts and print out proc stat
	processes = start_remote_processes(args.addresses)
	time.sleep(1)

	# Create a socket object for each remote host
	sockets = []
	for i in range(0, len(args.addresses)):
		sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

		print('Connecting to child process @ %s:%d... ' % (args.addresses[i], COMM_PORT), end = '')
		sockets[i].connect((args.addresses[i], COMM_PORT))
		print('Success.')

	# Get a string from each
	for i in range(0, len(sockets)):
		print(perform_command(sockets[i], 'RESPOND'))

	# Close all the sockets and exit
	print('Closing all sockets.')
	for i in range(0, len(sockets)):
		sockets[i].close()
	

# Make this behave like a boring old c program
if __name__ == '__main__':
	main()

