
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
from utils import vec2


# Constants
COMM_PORT = 9867
ARGS = None



# Gets hosts from a list in a file
def get_hosts_from_file(hostfile):
	hosts = []
	fp = None

	# Open the specified file
	try: fp = open(hostfile, 'r')
	except:
		print("Error, could not open '%s'" % hostfile)
		exit(1)

	# Parse the file
	lines = fp.read().split('\n')
	for line in lines:
		names = list(filter(None, line.split(' ')))
		for name in names:
			if name[0] == '#': break
			hosts.append(resmon_host(name, COMM_PORT))

	# Close file and return
	fp.close()
	return hosts



# Starts the timer thread and returns it
def start_timer_thread(delay):

	# Start the scheduler thread
	thread = threading.Thread(target = time.sleep, args = (delay,))
	thread.start()

	# Return the thread so that we can wait on it to achieve a delay
	return thread



# Re-draw the screen
def redraw(screen, hosts):

	screen.erase()
	screen_max_y, screen_max_x = screen.getmaxyx()

	# Host positioning
	width = screen_max_x
	position = vec2(0, 0)
	more_string = 'V  MORE  V'

	# Print the hosts
	try:
		for i in range(0, len(hosts)):

			# Render the host
			size = hosts[i].render(screen, position, width)
			position.y += size.y

			# Print a divider line
			if i != len(hosts) - 1:
				screen.move(position.y, position.x)
				for j in range(0, screen_max_x): screen.addstr('-')
			position.y += 1

	# This happens when printing runs off the end of the terminal (usually)
	except curses.error:
		screen_max_y, screen_max_x = screen.getmaxyx()
		screen.move(screen_max_y - 1, 0)
		screen.clrtoeol()
		screen.move(screen_max_y - 1, int((screen_max_x - len(more_string)) / 2))
		screen.addstr(more_string)

	# Refresh the screen
	screen.refresh()



# Update hosts in parallel
def update_hosts(hosts, timeout):
	threads = []
	for host in hosts:
		thread = threading.Thread(target = host.update, args = (timeout,))
		thread.start()
		threads.append(thread)
	for thread in threads:
		thread.join()



# Main routine
def main(screen):

	# Initialise curses colors
	curses.use_default_colors()
	for i in range(0, curses.COLORS):
		curses.init_pair(i + 1, i, -1)

	# Clear and update the screen, disable the cursor
	curses.curs_set(0)
	screen.erase()
	screen.refresh()

	# Get hosts from file or command line
	hosts = []
	if ARGS.hostfile != None:
		hosts = get_hosts_from_file(ARGS.hostfile)
	if ARGS.hosts != None:
		for name in ARGS.hosts:
			hosts.append(resmon_host(name, COMM_PORT))

	# Make sure we have some hosts to monitor
	if len(hosts) == 0:
		print("Error, no hosts specified, exiting.")
		exit(1)

	# Start the wait thread thread for non blocking delay
	timer_thread = start_timer_thread(ARGS.delay)

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
		timer_thread = start_timer_thread(ARGS.delay)

		# Update host stats
		update_hosts(hosts, timeout = ARGS.delay / 2)



# Builds the command line parameter parser
def build_option_parser():

	# Brief description of script
	parser = argparse.ArgumentParser(description = 'Monitor resource usage on a number of remote hosts.')

	# Hosts to monitor file and no file
	parser.add_argument(
		'-H', '--hosts', nargs = '+', type = str,
		help = 'List of remote hosts to connect with.')
	parser.add_argument(
		'-f', '--hostfile', type = str,
		help = "Path to hostfile where hostnames are defined.")

	# Allows user to set update delay
	parser.add_argument(
		'-d', '--delay', type = float, default = 0.1, required = False,
		help = 'Set delay between updates in seconds.')

	# Return the constructed parser
	return parser



# Make this behave like a boring old c program
if __name__ == '__main__':

	# Parse command line arguments, help etc
	parser = build_option_parser()
	ARGS = parser.parse_args()

	# Run curses program
	try:
		wrapper(main)		# This is a curses application
	except KeyboardInterrupt:
		print('Received KB interrupt, quitting monitor.')
