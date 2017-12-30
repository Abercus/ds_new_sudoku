# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from application.common import  PUSH_TIMEOUT,\
    MSG_FIELD_SEP, MSG_SEP, RSP_OK, RSP_UNAME_TAKEN, RSP_SESSION_ENDED,\
    RSP_SESSION_TAKEN, RSP_UNKNCONTROL,PUSH_END_SESSION,REQ_QUIT_SESS,\
    REQ_UNAME, REQ_GET_SESS, REQ_JOIN_SESS, REQ_NEW_SESS, REQ_START_SESS, REQ_GUESS,\
    END_TERM

from socket import error as soc_err
import socket
from sessions import gameSession
import Pyro4
#import multiprocessing
#import threading



# Constants -------------------------------------------------------------------
___NAME = 'Sudoku Protocol'
___VER = '0.1.0.0'
___DESC = 'Sudoku Protocol Server-Side'
___BUILT = '2017-11-02'
___VENDOR = 'Copyright (c) 2017'
bsize=2048

@Pyro4.expose
class Client():#threading.Thread):
    def __init__(self,sessions,anames,boards,users):
        '''
        Manages each user that has connected to server but is not connected to a game session. User can check game session list, join a game session or start a new one.
        @param sessions: synchronized list of available game sessions
        @param anames: usernames in active use
        @param boards: all possible game boards
        @param users: list of active user objects, used to remove link to object
        '''
        #threading.Thread.__init__(self)
        self.uname=''
        #self.sock=sock
        self.sessions=sessions
        self.session=None
        self.activenames=anames
        self.boards=boards
        self.users=users
        LOG.info('Managing new user')

    def chooseName(self, name):
        """
        User wants to choose username.
        @param name: the name he wants
        returns True if username is chosen, False if username unsuitable or already chosen
        """
        if self.uname != '':
            LOG.debug("User %s tried to change own username, ignoring..." % self.uname)
            return False    #Fail
        if name in self.activenames:
            LOG.info("User tried to choose existing username %s, ignoring..." % name)
            return False    #Fail
        else:
            LOG.info('User %s has chosen name.' % name)
            self.uname = name
            self.activenames.append(name)
            return True #Success
    def getSessions(self):
        #Client wants list of active sessions, returns list of active session names
        return list(self.sessions.keys())
    def joinSession(self, sessName):
        """
        User wants to join session.
        @param sessName: the name of the session he wants to join.
        returns False if wrong name or session already over, session info if successful.
        """
        if sessName not in self.sessions:
            return False
        else:
            this.session = self.sessions[sessName]
            return this.session.join(self)  #REELIKA to change implementation
    def newSession(self, sessName):
        """
        User wants to create new session.
        @param sessName: the name of the proposed new session.
        returns False if session name already in use, session info if successful.
        """
        if sessName in self.sessions:
            return False
        else:
            self.sessions[sessName]=gameSession(sessName, self.boards, prefpl, self.sessions)
            self.session = sessName
            return self.sessions[sessName].join(self)   #REELIKA
    def leave(self):
        """Client disconnecting"""
        self.activenames.remove(self.uname)
        self.users.remove(self) #Remove object, dieeee!

    """
    def run(self):
        """
        When user has connected to dedicated server.
        Respond to user requests such has choosing a name, joining a session, create a new session,
        getting session lists
        """
                    # User sends a guess for game
                    elif m.startswith(REQ_GUESS+MSG_FIELD_SEP):
                        self.sessions[self.session].process((m,self))
                    # User wants to start a session
                    elif m.startswith(REQ_START_SESS+MSG_FIELD_SEP):
                        self.sessions[self.session].process((m,self))
                    # User wants to quit a session
                    elif m.startswith(REQ_QUIT_SESS+MSG_FIELD_SEP):
                        self.sessions[self.session].leave(self)
                    else:
                        LOG.debug('Unknown control message received: %s ' % m)
                        self.sock.sendall(RSP_UNKNCONTROL+MSG_FIELD_SEP+END_TERM)
            except Exception as e:
                LOG.info('Problem with connection, dropping user %s' % self.uname)
                LOG.debug(e)
                if self.uname in self.activenames:
                    self.activenames.remove(self.uname)
                if self.session:# if user was connected to a session
                    self.sessions[self.session].leave(self)
                disconnect_client(self.sock)
                return
    """

    """
    def notify(self, message):
        """
        #Method to notify user of changes
        #To be deprecated once client-side methods exist, to be managed by session
        """
        if message.startswith(PUSH_END_SESSION):
            self.session=None
        self.sock.sendall(message + END_TERM)
    """
