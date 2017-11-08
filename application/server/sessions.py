import threading
from multiprocessing import Queue
import socket
from random import  random
import Queue
from application.common import REQ_GUESS, REQ_START_SESS, MSG_FIELD_SEP, \
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
	outboxes=[]	#messages to clients, one for each client
	while True:
		if not users.empty():
			outbox=Queue.Queue()
			outboxes.append(outbox)
			threading.Thread(target=sesThread, args=(users.get(),info,inbox,outbox,unman)).start()
		if not inbox.empty():
			m=process(inbox.get(),info)
			if len(m)>0: #check that message was OK
				for ob in outboxes:
					ob.put(m) #add message to be sent to all connected clients
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
			res=MSG_FIELD_SEP.join([PUSH_SESS_UPDATE]+[0,x,y,g]+list(info.ldboard))
		else:
			info.ldboard[user]+=1
			res=MSG_FIELD_SEP.join([PUSH_SESS_UPDATE]+[1,x,y,g]+list(info.ldboard))
	return res
def sesThread(client, info, inbox, outbox, unman):
	'''
	'''
	pass
