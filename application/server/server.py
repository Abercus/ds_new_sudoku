#!/usr/bin/python
from protocol import __disconnect_client

# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports ---------------------------------------------------------------------
import threading
from multiprocessing import Queue
import protocol
from application.common import tcp_receive, tcp_send
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as soc_error
from sys import exit
#import Queue
# Constants -------------------------------------------------------------------
___NAME = 'Sudoku Server'
___VER = '0.1.0.0'
___DESC = 'Sudoku Server (TCP version)'
___BUILT = '2017-11-01'
___VENDOR = 'Copyright (c) 2017'

# Private methods -------------------------------------------------------------
def __info():
	return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
# Not a real main method-------------------------------------------------------
def server_main(args):
	'''Runs the Mboard server
	@param args: ArgParse collected arguments
	'''
	sudokus="sudoku_db" #Make this ArgParsable?

	# Starting server
	LOG.info('%s version %s started ...' % (___NAME, ___VER))

	# Declaring TCP socket
	__server_socket = socket(AF_INET,SOCK_STREAM)
	LOG.debug('Server socket created, descriptor %d' % __server_socket.fileno())
	# Bind TCP Socket
	try:
		__server_socket.bind(("127.0.0.1",7777))
	except soc_error as e:
		LOG.error('Can\'t start MBoard server, error : %s' % str(e) )
		exit(1)
	LOG.debug('Server socket bound on %s:%d' % __server_socket.getsockname())
	# Put TCP socket into listening state
	__server_socket.listen(7000)
	LOG.info('Accepting requests on TCP %s:%d' % __server_socket.getsockname())

	# Declare client socket, set to None
	client_socket = None
	# Create Queue for users that are not managed by anyone
	unmanaged = Queue()
	# Create list for all names in active use
	names = []
	# Create thread that manages user list
	umanager=threading.Thread(target=protocol.serThread1, args=(unmanaged,[])) #TODO add sudokus to args, I removed it
	umanager.start()
	# Serve forever
	while 1:
		try:
			LOG.debug('Awaiting new client connections ...')
			# Accept client's connection store the client socket into
			# client_socket and client address into source
			client_socket,source = __server_socket.accept()
			LOG.debug('New client connected from %s:%d' % source)
			try:
				protocol.process_uname(client_socket,source,unmanaged,names)
			except (soc_error) as e:
				# In case we failed in the middle of transfer we should report error
				LOG.error('Interrupted receiving the data from %s:%d, '\
						  'error: %s' % (source+(e,)))
				# ... and close socket
				__disconnect_client(client_socket)
				client_socket = None
				# ... and proceed to next client waiting in to accept
				continue
			client_socket=None


		except KeyboardInterrupt as e:
			LOG.debug('Ctrl+C issued ...')
			LOG.info('Terminating server ...')
			break

	# If we were interrupted, make sure client socket is also closed
	if client_socket != None:
		__disconnect_client(client_socket)

	# Close server socket
	__server_socket.close()
	LOG.debug('Server socket closed')


server_main('') #remove in final version ;)
