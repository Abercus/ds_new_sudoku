# Setup Python logging --------------------------------------------------------
import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
LOG = logging.getLogger()

# Imports----------------------------------------------------------------------
from application.common import TCP_RECEIVE_BUFFER_SIZE, \
    RSP_OK, RSP_UNKNCONTROL, \
    REQ_UNAME, REQ_GET_SESS, REQ_JOIN_SESS, REQ_NEW_SESS, \
    MSG_FIELD_SEP, MSG_SEP, RSP_UNAME_TAKEN,RSP_OK_GET_SESS, RSP_SESSION_ENDED, RSP_SESSION_TAKEN,\
    PUSH_END_SESSION, PUSH_UPDATE_SESS

import tkFont as tkfont
import tkMessageBox as tm
from Queue import Queue
from Tkinter import *
from threading import Thread
from time import sleep

from application.client.gameboard import GameBoard
from gui_parts import LoginFrame, ConnectFrame, SessionsFrame
from ast import literal_eval
import Pyro4
import Pyro4.naming



class Application(Tk):
    '''
    Launch the main part of the GUI
    '''
    def __init__(self, client, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Sudoku Game')
        self.geometry('490x350')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        # Assign client object
        self.client = client
        # Create Queue. This queue will be used by server listening thread and update_gui thread
        self.queue = Queue()
        # Array to store the threads
        self.threads = []
        #TODO using
        self.__callback_gate = None
        self.__callback_receiver = Pyro4.Daemon()

        # Main container to store parts of the gui
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Array of frames to store parts of the gui
        self.frames = {}
        self.fnames = (LoginFrame, ConnectFrame, SessionsFrame, GameBoard)
        for F in self.fnames:
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show LoginFrame first
        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        '''
        Show frame by name
        @param page_name: name of the frame to show
        '''
        self.frame = self.frames[page_name]
        self.fname = page_name
        self.frame.tkraise()

    def connect_server(self, srv_addr = ''):
        '''
        Connect to the server
        @param srv_addr: server address
        '''

        # Default server address is 127.0.0.1:7777
        if srv_addr == '':
            srv_addr = '127.0.0.1'+':'+'7777'

        a, b = srv_addr.split(':')
        if self.client.connect((a,int(b))):

            #TODO register gate
            on_push_update_sess = lambda x: self.push_update_sess(x)
            on_push_end_sess = lambda x: self.push_end_sess(x)
            self.__callback_gate = ClientCallbackGate(on_push_update_sess, on_push_end_sess)
            self.__callback_receiver.register(self.__callback_gate)
            self.client.server.register(self.__callback_gate)

            tm.showinfo("Login info", "Connected to the server")
            return TRUE
        return FALSE


    def send_username(self, username):
        '''
        Send entered username to the server
        @param username: user name
        '''
        msgs =  self.client.send_username(username)
        # When username was already used by someone, display error
        if msgs == 0:
            tm.showerror("Login error", "This username is taken, try another one")
            self.frames["LoginFrame"].rep = True
            self.show_frame("LoginFrame")
        else:
            self.show_frame("SessionsFrame")
            self.get_sess()

    def get_sess(self):
        '''
        Send request to the server to get current sessions list
        '''
        msgs =  self.client.get_sess()
        # If we are in sessions list.
        logging.debug('Sessions retrieved ...')
        self.frame.sessions.delete('1.0', END)
        for m in msgs:
            self.frame.sessions.insert(END, m + "\n")

    def join_sess(self, sess_id):
        '''
        Send request to the server to join a session
        @param sess_id: name of the session to join
        '''
        msgs = self.client.join_sess(msg=sess_id)
        if msgs == 0:
            tm.showerror("Login error", "Session ended choose another")
        else:
            self.initialize_game()

    def create_sess(self, num_of_players, sess_name):
        '''
        Send request to the server to create new session
        @param num_of_players: desired number of players entered
        @param sess_name: name of the session entered
        '''
        msg = num_of_players + MSG_SEP + sess_name
        msgs = self.client.create_sess(msg=msg)
        if msgs == 0:
            tm.showerror("Login error", "This session name is taken, try another one")
        else:
            self.initialize_game()

    def initialize_game(self):
            # When game hasn't started.
            self.show_frame("GameBoard")
            self.frame.clearBoard()
            self.frame.updatePlayers({})


    def send_guess(self, x, y, value):
        '''
        Send entered number to the server to check if it is right ot not
        @param x: x coordinate on the board
        @param y: y coordinate on the board
        @param value: entered number
        '''
        msg = str(x) + str(y) + str(value)
        return self.client.send_guess(msg)

    def update_game(self, message):
        # If we are in game
        # If already in gameboard. Joined before.
        # If board is returned
        if message.startswith(RSP_OK + MSG_FIELD_SEP + "[["):
            b = message[message.find(MSG_FIELD_SEP) + 1:]
            board, players = b.split(MSG_SEP)
            # got board and players. Update players list ands core board
            self.frame.clearBoard()
            self.frame.initBoard(literal_eval(board))
            self.frame.updatePlayers(literal_eval(players))


    def push_update_sess(self, message, msg=None):
        # When game session has updated from server side we do local updates as well
        # If it was correct guess then we updat board
        if message.startswith(PUSH_UPDATE_SESS + MSG_FIELD_SEP + "1"):
            # Correct guess
            board, ldb = message[3:].split(MSG_SEP)
            self.frame.updatePlayers(literal_eval(ldb))
            self.frame.initBoard(literal_eval(board))
        else:
            # Else we only update leaderboard
            ldb = literal_eval(message.split(MSG_SEP)[1])
            self.frame.updatePlayers(ldb)

    def push_end_sess(self, message, msg=None):
        # When session ends - we got a winner.
        msgs = message.split(MSG_FIELD_SEP)[1]
        if msgs == self.username:
            tm.showinfo("Info", "Congratulations you win")
        else:
            tm.showinfo("Info", "Winner is " + msgs)
        self.show_frame("SessionsFrame")
        self.get_sess()

    def exit_game(self):
        '''
        Send request to the server to leave the session
        '''
        self.client.exit_game()



class ClientCallbackGate():
    def __init__(self, push_update_sess, push_end_sess):
        self.__push_update_sess = push_update_sess
        self.__push_end_sess = push_end_sess

    @Pyro4.expose
    @Pyro4.callback
    def push_update_sess(self, msg=None):
        '''This is called by server once '''
        logging.debug('Push update sessioon')
        self.__push_update_sess(msg)

    @Pyro4.expose
    @Pyro4.callback
    def push_end_sess(self, msg=None):
        '''This is called by server once '''
        logging.debug('Push end sessioon')
        self.__push_end_sess(msg)