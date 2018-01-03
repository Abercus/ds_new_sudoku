# Setup Python logging --------------------------------------------------------
import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
LOG = logging.getLogger()

# Imports----------------------------------------------------------------------
from application.common import MC_IP, MC_PORT, WHOISHERE, MSG_SEP

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


from socket import SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SOL_IP
from socket import IPPROTO_IP, IP_MULTICAST_LOOP
from socket import inet_aton, IP_ADD_MEMBERSHIP
from threading import Thread, Lock, Condition
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err



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
        self.__callback_receiver_tread = \
            Thread(name=self.__class__.__name__ + '-CallbackReceiver', \
                   target=self.callback_receiver_loop)

        self.__notifications = []
        self.__notifications_lock = Condition()
        self.__notifications_thread =\
            Thread(name=self.__class__.__name__+'-Notifications',\
                   target=self.notification_loop)

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



    def search_for_server(self):
        mc_ip,mc_port = MC_IP, MC_PORT
        __rcv_bsize = 1024
        __s = socket(AF_INET, SOCK_DGRAM)
        __s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        __s.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
        __s.bind((mc_ip, mc_port))
        LOG.debug('Socket bound to %s:%s' % __s.getsockname())
        __s.setsockopt(SOL_IP, IP_ADD_MEMBERSHIP, \
                            inet_aton(mc_ip) + inet_aton('0.0.0.0'))
        LOG.debug('Subscribed for multi-cast group %s:%d' \
                  '' % (mc_ip, mc_port))

        try:
            while 1:
                # Receive multi-cast message
                message,addr = __s.recvfrom(__rcv_bsize)
                LOG.debug('Received Multicast From: '\
                      '%s:%s [%s]' % (addr+(message,)))

                if message.startswith(WHOISHERE):
                    _, s_addr, s_port = message.split(":")
                    p_address = (s_addr, int(s_port))
                    __s.close()
                    return p_address
        except soc_err as e:
            LOG.warn('Socket error: %s' % str(e))
        except (KeyboardInterrupt, SystemExit):
            LOG.info('Ctrl+C issued, terminating ...')
            __s.close()
            exit()
        LOG.debug('Terminating ...')




    def connect_server(self, srv_addr):
        '''
        Connect to the server
        @param srv_addr: server address
        '''

        conn = self.client.connect(srv_addr)
        if conn:
            #TODO register gate
            on_notify = lambda x: self.__notify(x)
            self.__callback_gate = ClientCallbackGate(on_notify)
            self.__callback_receiver.register(self.__callback_gate)
            LOG.debug("Made client-side object ")
            self.client.register_gate(self.__callback_gate)
            LOG.debug('Starting Notifications Handler ...')
            self.__notifications_thread.start()
            LOG.debug('Starting Callback Receiver ...')
            self.__callback_receiver_tread.start()
            tm.showinfo("Login info", "Connected to the server")
        return conn

    def __notify(self,msg):
        with self.__notifications_lock:
            was_empty = len(self.__notifications) <= 0
            self.__notifications.append(msg)
            if was_empty:
                self.__notifications_lock.notifyAll()

    def notification_loop(self):
        '''Loop: wait for notification, show new messages'''
        LOG.debug('Falling into notification loop ...')
        while 1:
            with self.__notifications_lock:
                if len(self.__notifications) <= 0:
                    self.__notifications_lock.wait()
                msg  = self.__notifications.pop(0)
                if msg == 'DIE!':
                    break
                LOG.debug('notify received ...')
                #TODO identify which funtion to call
                # self.push_start_game(msg)
                # self.push_update_sess(msg)
                # self.push_end_sess(msg)

        LOG.debug('Leaved Notifications loop')

    def callback_receiver_loop(self):
        self.__callback_receiver.requestLoop()
        LOG.debug('Leaved Callback Receiver loop')

    def send_username(self, username):
        '''
        Send entered username to the server
        @param username: user name
        '''
        msgs =  self.client.send_username(username)
        # When username was already used by someone, display error
        if not msgs:
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
        if msgs == False:
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
        self.client.send_guess(msg)

    def push_start_game(self, message):
        # If we are in game
        # If already in gameboard. Joined before.
        # If board is returned
        logging.debug('game starting... %s' % message[0])
        self.show_frame("GameBoard")
        if message is not False:
            logging.debug('game board draw')
            board, players = message[0],message[1]
            # got board and players. Update players list ands core board
            self.frame.clearBoard()
            self.frame.initBoard(literal_eval(board))
            self.frame.updatePlayers(literal_eval(players))


    def push_update_sess(self, message):
        # When game session has updated from server side we do local updates as well
        # If it was correct guess then we updat board
        logging.debug('game updating... ')
        if len(message) == 2:
            # Correct guess
            board, ldb = message[0], message[1]
            self.frame.updatePlayers(literal_eval(ldb))
            self.frame.initBoard(literal_eval(board))
        else:
            # Else we only update leaderboard
            ldb = literal_eval(message)
            self.frame.updatePlayers(ldb)

    def push_end_sess(self, message):
        # When session ends - we got a winner.
        logging.debug('game ending... ')
        if message == self.username:
            tm.showinfo("Info", "Congratulations you win")
        else:
            tm.showinfo("Info", "Winner is " + message)
        self.show_frame("SessionsFrame")
        self.get_sess()

    def exit_game(self):
        '''
        Send request to the server to leave the session
        '''
        self.client.exit_game()



class ClientCallbackGate():
    def __init__(self, notify):
        self.__notify = notify


    @Pyro4.expose
    @Pyro4.callback
    def notify(self, msg=None):
        '''This is called by server once '''
        logging.debug('Push start sessioon')
        self.__notify(msg)
