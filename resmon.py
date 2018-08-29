#!/usr/bin/env python3


import argparse
import subprocess
import sys
import os
import socket
import time
import threading

from rm_host import resmon_host



# Constants
COMM_PORT = 9867


# Builds the command line parameter parser
def build_option_parser():

	# Brief description of script
	parser = argparse.ArgumentParser(description = 'Monitor CPU usage of a number of remote hosts. Connects via ssh, so make sure you have passwordless ssh set up for the hosts you want to monitor.')

	# Add address information to the arguments
	parser.add_argument('-a', '--addresses', nargs = '+', required = True,
						help = 'List of remote hosts to monitor.')

	# Allows user to set update delay
	parser.add_argument('-d', '--delay', type = float, default = 1, required = False,
						help = 'Set delay between updates.')

	# Return the constructed parser
	return parser


# Starts the timer thread and returns it
def start_timer_thread(delay):
	
	# Start the scheduler thread
	thread = threading.Thread(target = time.sleep, args = (delay,))
	thread.start()

	# Return the thread so that we can wait on it to achieve a delay
	return thread


# Main routine
def main():

	# Add parser options and parse command line arguments
	parser = build_option_parser()
	args = parser.parse_args()

	# Start the wait thread thread for non blocking delay
	timer_thread = start_timer_thread(args.delay)

	# Intialise array of hosts
	hosts = []
	for address in args.addresses:
		hosts.append(resmon_host(address, COMM_PORT))


	# Clear the screen	
	print('\033[1J', end = '')
	print('\033[;H', end = '')

	# Update each host in a loop
	while True:

		# Wait for the scheduler thread to finish, then restart it
		timer_thread.join()
		timer_thread = start_timer_thread(args.delay)
		
		# Get terminal dimensions
		rows, columns = os.popen('stty size', 'r').read().split()

		# Do the updates and generate the print string
		lines = []
		for host in hosts:
			host.update()
			lines.extend(host.stat.cpu.string(4, int(columns)))

		# Move cursor to top left, then print everything
		line_number = 1
		for line in lines:
			print('\033[%d;1f' % line_number, end = line)
			line_number += 1
		
		# Flush standard out to perform the print
		sys.stdout.flush()
	

# Make this behave like a boring old c program
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Recieved KB interrupt, quitting monitor.')

