#!/usr/bin/env python3


import argparse
import subprocess
import sys
import os
import socket
import time
import threading
import curses
import signal
from curses import wrapper

from rm_host import resmon_host



# Constants
COMM_PORT = 9867



# Builds the command line parameter parser
def build_option_parser():

	# Brief description of script
	parser = argparse.ArgumentParser(description = 'Monitor CPU usage of a number of remote hosts.')

	# Add address information to the arguments
	parser.add_argument('-a', '--addresses', nargs = '+', required = True,
						help = 'List of remote hosts to monitor. Uses passwordless ssh to connect.')

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



# Re-draw the screen
def redraw(screen, hosts):

	# Generate host windows
	cursor_y = 0
	for host in hosts:
		screen.move(cursor_y, 0)
		host_displacement = host.render(screen)
		cursor_y += host_displacement

	# Refresh and clear the screen
	screen.refresh()
	screen.erase()


# Main routine
def main(screen):

	# Add parser options and parse command line arguments
	parser = build_option_parser()
	args = parser.parse_args()

	# Initialise curses colors
	curses.use_default_colors()
	for i in range(0, curses.COLORS):
		curses.init_pair(i+1, i, -1)

	# Clear and update the screen, disable the cursor
	curses.curs_set(0)
	screen.erase()
	screen.refresh()

	# Start the wait thread thread for non blocking delay
	timer_thread = start_timer_thread(args.delay)

	# Intialise array of hosts
	hosts = []
	for address in args.addresses:
		hosts.append(resmon_host(address, COMM_PORT))

	# Define a resize handler
	def resize_handler(*args):
		rows, columns = os.popen('stty size', 'r').read().split()
		curses.resizeterm(int(rows), int(columns))
		redraw(screen, hosts)
	
	# Register the handler with the resize signal
	signal.signal(signal.SIGWINCH, resize_handler) 

	# Main update loop
	while True:

		# redraw
		redraw(screen, hosts)

		# Wait for the scheduler thread to finish, then restart it
		timer_thread.join()
		timer_thread = start_timer_thread(args.delay)

		# Update host stats
		for host in hosts:
			host.update_stats()



# Make this behave like a boring old c program
if __name__ == '__main__':
	try:
		wrapper(main)		# This is a curses application
	except KeyboardInterrupt:
		print('Recieved KB interrupt, quitting monitor.')

