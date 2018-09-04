#!/usr/bin/env python3


# Simple point class, used all over the place
class vec2:
	x = None
	y = None

	def __init__(self, x_init, y_init):
		self.x = x_init
		self.y = y_init


# Function for generating a memory string from a large value in bytes
def mem_string(value_B):

	sequence = ['B', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

	value = value_B
	for i in range(0, len(sequence)):
		if (value < 1024) | (i == len(sequence) - 1):
			return '%.1f%s' % (value, sequence[i])
		else:
			value /= 1024

