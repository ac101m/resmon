#!/usr/bin/env python3


import socket
import sys


# Get command string from a socket
def get_command_string(connection):
	command = connection.recv(1024).decode()
	return command



# Get data string from /proc/stat
def get_data_string():
	return 'Hello world'



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
	
	# Wait for a connection
	print('%s:%s - Waiting for connection... ' % (name, port), end = ''); sys.stdout.flush()
	connection, addr = s.accept()
	print('Established.')

	# Go into main service loop
	while True:

		# Get the command string from the socket
		command = get_command_string(connection)

		# Empty command = quit
		if not command:
			break
		
		# Command to request
		elif command == 'RESPOND':
			connection.sendall(get_data_string().encode('utf-8'))

		# Command was not recognised
		else:
			print('Command %s not recognised.' % command)
			sys.exit(1)

	# Close the socket
	print('%s - Server exiting.' % (name))
	connection.close()



# Make this behave like a boring old c program
if __name__ == '__main__':
	main()
