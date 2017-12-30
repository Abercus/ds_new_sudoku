import random
from application.common import REQ_GUESS, REQ_START_SESS, MSG_FIELD_SEP, MSG_SEP, \
            PUSH_UPDATE_SESS, PUSH_END_SESSION,\
            RSP_UNKNCONTROL, RSP_OK, RSP_SESSION_ENDED
import Pyro4
# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
BUFFER_SIZE=2048

class gameSession:
    def __init__(self,name,boards,prefplayers,sess):
        '''
        A process that manages a single game session. All users added are processed in subthreads, process chooses board and handles subthreads.
        @param name: the name of the game session
        @param users: joining users in a Queue waiting to be processed in subthreads
        @param unman: global queue of users who are not managed by anything, all users in this session will be added there when session ends
        @param boards: list of all possible game boards, one is chosen at random
        '''
        self.name = name	#name of session
        self.board = boards[random.randint(0,len(boards)-1)]
        self.boardstate=self.board[2]	#board state, this shows what is locked
        self.ldboard = {}	#leaderboard
        self.subs = {}	#list of subscribers
        self.prefplayers = int(prefplayers)
        self.started = False
        self.sessions=sess
        LOG.info('New session %s started' % self.name)

    def join(self,user):
        """
        When user joins a session it's added to leaderboard and subscription list.
        When game has already started then send game state to user.
        :param user: user
        """
        self.subs[user.uname]=user	#add to people to be notified
        LOG.debug("Users subscribed: "+str(self.subs))
        self.ldboard[user.uname]=0	#add to leaderboard
        LOG.debug(self.ldboard)
        LOG.info('User %s joined session %s' % (user.uname,self.name))
        if self.started:	#if game ongoing, send info to this person
            self.send_gstate(user)
        else:	#if game not started, add to players list, check if we have enough players
            if len(self.subs)>=self.prefplayers:
                LOG.info("Game %s starting!" % self.name)
                self.started=True
                for sub in self.subs:
                    self.send_gstate(self.subs[sub]) #sends opening board to everyone
            else:
                user.notify(RSP_OK+MSG_FIELD_SEP) #tell player game not on yet!

    def send_gstate(self,user):
        """
        sends game state to new user
        """
        message=RSP_OK+MSG_FIELD_SEP+str(self.boardstate)+MSG_SEP+str(self.ldboard)
        user.notify(message)
        LOG.info('Sent update to %s' % user.uname)

    def leave(self,user):
        """
        When user wishes to leave the session, unsubscribe and remove from leaderboard.
        If there is only 1 person remaining then send notification that game is over.
        :param user: user
        """
        self.ldboard.pop(user.uname,None)
        self.subs.pop(user.uname,None)
        LOG.info('User %s leaving session %s' % (user.uname,self.name))
        if len(self.subs) <= 1:
            winpl=''
            winsc=-1
            for pl in self.ldboard:
                if self.ldboard[pl]>winsc:
                    winsc=self.ldboard[pl]
                    winpl=pl
            res=PUSH_END_SESSION+MSG_FIELD_SEP+winpl #send winner!
            LOG.info('Session %s ended' % self.name)
            for sub in self.subs:
                self.subs[sub].notify(res)
            self.sessions.pop(self.name,None)

    def process(self,message):
        """
        Processes messages which have been sent from the client.
        """
        payload=message[0]
        user=message[1]
        if payload.startswith(REQ_GUESS): #user makes guess
            m=payload.split(MSG_FIELD_SEP)[1]
            LOG.info('User %s has sent a guess: %s' % (user,str(m)))
            #payload should be 3 integers: x, y, guess (guess in str for here)
            x,y,g=int(m[0]),int(m[1]),str(m[2])
            if self.boardstate[x][y]!="-": #no guess possible here
                logging.info('User %s sent impossible guess' % user)
                pass
            elif self.board[1][x][y]!=g:
                logging.info('User %s made a wrong guess' % user)
                self.ldboard[user.uname]-=1
                #wrong guess
                res=PUSH_UPDATE_SESS+MSG_FIELD_SEP+"0"+str(x)+str(y)+str(g)+MSG_SEP+str(self.ldboard)
                for sub in self.subs:
                    self.subs[sub].notify(res)
            else:
                self.ldboard[user.uname]+=1
                logging.info("User %s made a correct guess" % user)
                self.boardstate[x][y]=g
                res=PUSH_UPDATE_SESS+MSG_FIELD_SEP+"1"+str(self.boardstate)+MSG_SEP+str(self.ldboard)
                for sub in self.subs:
                    self.subs[sub].notify(res)
                # If board has been completed send win information
                if self.boardstate==self.board[1]: #board completed!
                    logging.info("Board has been completed.")
                    winpl=''
                    winsc=-1
                    for pl in self.ldboard:
                        if self.ldboard[pl]>winsc:
                            winsc=self.ldboard[pl]
                            winpl=pl
                    res=PUSH_END_SESSION+MSG_FIELD_SEP+winpl #send winner!
                    for sub in self.subs:
                        self.subs[sub].notify(res)
                    self.sessions.pop(self.name,None)

        elif payload.startswith(REQ_START_SESS): #user wants to start session
            if not self.started:
                self.started=True
                LOG.info('Session %s starting.' % self.name)
                for sub in self.subs:
                    self.send_gstate(self.subs[sub]) #sends opening board to everyone
