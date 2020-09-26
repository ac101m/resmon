#!/usr/bin/env python3


import rm_host
import sys
import curses
from math import ceil

from utils import vec2
from utils import mem_string



# Container class for host resource utilisation data
class resmon_stat:

	cpu = None		# CPU usage related stats
	mem = None


	# Constructor
	def __init__(self, source):

		# Split source into lines for parsing
		lines = source.split('\n')

		# Get lines that contain CPU utilisation
		cpu_source = []
		mem_source = []
		for line in lines:
			if 'cpu' in line: cpu_source.append(line)
			if 'Mem' in line: mem_source.append(line)
			if 'Buffers' in line: mem_source.append(line)
			if 'Cached' in line: mem_source.append(line)
			if 'Swap' in line: mem_source.append(line)

		# Initialise CPU and memory utilisation data
		self.cpu = resmon_cpu(cpu_source)
		self.mem = resmon_memory(mem_source)


	# Update method, parses a response datagram from the remote responder (a long ass string)
	def update(self, source):

		# Split source into lines for parsing
		lines = source.split('\n')

		# Get lines that contain CPU utilisation
		cpu_source = []
		mem_source = []
		for line in lines:
			if 'cpu' in line: cpu_source.append(line)
			if 'Mem' in line: mem_source.append(line)
			if 'Buffers' in line: mem_source.append(line)
			if 'Cached' in line: mem_source.append(line)
			if 'Swap' in line: mem_source.append(line)

		# Initialise CPU and memory utilisation data
		self.cpu.update(cpu_source)
		self.mem.update(mem_source)


	# Render CPU and memory
	def render(self, screen, position, width):

		# Calculate the number of cores per line
		cores_per_line = 2
		core_count = len(self.cpu.cores)
		while True:
			if (core_count / cores_per_line) < 6:
				if (core_count % cores_per_line) == 0:
					break
			cores_per_line += 1

		# Work out the size of display bars
		core_bar_length = int(width / cores_per_line)
		core_line_length = core_bar_length * cores_per_line
		mem_bar_length = int(core_line_length / 2)

		# Render memory info
		mem_position = vec2(position.x + (core_line_length - mem_bar_length), position.y)
		mem_lines = self.mem.render(screen, mem_position, mem_bar_length)

		# Render CPU info to window
		cpu_position = vec2(position.x, position.y + mem_lines)
		cpu_lines = self.cpu.render(screen, cpu_position, width, cores_per_line)

		# Return the vertical size of the render
		return cpu_lines + mem_lines



# Container class for memory utilisation data
class resmon_memory:

	# Memory
	mem_total = None
	mem_free = None
	mem_avail = None
	mem_buf = None
	mem_cache = None
	mem_user = None

	# Page file
	swap_total = None
	swap_free = None


	# Constructor, initialises data from source string
	def __init__(self, source):

		# Just call update
		self.update(source)


	# Update from source
	def update(self, source):

		# Memory and swap usage
		for line in source:
			if 'MemTotal' in line: 		self.mem_total 		= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'MemFree' in line: 		self.mem_free 		= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'MemAvailable' in line:	self.mem_avail 		= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'Buffers' in line:		self.mem_buf 		= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'Cached' in line:		self.mem_cache 		= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'SwapTotal' in line:		self.swap_total 	= int(list(filter(bool, line.split(' ')))[1]) * 1024
			if 'SwapFree' in line:		self.swap_free 		= int(list(filter(bool, line.split(' ')))[1]) * 1024

		# User process memory
		self.mem_user = (self.mem_total - self.mem_free) - (self.mem_cache + self.mem_buf)


	# Render memory and swap bars
	def render(self, screen, position, length):

		# Draw the memory bar
		self.render_mem(screen, position, length)

		# Draw the swap bar
		swap_position = vec2(position.x, position.y + 1)
		self.render_swap(screen, swap_position, length)

		# Return number of lines used
		return 2


	# Render memory bar
	def render_mem(self, screen, position, length):

		# Segment value
		chunk_value = self.mem_total / (length - 2)

		# Generate usage string
		usage_string = '%s/%s' % (mem_string(self.mem_user), mem_string(self.mem_total))

		# Color table for RAM
		col = [(self.mem_user, curses.color_pair(3)),
			   (self.mem_buf, curses.color_pair(5)),
			   (self.mem_cache, curses.color_pair(4)),
			   (self.mem_free, curses.color_pair(9))]

		# Print the start of the bar
		label = 'Mem '
		screen.move(position.y, position.x - len(label))
		screen.addstr(label)
		screen.addstr('[')

		# Draw the bar
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
			if i < (length - 2) - len(usage_string):
				if (i + 0.5) * chunk_value < self.mem_total - self.mem_free:
					screen.addstr('|', current_col)
				else:
					screen.addstr(' ')
			else:
				screen.addstr(usage_string[j], current_col)
				j += 1

		# Close the bar
		screen.addstr(']')


	# Render swap bar
	def render_swap(self, screen, position, length):

		# Print the start of the bar
		label = 'Swap '
		screen.move(position.y, position.x - len(label))
		screen.addstr(label)
		screen.addstr('[')

		# Segment value
		segment_value = self.swap_total / (length - 2)
		swap_used = self.swap_total - self.swap_free
		usage_string = '%s/%s' % (mem_string(swap_used), mem_string(self.swap_total))

		# Draw the bar
		current_col = curses.color_pair(3)
		j = 0; k = 0
		for i in range(0, length - 2):

			# Do color stuff
			if (i + 0.5) * segment_value >= self.swap_total - self.swap_free:
				current_col = curses.color_pair(9)

			# Do character stuff
			if i < (length - 2) - len(usage_string):
				if (i + 0.5) * segment_value < self.swap_total - self.swap_free:
					screen.addstr('|', current_col)
				else:
					screen.addstr(' ')
			else:
				screen.addstr(usage_string[j], current_col)
				j += 1

		# Close the bar
		screen.addstr(']')



# Container class for cpu utilisation data
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
	def render(self, screen, position, width, cores_per_line):

		# Temporary core position math
		core_bar_length = int(width / cores_per_line)

		# For all cores
		core_position = vec2(position.x, position.y)
		for i in range(0, len(self.cores)):

			# Render the core to the window at the specified position
			self.cores[i].render(screen, core_position, core_bar_length)

			# Calculate position of next core bar
			if i % cores_per_line == cores_per_line - 1:
				core_position.x = position.x
				core_position.y += 1
			else:
				core_position.x += core_bar_length

		# Return the number of lines used for cores
		return ceil(len(self.cores) / cores_per_line)



# Container class for the single core utilisation data
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
	def render(self, screen, position, length):

		# Value of each character in the bar
		chunk_value = 100 / (length - 2)
		percentage_string = '%.1f%%' % (100 - self.idle)

		# Color table
		col = [(self.user, curses.color_pair(3)),
			   (self.nice, curses.color_pair(5)),
			   (self.system, curses.color_pair(2)),
			   (self.irq, curses.color_pair(4)),
			   (self.softirq, curses.color_pair(6)),
			   (self.iowait, curses.color_pair(9 if curses.COLORS > 9 else 0)),
			   (self.idle, curses.color_pair(9 if curses.COLORS > 9 else 0))]

		# Move the cursor and begin rendering
		screen.move(position.y, position.x)
		screen.addstr('[')

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
					screen.addstr('|', current_col)
				else:
					screen.addstr(' ')
			else:
				screen.addstr(percentage_string[j], current_col)
				j += 1

		# End of bar
		screen.addstr(']')
