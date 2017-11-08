"""
Common methods/functions/variables between server and client.
Largely copied from Seminar Task 2, changed for sudoku.
"""
# Imports----------------------------------------------------------------------
from socket import SHUT_WR, SHUT_RD
from exceptions import Exception
# TCP related constants -------------------------------------------------------
#
DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
#
# When receiving big messages in multiple blocks from the TCP stream
# the receive buffer size should be select according to amount of RAM available
# (more RAM = bigger blocks = less receive cycles = faster delivery)
TCP_RECEIVE_BUFFER_SIZE = 1024*1024
#
# Sudoku protocol constants ---------------------------------------------------
#
MAX_PDU_SIZE = 200*1024*1024 # Reasonable amount of data to store in RAM
# Requests --------------------------------------------------------------------
REQ_DISCONNECT = '0' #?
REQ_UNAME = '1'
REQ_GET_SESS = '2'
REQ_JOIN_SESS = '3'
REQ_GUESS = '5'
REQ_NEW_SESS = '6'
REQ_START_SESS = '7'
PUSH_UPDATE_SESS = '8'
PUSH_END_SESSION = '9'
PUSH_UPDATE_SCORE = '10'
CTR_MSGS = { REQ_UNAME:'Give current username',
			REQ_DISCONNECT:'Disconnect me',
			REQ_GET_SESS:'Get game session info',
			REQ_JOIN_SESS:'Join game session',
			REQ_GUESS:'Guess a field value',
			REQ_NEW_SESS:'Create new game session',
			REQ_START_SESS:'Start game session',
			PUSH_UPDATE_SESS: 'Send game field update', #For server
			PUSH_END_SESSION: 'Send game session end message', #For server
			PUSH_UPDATE_SCORE: ''
			  }
# Responses--------------------------------------------------------------------
RSP_OK = '0'
RSP_BADFORMAT = '1'
RSP_UNAME_TAKEN = '2'
RSP_UNKNCONTROL = '3'
RSP_ERRTRANSM = '4'
RSP_CANT_CONNECT = '5'
RSP_SESSION_ENDED = '6'
RSP_SESSION_TAKEN ='7'
ERR_MSGS = { RSP_OK:'No Error',
			RSP_BADFORMAT:'Malformed message',
			RSP_UNAME_TAKEN:'Username taken',
			RSP_UNKNCONTROL:'Unknown control code',
			RSP_ERRTRANSM:'Transmission Error',
			RSP_CANT_CONNECT:'Can\'t connect to server',
			RSP_SESSION_ENDED: 'Game session ended',
			RSP_SESSION_TAKEN: 'Game session name taken'
			   }
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
# Message separator for sending multiple messages------------------------------
MSG_SEP = ';'
# End symbol ------------------------------------------------------------------
term = '\n'
# Exceptions ------------------------------------------------------------------
class ProtocolError(Exception):
	'''Should be thrown internally on client or server while receiving the
	data, in case remote end-point attempts to not follow the MBoard protocol
	'''
	def __init__(self,msg):
		Exception.__init__(self,msg)
# Common methods --------------------------------------------------------------
def tcp_send(sock,data):
	'''Send data using TCP socket. When the data is sent, close the TX pipe
	@param sock: TCP socket, used to send/receive
	@param data: The data to be sent
	@returns integer,  n bytes sent and error if any
	@throws socket.errror in case of transmission error
	'''
	sock.sendall(data)
	sock.shutdown(SHUT_WR)
	return len(data)

def tcp_receive(sock,buffer_size=TCP_RECEIVE_BUFFER_SIZE):
	'''Receive the data using TCP receive buffer.
	TCP splits the big data into blocks automatically and ensures,
	that the blocks are delivered in the same order they were sent.
	Appending the received blocks into big message is usually done manually.
	In this method the receiver also expects that the sender will close
	the RX pipe after sending, denoting the end of sending
	@param buffer_size: integer, the size of the block to receive in one
			iteration of the receive loop
	@returns string, data received
	@throws socket.errror in case of transmission error,
			MBoard PDU size exceeded in case of client attempting to
			send more data the MBoard protocol allows to send in one PDU
			(MBoard request or response) - MAX_PDU_SIZE
	'''
	m = ''	  # Here we collect the received message
	# Receive loop
	while 1:
		# Receive one block of data according to receive buffer size
		block = sock.recv(TCP_RECEIVE_BUFFER_SIZE)
		# If the remote end-point did issue shutdown on the socket
		# using  SHUT_WR flag, the local end point will receive and
		# empty string in all attempts of recv method. Therefore we
		# say we stop receiving once the first empty block was received
		if len(block) <= 0:
			break
		# There is no actual limit how big the message (m) can grow
		# during the block delivery progress. Still we have to take
		# into account amount of RAM on server when dealing with big
		# messages, and one point introduce a reasonable limit of
		# MBoard PDU (MBoard request/responses).
		if ( len(m) + len(block) ) >= MAX_PDU_SIZE:
			# Close the RX pipe to prevent the remote end-point of sending
			# more data
			sock.shutdown(SHUT_RD)
			# Garbage collect the unfinished message (m) and throw exception
			del m
			raise \
				ProtocolError( \
					'Remote end-point tried to exceed the MAX_PDU_SIZE'\
					'of protocol.'\
				)

		# Appending the blocks, assembling the message
		m += block
	return m
