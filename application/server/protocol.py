# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from application.common import  PUSH_TIMEOUT,\
    MSG_FIELD_SEP, MSG_SEP, RSP_OK, RSP_UNAME_TAKEN, RSP_SESSION_ENDED,\
    RSP_SESSION_TAKEN, RSP_UNKNCONTROL,PUSH_END_SESSION,REQ_QUIT_SESS,\
    REQ_UNAME, REQ_GET_SESS, REQ_JOIN_SESS, REQ_NEW_SESS, REQ_START_SESS, REQ_GUESS

from socket import error as soc_err
import socket
from sessions import gameSession
#import multiprocessing
import threading



# Constants -------------------------------------------------------------------
___NAME = 'Sudoku Protocol'
___VER = '0.1.0.0'
___DESC = 'Sudoku Protocol Server-Side'
___BUILT = '2017-11-02'
___VENDOR = 'Copyright (c) 2017'
bsize=2048
# Static functions ------------------------------------------------------------
def disconnect_client(sock):
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

class serProcess(threading.Thread):
    def __init__(self,sock,sessions,anames,boards):
        '''
        Manages each user that has connected to server but is not connected to a game session. User can check game session list, join a game session or start a new one.
        @param guest: (client_name,client_socket, source) tuple containing information about client
        @param sesss: list of all active game sessions. Deletions managed by serThread1, additions by serThread2, list in Python is thread safe.
        @param sessions: synchronized list of available game sessions
        @param anames: usernames in active use
        @param boards: all possible game boards
        '''
        threading.Thread.__init__(self)
        self.uname=''
        self.sock=sock
        self.sessions=sessions
        self.session=None
        self.activenames=anames
        self.boards=boards
        LOG.info('Managing new user')

    def run(self):
        while True:
            try:
                m = self.sock.recv(bsize)
                LOG.info('Received from user %s' % self.uname)
                if m.startswith(REQ_UNAME+MSG_FIELD_SEP):
                    if self.uname != '':
                        LOG.debug('User %s tried to change his/her existing username, ignoring...' % self.uname)
                        continue
                    m=m.split(MSG_FIELD_SEP)[1]
                    if m.endswith(MSG_SEP):
                        m=m[:-1]
                    while m in self.activenames:
                        try:
                            self.sock.sendall(RSP_UNAME_TAKEN+MSG_FIELD_SEP)
                            self.sock.settimeout(60)
                            m=self.sock.recv(bsize)
                            m=m.split(MSG_FIELD_SEP)[1]
                            if m.endswith(MSG_SEP):
                                m=m[:-1]
                        except (soc_err or socket.timeout):
                            LOG.info('Client failed to pick username')
                            disconnect_client(self.sock)
                            return
                    self.sock.settimeout(None)
                    LOG.info('Client picked username %s' % m)
                    self.uname=m
                    self.sock.sendall(RSP_OK+MSG_FIELD_SEP)
                    self.activenames.append(self.uname)

                elif m.startswith(REQ_GET_SESS+MSG_FIELD_SEP):
                    LOG.info('User %s requests sessions' % self.name)
                    ress=list(self.sessions.keys()) #list of session names
                    res=RSP_OK+MSG_FIELD_SEP+str(ress)
                    print(res)
                    self.sock.sendall(res)
                elif m.startswith(REQ_JOIN_SESS+MSG_FIELD_SEP):
                    message=m.split(MSG_FIELD_SEP)[1]
                    LOG.info('User %s wants to join session %s' % (self.name,message))
                    if message not in self.sessions: #if game session no longer available, must have ended
                        self.sock.sendall(RSP_SESSION_ENDED+MSG_FIELD_SEP)
                    else:
                        self.sessions[message].join(self) #guest sent to be managed by session, this thread has fulfilled its purpose
                        self.session=message
                elif m.startswith(REQ_NEW_SESS+MSG_FIELD_SEP):
                    LOG.info('User %s requests new session' % self.uname)
                    message=m.split(MSG_FIELD_SEP)[1].split(MSG_SEP)[0]
                    prefpl =m.split(MSG_SEP)[1]
                    if message in self.sessions: #session with this name already exists
                        self.sock.sendall(RSP_SESSION_TAKEN+MSG_FIELD_SEP)
                    else: #creates new process for new session
                        self.sessions[message]=gameSession(message,self.boards,prefpl,self.sessions)
                        self.sessions[message].join(self)
                        self.session=message
                elif m.startswith(REQ_GUESS+MSG_FIELD_SEP):
                    self.sessions[self.session].process((m,self))
                elif m.startswith(REQ_START_SESS+MSG_FIELD_SEP):
                    self.sessions[self.session].process((m,self))
		elif m.startswith(REQ_QUIT_SESS+MSG_FIELD_SEP):
                    self.sessions[self.session].leave(self)
                else:
                    LOG.debug('Unknown control message received: %s ' % m)
                    self.sock.sendall(RSP_UNKNCONTROL+MSG_FIELD_SEP)
            except Exception as e:
                LOG.info('Problem with connection, dropping user %s' % self.uname)
                LOG.debug(e)
                if self.uname in self.activenames:
                    self.activenames.remove(self.uname)
                    if self.session:# if user was connected to a session
                        self.sessions[self.session].leave(self)
                disconnect_client(self.sock)
                return
    def notify(self, message):
        if message.startswith(PUSH_END_SESSION):
            self.session=None
        self.sock.sendall(message)
