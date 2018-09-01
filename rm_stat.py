#!/usr/bin/env python3


import rm_host
import sys
import curses
from math import ceil



# Class to contain all statistics
class resmon_stat:

	cpu = None		# CPU usage related stats


	# Constructor
	def __init__(self, source):

		# Split source into lines for parsing
		lines = source.split('\n')
		i = 0

		# Get lines that contain CPU utilisation
		cpu_source = []
		while 'cpu' in lines[i]:
			cpu_source.append(lines[i])
			i += 1

		# Initialise CPU portion of the stat file
		self.cpu = resmon_cpu(cpu_source)


	# Update method, parses a response datagram from the remote responder (a long ass string)
	def update(self, source):
		
		# Split source into lines for parsing
		lines = source.split('\n')
		i = 0

		# Get lines that contain CPU utilisation
		cpu_source = []
		while 'cpu' in lines[i]:
			cpu_source.append(lines[i])
			i += 1

		# Update cpu usage using the CPU lines
		self.cpu.update(cpu_source)


	# Just pass render onto CPU for now
	def render(self, screen):

		# Create a new window
		cores_per_line = 4

		# Render CPU info to the window
		self.cpu.render(screen, cores_per_line)

		# Return the number of lines used by this host on the screen
		return ceil(len(self.cpu.cores) / cores_per_line)



# Class serves as a container for a sample of core usage data
class resmon_cpu:

	total = None 		# Agregate readings for all CPUs
	cores = []			# Readings for individual cores

	
	# Constructor, parses a list of 'cpun' lines
	def __init__(self, source):

		# First line is the agregate line for all cores
		self.total = resmon_core(source[0])

		# Iterate over the other lines adding cores
		self.cores = []
		for i in range(1, len(source)):
			self.cores.append(resmon_core(source[i]))


	# Update method, updates CPU utilisation
	def update(self, source):

		# Check that number of strings matches core count
		if len(source) != len(self.cores) + 1:
			print("CPU core count appears to have changed. Was %d, now %d." % (len(self.cores), len(source) - 1))
			sys.exit(1)

		# Update the agregate "core" stats
		self.total.update(source[0])

		# Update the other cores
		for i in range(0, len(self.cores)):
			self.cores[i].update(source[i + 1])

	
	# Generate usage bar strings for all cores, with a certain number of cores per line (placeholder)
	def render(self, screen, cores_per_line):

		# Temporary core position math
		screen_height, screen_width = screen.getmaxyx()
		core_bar_length = int(screen_width / cores_per_line)

		# For all cores
		cursor_y, cursor_x = screen.getyx()
		initial_cursor_x = cursor_x
		for i in range(0, len(self.cores)):
			
			# Render the core to the window at the specified position
			screen.move(cursor_y, cursor_x)
			self.cores[i].render(screen, core_bar_length)

			# Calculate position of next core bar
			if i % cores_per_line == cores_per_line - 1:
				cursor_x = initial_cursor_x
				cursor_y += 1
			else:
				cursor_x += core_bar_length



# Class contains stats of a single processor
class resmon_core:

	prev_source = ''	# Source strings used for the last update

	name = ''			# Name of the CPU
	user = 0.0			# Userspace processes
	nice = 0.0			# Niced processes
	system = 0.0		# System processes
	idle = 0.0			# Idle process
	iowait = 0.0		# Waiting on IO
	irq = 0.0			# Interrupt service handlers
	softirq = 0.0		# Software interrupt handlers


	# Constructor, sets up the data structure ready for evaluation later
	def __init__(self, source):
		
		# Initialise, setting name and idle to 100%
		components = list(filter(bool, source.split(' ')))
		self.name = components[0]
		self.idle = 100.0

		# Initialise prev_source so that subsequent calls to update function correctly
		self.prev_source = source
		

	# Update state with regards to previous state
	def update(self, source):

		# Split the input strings by spaces
		val_prev = list(filter(bool, self.prev_source.split(' ')))
		val = list(filter(bool, source.split(' ')))

		# Check that core name matches
		if val[0] != self.name:
			print('Processor name appears to have changed. Was %s, now %s.' % (self.name, components[0]))
			sys.exit(1)
			
		# Get total for all fields in string
		total = 0
		for i in range(1, len(val_prev)):
			total += int(val[i]) - int(val_prev[i])

		# Calculate percentages
		ema_new = 0.5
		ema_old = 1 - ema_new
		try:
			self.user 		= (self.user * ema_old) 	+ ((float(int(val[1]) - int(val_prev[1])) / total) * ema_new * 100)
			self.nice 		= (self.nice * ema_old) 	+ ((float(int(val[2]) - int(val_prev[2])) / total) * ema_new * 100)
			self.system 	= (self.system * ema_old) 	+ ((float(int(val[3]) - int(val_prev[3])) / total) * ema_new * 100)
			self.idle 		= (self.idle * ema_old) 	+ ((float(int(val[4]) - int(val_prev[4])) / total) * ema_new * 100)
			self.iowait 	= (self.iowait * ema_old) 	+ ((float(int(val[5]) - int(val_prev[5])) / total) * ema_new * 100)
			self.irq 		= (self.irq * ema_old) 		+ ((float(int(val[6]) - int(val_prev[6])) / total) * ema_new * 100)
			self.softirq 	= (self.softirq * ema_old) 	+ ((float(int(val[7]) - int(val_prev[7])) / total) * ema_new * 100)
		except ZeroDivisionError:
			self.user = self.nice = self.system = self.iowait = self.irq = self.softirq = 0
			self.idle = 100

		# Set prev source
		self.prev_source = source


	# Renders a core bar to the curses window
	def render(self, window, length):

		# Value of each character in the bar
		chunk_value = 100 / (length - 2)
		percentage_string = '%.1f%%' % (100 - self.idle)
		
		# Bar start
		window.addch('[')

		# Color table
		col = [(self.user, curses.color_pair(3)),
			   (self.nice, curses.color_pair(5)),	
			   (self.system, curses.color_pair(2)),
			   (self.irq, curses.color_pair(4)),
			   (self.softirq, curses.color_pair(6)),
			   (self.iowait, curses.color_pair(9)),
			   (self.idle, curses.color_pair(9))]

		# Generate the usage bar
		current_col = None
		j = 0; k = 0; col_threshold = 0
		for i in range(0, length - 2):

			# Do colour stuff
			while True:
				if i * chunk_value >= col_threshold:
					col_threshold += col[k][0]
					current_col = col[k][1]
					k += 1
				else:
					break

			# Do character stuff
			if i < (length - 2) - len(percentage_string):
				if (i + 0.5) * chunk_value < 100 - self.idle: 
					window.addstr('|', current_col)
				else: 
					window.addch(' ')
			else:
				window.addstr(percentage_string[j], current_col)
				j += 1

		# End of bar
		window.addch(']')

