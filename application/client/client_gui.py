import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
LOG = logging.getLogger()

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

from application.client.gameboard import GameBoard
from gui_parts import LoginFrame, ConnectFrame, SessionsFrame


class Application(Tk):

    def __init__(self, client, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Authentication Box')
        self.geometry('490x350')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.client = client
        self.queue = Queue()
        self.threads = []

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        fnames = (LoginFrame, ConnectFrame, SessionsFrame, GameBoard)
        for F in fnames:
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        self.frame = self.frames[page_name]
        self.fname = page_name
        self.frame.tkraise()

    def connect_server(self, srv_addr = ''):
        if srv_addr == '':
            srv_addr = '127.0.0.1'+':'+'7777'

        a, b = srv_addr.split(':')
        if self.client.connect((a,int(b))):
            #TODO: server side
            gui = Thread(name='GuiProcessor', \
                         target=self.update_gui, args=(self.queue,))
            self.threads.append(gui)

            ser = Thread(name='ServerProcessor', \
                       target=self.client.loop, args=(self.queue,))
            self.threads.append(ser)

            for t in self.threads:
                t.start()

            tm.showinfo("Login info", "Connected to the server")
            return TRUE
        return FALSE


    def send_username(self, username):
        return self.client.send_username(username)

    def get_sess(self):
        return self.client.get_sess()
        #return ['session 1', 'session 2', 'session 3']

    def join_sess(self, sess_id):
        #tm.showinfo("Login info", "Join")
        self.client.join_sess(msg=sess_id)

    def create_sess(self, num_of_players):
        #tm.showinfo("Login info", "Create")
        self.client.create_sess(msg=num_of_players)

    def check_number(self, number):
        self.client.check_number()

    def exit_game(self):
        self.client.exit_game()


    def update_gui(self, q):
        logging.info('GuiProcessor started ....' )
        message = q.get()
        #TODO: here goes protocol to update gui as needed

        logging.info('Received [%d bytes] in total' % len(message))
        if len(message) < 2:
            logging.debug('Not enough data received from %s ' % message)
            return
        logging.debug('Response control code (%s)' % message[0])
        if message.startswith(RSP_OK + MSG_FIELD_SEP):
            for i in len(self.fnames):
                if self.fnames[i] == self.fname:
                     self.controller.show_frame(self.fnames[i+1])

        elif message.startswith(RSP_UNAME_TAKEN + MSG_FIELD_SEP):
            tm.showerror("Login error", "This username is taken, try another one")


        elif message.startswith(RSP_OK_GET_SESS + MSG_FIELD_SEP):
            logging.debug('Sessions retrieved ...')
            msgs = message[2:].split(MSG_FIELD_SEP)
            msgs = map(self.client.deserialize, msgs)
            for m in msgs:
                self.client.__on_recv(m)
            self.frame.sessions.insert(END, msgs)

        elif message.startswith(RSP_SESSION_ENDED + MSG_FIELD_SEP):
            tm.showerror("Login error", "Session ended choose another")

        elif message.startswith(RSP_SESSION_TAKEN + MSG_FIELD_SEP):
            tm.showerror("Login error", "This session name is taken, try another one")

        elif message.startswith(PUSH_UPDATE_SESS + MSG_FIELD_SEP):
            msgs = message[2:].split(MSG_FIELD_SEP)
            msgs = map(self.client.deserialize, msgs)
            #TODO: update game

        elif message.startswith(PUSH_END_SESSION + MSG_FIELD_SEP):
            msgs = message[2:].split(MSG_FIELD_SEP)
            msgs = map(self.client.deserialize, msgs)
            if msgs == self.username:
                tm.showinfo("Info", "Congratulations you won")
            else: tm.showinfo("Info", "Winer is " + msgs)

        else:
            logging.debug('Unknown control message received: %s ' % message)
            return RSP_UNKNCONTROL

