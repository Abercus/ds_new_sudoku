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
REQ_UNAME = '1'
REQ_GET_SESS = '2'
REQ_JOIN_SESS = '3'
REQ_QUIT_SESS = '4'
REQ_GUESS = '5'
REQ_NEW_SESS = '6'
REQ_START_SESS = '7'
PUSH_UPDATE_SESS = '8'
PUSH_END_SESSION = '9'
PUSH_TIMEOUT = '0'
CTR_MSGS = { REQ_UNAME:'Give current username',
			REQ_GET_SESS:'Get game session info',
			REQ_JOIN_SESS:'Join game session',
			REQ_GUESS:'Guess a field value',
			REQ_QUIT_SESS:'Quit session',
			REQ_NEW_SESS:'Create new game session',
			REQ_START_SESS:'Start game session',
			PUSH_UPDATE_SESS: 'Send game field update',	#For server
			PUSH_END_SESSION: 'Send game session end message',	#For server
			PUSH_TIMEOUT: 'Client timed out, disconnected'	#For server
			  }
# Responses--------------------------------------------------------------------
RSP_OK = '0'
RSP_UNAME_TAKEN = '2'
RSP_UNKNCONTROL = '3'
RSP_SESSION_ENDED = '6'
RSP_SESSION_TAKEN ='7'
RSP_OK_GET_SESS = '8'
ERR_MSGS = { RSP_OK:'No Error',
			RSP_UNAME_TAKEN:'Username taken',
			RSP_UNKNCONTROL:'Unknown control code',
			RSP_SESSION_ENDED: 'Game session ended',
			RSP_SESSION_TAKEN: 'Game session name taken',
			RSP_OK_GET_SESS: 'Session list'
			   }
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
# Message separator for sending multiple messages------------------------------
MSG_SEP = ';'

END_TERM = "!"