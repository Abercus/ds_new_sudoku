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
                         target=self.updateGUI, args=(self.queue,))
            self.threads.append(gui)

            ser = Thread(name='ServerProcessor', \
                       target=self.client.loop, args=(self.queue,))
            self.threads.append(ser)

            for t in self.threads:
                t.start()

            tm.showinfo("Login info", "Connected to the server")
            return TRUE
        return FALSE


    def updateGUI(self, q):
        m = q.get()
        self.frame.sessions.insert(END, m)
        #TODO: here goes protocol to update gui as needed

    def send_username(self, username):
        return self.client.send_username(username)

    def get_sess(self):
        return self.client.get_sess()
        #return ['session 1', 'session 2', 'session 3']

    def join_sess(self, sess_id):
        tm.showinfo("Login info", "Join")
       # self.client.join_sess(msg=sess_id)

    def create_sess(self, sess_name):
        tm.showinfo("Login info", "Create")
       # self.client.join_sess(msg=sess_name)


