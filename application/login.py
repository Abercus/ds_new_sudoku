from Tkinter import *
import tkMessageBox as tm
import tkFont as tkfont

class LoginApplication(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Authentication Box')
        self.geometry('300x150')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, ConnectFrame):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


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
            tm.showinfo("Login info", "Welcome " + username)
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

        if address == "":
            tm.showerror("Login error", "Can't connect")
        else:
            tm.showinfo("Login info", "Connected to " + address)


