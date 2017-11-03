# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from exceptions import ValueError # for handling number format exceptions
from common import __RSP_BADFORMAT, term,\
	 __MSG_FIELD_SEP, __RSP_OK, __RSP_UNAME_TAKEN,\
	__REQ_UNAME, REQ_GET_SESS
from socket import error as soc_err
# Constants -------------------------------------------------------------------
___NAME = 'Sudoku Protocol'
___VER = '0.1.0.0'
___DESC = 'Sudoku Protocol Server-Side'
___BUILT = '2017-11-02'
___VENDOR = 'Copyright (c) 2017'
# Static functions ------------------------------------------------------------
def __disconnect_client(sock):
	'''Disconnect the client, close the corresponding TCP socket
	@param sock: TCP socket to close (client socket)
	'''
	# Check if the socket is closed disconnected already ( in case there can
	# be no I/O descriptor
	try:
		sock.fileno()
	except soc_err:
		LOG.debug('Socket closed already ...')
		return
	# Closing RX/TX pipes
	LOG.debug('Closing client socket')
	# Close socket, remove I/O descriptor
	sock.close()
	LOG.info('Disconnected client')

def server_process(message,source):
	'''Process the client's message, modify the board if needed
		@param message: string, protocol data unit received from client
		@param source: tuple ( ip, port ), client's socket address
		@returns string, response to send to client
	'''
	LOG.debug('Received request [%d bytes] in total' % len(message))
	if len(message) < 2:
		LOG.debug('Not enough data received from %s ' % message)
		return __RSP_BADFORMAT
	LOG.debug('Request control code (%s)' % message[0])
	if message.startswith(__REQ_GET_SESS + __MSG_FIELD_SEP):
		pass
	else:
		LOG.debug('Unknown control message received: %s ' % message)
		return __RSP_UNKNCONTROL
def process_uname(sock, source, unman, activenames):
	#get username, check for duplicates
	m = tcp_receive(client_socket)
	if m.startswith(__REQ_UNAME):
		m=m.split(__MSG_FIELD_SEP)[1]
		while m in activenames:
			try:
				tcp_send(client_socket, __RSP_UNAME_TAKEN)
				m=tcp_teceive(client_socket)
				m=m.split(__MSG_FIELD_SEP)[1]
			except (soc_error):
				LOG.info('Client failed to pick username from %s:%d' % source)
				__disconnect_client(client_socket)
				return
	unmanaged.put((m,client_socket,source))
	tcp_send(client_socket,__RSP_OK)
