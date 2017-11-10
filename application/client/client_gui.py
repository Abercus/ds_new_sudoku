import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
LOG = logging.getLogger()

from application.common import TCP_RECEIVE_BUFFER_SIZE, \
    RSP_OK, RSP_UNKNCONTROL, \
    REQ_UNAME, REQ_GET_SESS, REQ_JOIN_SESS, REQ_NEW_SESS, \
    MSG_FIELD_SEP, MSG_SEP, RSP_UNAME_TAKEN

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
        self.geometry('450x320')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.client = client
        self.queue = Queue()
        self.threads = []

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, ConnectFrame, SessionsFrame, GameBoard):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        self.frame = self.frames[page_name]
        self.frame.tkraise()

    def connect_server(self, srv_addr):
        # 127.0.0.1:7777
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
        self.client.exit()


    def update_gui(self, q):
        message = q.get()
        #TODO: here goes protocol to update gui as needed

        logging.debug('Received [%d bytes] in total' % len(message))
        if len(message) < 2:
            logging.debug('Not enough data received from %s ' % message)
            return
        logging.debug('Response control code (%s)' % message[0])
        if message.startswith(RSP_OK + MSG_FIELD_SEP):
            logging.debug('Messages retrieved ...')
            msgs = message[2:].split(MSG_FIELD_SEP)
            msgs = map(self.client.deserialize,msgs)
            for m in msgs:
                self.client.__on_recv(m)
            return msgs
       # elif message.startswith(RSP_OK_GET_SESS + MSG_FIELD_SEP):
          #  self.frame.sessions.insert(END, message)
        elif message.startswith(RSP_UNAME_TAKEN + MSG_FIELD_SEP):
            tm.showerror("Error", RSP_UNAME_TAKEN)
        else:
            logging.debug('Unknown control message received: %s ' % message)
            return RSP_UNKNCONTROL

