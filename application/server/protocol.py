# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from application.common import  PUSH_TIMEOUT,\
    MSG_FIELD_SEP, MSG_SEP, END_TERM

from socket import error as soc_err
import socket
from sessions import gameSession
import Pyro4
#import multiprocessing
#import threading

import Pyro4
from threading import Lock

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
        self.clients_gate = None # for server to call client funcs
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
            self.session = sessName #TODO
            return self.sessions[sessName].join(self)  #REELIKA to change implementation

    def newSession(self, msg):
        """
        User wants to create new session.
        @param msg: number of desired players and the name of the session we want to create
        returns False if session name already in use, session info if successful.
        """
        sessName=msg.split(MSG_SEP)[0]
        prefpl = msg.split(MSG_SEP)[1]
        if sessName in self.sessions:
            return False
        else:
            self.sessions[sessName]=gameSession(sessName, self.boards, prefpl, self.sessions)
            self.session = sessName
            return self.sessions[sessName].join(self)   #REELIKA

    def leave(self, msg):
        """Client disconnecting"""
        LOG.debug("leaving user: " + str(msg))
        self.activenames.remove(msg)
        if self.session != None and self.session in self.sessions:	#if present in session
            self.sessions[self.session].leave(msg)
        return self.users.remove(self) #Remove object, dieeee!

    def sendGuess(self, message):
        """Client sends a guess"""
        LOG.debug("guess: " + str(message))
        return self.sessions[self.session].sendGuess((str(message),str(self.uname)))

    def register(self, client_gate):
        """Client registeres gate"""
        LOG.debug("Registering notify object for client. ")
        self.clients_gate = client_gate

    def notify(self, message):
        """Uses client-side method to update board"""
        self.clients_gate.push_update_sess(message)

    def pushEnd(self, message):
        """Uses client-side method to notify end of session"""
        self.session = None
        self.clients_gate.push_end_sess(message)

    def pushStart(self, message):
        """Uses client-side method to notify start of session"""
        self.clients_gate.push_start_game(message) 

