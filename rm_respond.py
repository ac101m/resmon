#!/usr/bin/env python3


import socket
import sys


# Get command string from a socket
def get_command_string(connection):
	command = connection.recv(1024).decode()
	return command



# Get data string from /proc/stat
def get_raw_cpu_util():
	with open('/proc/stat', 'r') as statfile:
		data = statfile.read()
	return data



# Main routine
def main():

	# Extract command line parameters
	name = sys.argv[1]
	port = sys.argv[2]

	# Check that the port has been specified
	if len(sys.argv) < 3:
		sys.stderr.write('Error, not enough arguments. Closing.')
		sys.exit(1)

	# Create socket object
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', int(port)))
	s.listen(1)
	connection, addr = s.accept()

	# Go into main service loop
	while True:

		# Get the command, then handle it
		command = get_command_string(connection)
		
		# Command to request
		if command == 'REQUEST_CPU_UTIL':
			connection.sendall(get_raw_cpu_util().encode('utf-8'))

		# Empty command = stop
		elif command:
			print('Recieved null command, stopping responder.')
			break
			
		# Command was not recognised = stop
		else:
			print('Command %s not recognised, stopping responder.' % command)
			break;

	# Close the connection
	connection.close()
	


# Make this behave like a boring old c program
if __name__ == '__main__':
	main()
