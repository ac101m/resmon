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
	parser = argparse.ArgumentParser(description = 'Monitor CPU usage of remote hosts.')

	# Add address information to the arguments
	parser.add_argument('-a', '--addresses', nargs = '+', required = False,
						help = 'List of remote hosts to monitor. Must be accessible by passworldess ssh.')

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

	# Get response from each host and print it
	time.sleep(1)
	for i in range(0, len(hosts)):
		print(hosts[i].get_response('REQUEST_CPU_UTIL'))

	# Exit
	sys.exit(0)
	

# Make this behave like a boring old c program
if __name__ == '__main__':
	main()

