# Imports----------------------------------------------------------------------
import tkMessageBox as tm
from Tkinter import *


class LoginFrame(Frame):
    '''
    Launch the login part of the GUI
    '''
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')

        # Define the controller class
        self.controller = controller

        self.label_1 = Label(self, text="Enter Nickname: ")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))
        self.rep=False	#changed to True if UNAME_TAKEN

        self.logbtn = Button(self, text="Login", command = lambda: self._login_btn_clickked(self.rep))
        self.logbtn.grid(columnspan=2, pady=(10, 10))

    def _login_btn_clickked(self, rep=False):
        '''
        Check the username and send it ot the server
        @param rep:
        '''
        username = self.entry_1.get()
        if username == "":
            tm.showerror("Login error", "Empty username is no allowed")
        elif len(username) > 8:
            tm.showerror("Login error", "Length of username must be less than 8 characters")
        elif ' ' in username:
            tm.showerror("Login error", "Space in username is not allowed")
        elif not username.isalnum():
            tm.showerror("Login error", "Must consist of alphanumeric characters")
        elif rep:
            self.controller.username = username
            self.controller.send_username(self.controller.username)
        else:
            self.controller.show_frame("ConnectFrame")
            self.controller.username = username


class ConnectFrame(Frame):
    '''
    Launch the server address part of the GUI
     '''
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')

        # Define the controller class
        self.controller = controller

        self.label_1 = Label(self, text="Press button to search and connect to server...")
        self.label_1.grid(row=0, sticky=E , pady=(40, 10))


        self.logbtn = Button(self, text="Search for server", command = self._connect_btn_clickked)
        self.logbtn.grid(columnspan=2, pady=(10, 10))


    def _connect_btn_clickked(self):
        '''
        Connect to the server
        '''

        address = self.controller.search_for_server()
        if self.controller.connect_server(address):
            self.controller.send_username(self.controller.username)

        else:
            tm.showerror("Login error", "Can't connect")


class SessionsFrame(Frame):
    '''
    Launch the session part of the GUI
    '''
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')

        # Define the controller class
        self.controller = controller

        self.sessions = Text(self, height=6, width=20, font=('Verdana', 10))
        self.sessions.grid(row = 0,column = 1, columnspan=3, pady=(10, 10))

        self.create_sess_btn = Button(self, text="Create Session", command = self._new_btn_clickked)
        self.create_sess_btn.grid(row = 1,column = 1, columnspan=3, pady=(10, 10))

        self.join_sess_btn = Button(self, text="Join Session", command=self._join_btn_clickked)
        self.join_sess_btn.grid(row = 2,column = 1, columnspan=3, pady=(10, 10))

        self.refresh_sess_btn = Button(self, text="Refresh Session", command=self._refresh_btn_clickked)
        self.refresh_sess_btn.grid(row = 3,column = 1, columnspan=3, pady=(10, 10))


    def _new_btn_clickked(self):
        '''
        Create new session
        '''
        self.controller.num_payers = None
        self.controller.sess_name = None
        while TRUE:
            # Choose number of desired players
            self.popup("Enter number of the players")
            try:
                if not self.input.value:
                    return

                self.controller.num_payers = int(self.input.value)

                if int(self.input.value) < 2:
                    tm.showerror("Error", "At least 2 players must be in the game")
                else:
                    break
            except ValueError:
                tm.showerror("Error", "Number must be integer")

        while TRUE:
            # Choose name of the session
            self.popup("Enter name of the session")
            if not self.input.value:
                return
            if self.input.value.strip() == "":
                tm.showerror("Error", "Name must not be empty")
                continue
            self.controller.sess_name = self.input.value
            break

        if self.controller.sess_name and self.controller.num_payers:
            self.controller.create_sess(self.controller.sess_name, str(self.controller.num_payers))


    def _join_btn_clickked(self):
        '''
        Join to existing session
        '''
        self.popup("Enter name of the session to join")
        self.controller.sess_name = self.input.value
        # Send request to the server to join the session
        if self.controller.sess_name:
            self.controller.join_sess(self.controller.sess_name)


    def _refresh_btn_clickked(self):
        self.controller.get_sess()

    def popup(self, text):
        '''
        Show the popup window and disables buttons
        @param text: text for the popup window
        '''
        self.input = popupWindow(self.master, text)
        self.create_sess_btn["state"] = "disabled"
        self.join_sess_btn["state"] = "disabled"
        self.master.wait_window(self.input.top)
        self.create_sess_btn["state"] = "normal"
        self.join_sess_btn["state"] = "normal"


class popupWindow(object):
    '''
    Popup window of the GUI
    '''
    def __init__(self, master, text):
        '''
        Create popup window
        @param master: parent class
        @param text: text to write on the window
        '''
        self.value = None

        top = self.top = Toplevel(master)
        self.l = Label(top, text=text)
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        '''
        Destory popup window after pressing ok button
        '''
        self.value = self.e.get()
        self.top.destroy()
