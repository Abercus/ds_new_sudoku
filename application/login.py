from Tkinter import *
import tkMessageBox as tm
import tkFont as tkfont
from threading import Thread, Lock

class Application(Tk):

    def __init__(self, client, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Authentication Box')
        self.geometry('350x300')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.client = client

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, ConnectFrame, SessionsFrame):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def connect_server(self, srv_addr):
        # 127.0.0.1:7777
        a, b = srv_addr.split(':')
        if self.client.connect((a,int(b))):

            #TODO: server side
            # t = Thread(name='ServerProcessor', \
            #            target=self.client.loop, args=())
            # t.start()
            # t.join()

            tm.showinfo("Login info", "Connected to the server")
            return TRUE
        else: return TRUE

    def get_sess(self):
        #return self.client.get_sess()
        return ['session 1', 'session 2', 'session 3']

    def join_sess(self, sess_id):
        tm.showinfo("Login info", "Join")
       # self.client.join_sess(msg=sess_id)

    def create_sess(self, sess_name):
        tm.showinfo("Login info", "Create")
       # self.client.join_sess(msg=sess_name)



class LoginFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.label_1 = Label(self, text="Username: ")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))

        self.logbtn = Button(self, text="Login", command = self._login_btn_clickked)
        self.logbtn.grid(columnspan=2, pady=(10, 10))

    def _login_btn_clickked(self):

        username = self.entry_1.get()

        if username == "":
            tm.showerror("Login error", "Empty username is no allowed")
        elif len(username)>8:
            tm.showerror("Login error", "Length of username must be less than 8 characters")
        elif (' ' in username) == True:
            tm.showerror("Login error", "Space in username is not allowed")
        else:
          #  tm.showinfo("Login info", "Welcome " + username)
            self.controller.show_frame("ConnectFrame")


class ConnectFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.label_1 = Label(self, text="Server address: ")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))

        self.logbtn = Button(self, text="Connect", command = self._connect_btn_clickked)
        self.logbtn.grid(columnspan=2, pady=(10, 10))

    def _connect_btn_clickked(self):

        address = self.entry_1.get()

        if self.controller.connect_server(address):
            self.controller.show_frame("SessionsFrame")
            tm.showinfo("Login info", "Connected to " + address)
        else:
            tm.showerror("Login error", "Can't connect")


class SessionsFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        sessions = self.controller.get_sess()

        self.sessions = Text(self, height=6, width=20, font=('Verdana', 10))
        self.sessions.grid(row = 0,column = 1, columnspan=3, pady=(10, 10))
        self.sessions.insert(END, sessions)

        self.create_sess_btn = Button(self, text="Create Session", command = self._new_btn_clickked)
        self.create_sess_btn.grid(row = 1,column = 1, columnspan=3, pady=(10, 10))

        self.join_sess_btn = Button(self, text="Join Session", command=self._join_btn_clickked)
        self.join_sess_btn.grid(row = 2,column = 1, columnspan=3, pady=(10, 10))

    def _new_btn_clickked(self):
        toplevel = Toplevel()
        popup = Label(toplevel, text="enter name of session you want to create: ", width = 40, height = 10)
        popup.grid(row=0, column=1,columnspan=3, pady=(10, 10))
        session_name_ent = Entry(self)
        session_name_ent.grid(row=2, column=1, columnspan=3, pady=(10, 10))
        okbtn = Button(self, text="OK", command = self.controller.create_sess)
        okbtn.grid(row=3, column=1,columnspan=2, pady=(10, 10))

    def _join_btn_clickked(self):
        toplevel = Toplevel()
        popup = Label(toplevel, text="enter id of session you want to join: ", width = 100, height = 0)
        popup.pack()
        self.session_id_ent = Entry(self)
        self.session_id_ent.pack()
        okbtn = Button(self, text="OK", command = self.controller.join_sess)
        okbtn.pack()
