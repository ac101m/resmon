#!/usr/bin/env python3


import argparse
import subprocess
import sys
import os
import socket
import time

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


# Main routine
def main():

	# Add parser options and parse command line arguments
	parser = build_option_parser()
	args = parser.parse_args()

	# Intialise array of hosts
	hosts = []
	for i in range(0, len(args.addresses)):
		hosts.append(resmon_host(args.addresses[i], COMM_PORT))

	# Update each host
	while True:
		time.sleep(args.delay)
		for i in range(0, len(hosts)):
			hosts[i].update()
			print(100 - hosts[i].stat.cpu.total.idle)
	

# Make this behave like a boring old c program
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('\nRecieved KB interrupt, quitting monitor.')

