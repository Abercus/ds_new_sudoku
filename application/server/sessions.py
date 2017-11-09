import threading
from multiprocessing import Queue
import socket
from random import  random
import Queue
from application.common import REQ_GUESS, REQ_START_SESS, MSG_FIELD_SEP, MSG_SEP, \
			PUSH_UPDATE_SESS, PUSH_UPDATE_SCORE, PUSH_END_SESSION,\
			RSP_UNKNCONTROL, RSP_OK, RSP_SESSION_ENDED, RSP_BADFORMAT

def sesProcess(name, users, unman, boards):
	'''
	A process that manages a single game session. All users added are processed in subthreads, process chooses board and handles subthreads.
	@param name: the name of the game session
	@param users: joining users in a Queue waiting to be processed in subthreads
	@param unman: global queue of users who are not managed by anything, all users in this session will be added there when session ends
	@param boards: list of all possible game boards, one is chosen at random
	'''
	board = boards[random.randInt(len(boards))]
	info = {}	#dictionary for easier variable management in functions
	info["board"]=board
	info["boardstate"]=board[2]	#board state, this shows what is locked
	info["started"] = False	#whether the game has been started or in waiting mode
	info["ldboard"] = []	#leaderboard
	inbox=Queue.Queue()	#messages from clients
	subs = []	#list of subscribers
	while True:
		if not users.empty():
			t=threading.Thread(target=sesThread, args=(users.get(),info,inbox,unman))
			t.start()
			subs.append(t)
		if not inbox.empty():
			m=process(inbox.get(),info)
			if len(m)>0: #check that message was OK
				for s in subs:
					s.notify(m) #add message to be sent to all connected clients
				if m.startswith(PUSH_SESS_ENDED):
					return #Game over!
def process(message, info):
	'''
	Processes messages left in inbox
	'''
	payload=message[0]
	user=message[1]
	res=""
	if payload.startswith(REQ_GUESS): #otherwise ignore noise
		m=payload.split(MSG_FIELD_SEP)[1]
		#payload should be 3 integers: x, y, guess
		x,y,g=int(m[0]),int(m[1]),int(m[2])
		if info.boardstate[x][y]!="-" or info.board[1][x][y]!=g:
			info.ldboard[user]-=1
			#invalid or wrong guess
			res=MSG_FIELD_SEP.join([PUSH_SESS_UPDATE]+[0,x,y,g]+MSG_SEP+list(info.ldboard))
		else:
			info.ldboard[user]+=1
			res=MSG_FIELD_SEP.join([PUSH_SESS_UPDATE]+[1,x,y,g]+MSG_SEP+list(info.ldboard))
	return res
class sesThread:
	def __init__(client, info, inbox, unman):
		'''
		Deals with specific client connected to specific game session
		@param client: 
		@param 
		'''
		Thread.__init__(self)
		self.address=client[2]
		self.socket=client[1]
		self.uname=client[0]
		self.info=info
		self.inbox=inbox
		self.unman=unman
	def notify(self,message):
		__session_send(message)
	def __session_send(self,msg):
		m = msg + MSG_SEP
		with self.send_lock:
			r = False
			try:
				self.socket.sendall(m)
				r = True
			except KeyboardInterrupt:
				self.socket.close()
				LOG.info( 'Ctrl+C issued, disconnecting client %s:%d'\
						  '' % self.address )
			except soc_err as e:
				if e.errno == 107:
					LOG.warn( 'Client %s:%d left before server could handle it'\
					'' %  self.address )
				else:
					LOG.error( 'Error: %s' % str(e) )
				self.socket.close()
				LOG.info( 'Client %s:%d disconnected' % self.address )
			return r

	def __session_rcv(self):
		m,b = '',''
		try:
			b = self.socket.recv(BUFFER_SIZE)
			m += b
			while len(b) > 0 and not (b.endswith(MSG_FIELD_SEP)):
				b = self.socket.recv(BUFFER_SIZE)
				m += b
			if len(b) <= 0:
				self.socket.close()
				LOG.info( 'Client %s:%d disconnected' % self.address )
				m = ''
			m = m[:-1]
		except KeyboardInterrupt:
			self.socket.close()
			LOG.info( 'Ctrl+C issued, disconnecting client %s:%d' % self.address )
			m = ''
		except soc_err as e:
			if e.errno == 107:
				LOG.warn( 'Client %s:%d left before server could handle it'\
				'' %  self.address )
			else:
				LOG.error( 'Error: %s' % str(e) )
			self.socket.close()
			LOG.info( 'Client %s:%d disconnected' % self.address )
			m = ''
		return m

	def __protocol_rcv(self,message):
		LOG.debug('Received request [%d bytes] in total' % len(message))
		if len(message) < 2:
			LOG.debug('Not enough data received from %s ' % message)
			return RSP_BADFORMAT
		LOG.debug('Request control code (%s)' % message[0])
		if message.startswith(REQ_GUESS + MSG_FIELD_SEP):
			message=message.split(MSG_FIELD_SEP)
			msg = message[1]
			LOG.debug('Client %s:%d sent guess: '\
				'%s' % (self.addr+((msg[:60]+'...' if len(msg) > 60 else msg),)))
			self.inbox.put(message)
		else:
			LOG.debug('Unknown control message received: %s ' % message)
			return RSP_UNKNCONTROL

	
	def run(self):
		while True: #No sending, only receiving.
			m = self.__session_rcv()
			if len(m) <= 0:
				break
			message = self.__protocol_rcv(m)
