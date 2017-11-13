import tkMessageBox as tm
from Tkinter import *


class LoginFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')
        self.controller = controller
        self.label_1 = Label(self, text="Enter Nickname: ")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))
        self.rep=False	#changed to True if UNAME_TAKEN

        self.logbtn = Button(self, text="Login", command = lambda: self._login_btn_clickked(self.rep))
        self.logbtn.grid(columnspan=2, pady=(10, 10))

    def _login_btn_clickked(self, rep=False):

        username = self.entry_1.get()
        if username == "":
            tm.showerror("Login error", "Empty username is no allowed")
        elif len(username)>8:
            tm.showerror("Login error", "Length of username must be less than 8 characters")
        elif (' ' in username) == True:
            tm.showerror("Login error", "Space in username is not allowed")
        elif rep:
            self.controller.username = username
            self.controller.send_username(self.controller.username)
        else:
          #  tm.showinfo("Login info", "Welcome " + username)
            self.controller.show_frame("ConnectFrame")
            self.controller.username = username


class ConnectFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')
        self.controller = controller
        self.label_1 = Label(self, text="Enter Sudoku server address: ")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))

        self.logbtn = Button(self, text="Connect", command = self._connect_btn_clickked)
        self.logbtn.grid(columnspan=2, pady=(10, 10))

    def _connect_btn_clickked(self):

        address = self.entry_1.get()

        if self.controller.connect_server(address):
            self.controller.send_username(self.controller.username)
            #self.controller.get_sess()
           # self.controller.show_frame("SessionsFrame")
            #tm.showinfo("Login info", "Connected to " + address)
        else:
            tm.showerror("Login error", "Can't connect")


class SessionsFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')
        self.controller = controller

        self.sessions = Text(self, height=6, width=20, font=('Verdana', 10))
        self.sessions.grid(row = 0,column = 1, columnspan=3, pady=(10, 10))
        #self.sessions.insert(END, sessions)

        self.create_sess_btn = Button(self, text="Create Session", command = self._new_btn_clickked)
        self.create_sess_btn.grid(row = 1,column = 1, columnspan=3, pady=(10, 10))

        self.join_sess_btn = Button(self, text="Join Session", command=self._join_btn_clickked)
        self.join_sess_btn.grid(row = 2,column = 1, columnspan=3, pady=(10, 10))

    def _new_btn_clickked(self):

        while TRUE:
            self.popup("Enter number of the players")
            try:
                self.controller.num_payers = int(self.input.value)
                if int(self.input.value) < 2:
                    tm.showerror("Error", "At least 2 players must be in the game")
                else:
                    break
            except ValueError:
                tm.showerror("Error", "Number must be integer")

        while TRUE:
            self.popup("Enter name of the session")
            if self.input.value.strip() == "":
                tm.showerror("Error", "Name must not be empty")
                continue
            self.controller.sess_name = self.input.value
            break

        self.controller.create_sess(self.controller.sess_name, str(self.controller.num_payers))
        tm.showinfo("Login info", "you chose " +  self.input.value)


    def _join_btn_clickked(self):
        self.popup("Enter id of the session to join")
        self.controller.sess_name = self.input.value
        self.controller.join_sess(self.controller.sess_name)
        #self.controller.show_frame("GameBoard")
        tm.showinfo("Login info", "you chose  " +  self.input.value)

    def popup(self, text):
        self.input = popupWindow(self.master, text)
        self.create_sess_btn["state"] = "disabled"
        self.join_sess_btn["state"] = "disabled"
        self.master.wait_window(self.input.top)
        self.create_sess_btn["state"] = "normal"
        self.join_sess_btn["state"] = "normal"


class popupWindow(object):
    def __init__(self, master, text):
        top = self.top = Toplevel(master)
        self.l = Label(top, text=text)
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value = self.e.get()
        self.top.destroy()

class popupWin(object):
    def __init__(self, master, text):
        top = self.top = Toplevel(master)
        self.l = Label(top, text=text)
        self.l.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value = self.e.get()
        self.top.destroy()
