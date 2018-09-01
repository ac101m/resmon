#!/usr/bin/env python3


import socket
import sys



# Get command string from a socket connection
def get_command_string(connection):
	command = connection.recv(1024).decode()
	return command



# Get data string from /proc/stat
def get_raw_cpu_util():
	string = ''	

	# Open /proc/stat and read all the lines
	with open('/proc/stat', 'r') as fp:
		lines = fp.readlines()

	# Remove the interrupt line (it's big, and we don't need it)
	for line in lines:
		if 'intr' not in line:
			string = string + line

	# Return the lines
	return string



# Main routine
def main():

	# Check that name and port have been specified
	if len(sys.argv) < 3:
		sys.stderr.write('Error, not enough arguments. Stopping responder.\n')
		sys.exit(1)

	# Extract command line parameters
	name = sys.argv[1]
	port = sys.argv[2]

	# Try to create the socket object
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('', int(port)))
		s.listen(1)
	except:
		print('Failed to open socket. Stopping responder.')
		sys.exit(1)

	# Info message indicating that the responder is running
	print('Responder listening on port %s, Cntrl+C to shut down responder.' % port)

	# Go into main service loop
	while True:

		# Wait for a connection & recieve command
		connection, addr = s.accept()
		command = get_command_string(connection)
		print("Recieved '%s' from %s - " % (command, addr), end = '')

		# Return ping command
		if command == 'REQUEST_PING':
			print("Sending ping ack.")
			connection.sendall('REQUEST_PING_ACK'.encode('utf-8'))
			connection.close()			

		# Command to request cpu utilisation data (/proc/stat)
		elif command == 'REQUEST_STAT':
			print("Sending stat data.")
			connection.sendall(get_raw_cpu_util().encode('utf-8'))
			connection.close()
			
		# Command to request shutdown of remote process
		elif command == 'REQUEST_STOP':
			print('Stopping responder.')
			connection.sendall('REQUEST_STOP_ACK'.encode('utf-8'))
			connection.close()
			break;

		# Unrecognised command, quit
		else:
			print("Command '%s' not recognised, stopping responder." % command)
			connection.close()
			break;
	
	# Close the socket now that we are done with it
	s.close()	


# Make this behave like a boring old c program
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('\nRecieved KB interrupt, quitting responder.')

