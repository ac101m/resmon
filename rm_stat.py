#!/usr/bin/env python3


import rm_host
import sys



# Class to contain all statistics
class resmon_stat:

	cpu = None			# CPU usage related stats
	

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



# Class serves as a container for a sample of core usage data
class resmon_cpu:

	total = None 		# Agregate readings for all CPUs
	core = []			# Readings for individual cores

	
	# Constructor, parses a list of 'cpun' lines
	def __init__(self, source):

		# First line is the agregate line for all cores
		self.total = resmon_core(source[0])

		# Iterate over the other lines adding cores
		for i in range(1, len(source)):
			self.core.append(resmon_core(source[i]))


	# Update method, updates CPU utilisation
	def update(self, source):
		
		# Check that number of strings matches core count
		if len(source) != len(self.core) + 1:
			print("CPU core count appears to have changed. Was %d, now %d." % (len(self.core), len(source) - 1))
			sys.exit(1)

		# Update the agregate "core" stats
		self.total.update(source[0])

		# Update the other cores
		for i in range(0, len(self.core)):
			self.core[i].update(source[i + 1])



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


	# Constructor, parses a single 'cpun' line
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
		components_prev = list(filter(bool, self.prev_source.split(' ')))
		components = list(filter(bool, source.split(' ')))

		# Check that core name matches
		if components[0] != self.name:
			print('Processor name appears to have changed. Was %s, now %s.' % (self.name, components[0]))
			sys.exit(1)
			
		# Get total for all fields in string
		total = 0
		for i in range(1, len(components_prev)):
			total += int(components[i]) - int(components_prev[i])

		# Calculate percentages
		self.user = (float(int(components[1]) - int(components_prev[1])) / total) * 100
		self.nice = (float(int(components[2]) - int(components_prev[2])) / total) * 100
		self.system = (float(int(components[3]) - int(components_prev[3])) / total) * 100
		self.idle = (float(int(components[4]) - int(components_prev[4])) / total) * 100
		self.iowait = (float(int(components[5]) - int(components_prev[5])) / total) * 100
		self.irq = (float(int(components[6]) - int(components_prev[6])) / total) * 100
		self.softirq = (float(int(components[7]) - int(components_prev[7])) / total) * 100

		# Set prev source
		self.prev_source = source
		
