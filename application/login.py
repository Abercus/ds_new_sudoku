from Tkinter import *
import tkMessageBox as tm


class LoginFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.label_1 = Label(self, text="Username")
        self.entry_1 = Entry(self)

        self.label_1.grid(row=0, sticky=E)
        self.entry_1.grid(row=0, column=1)


        self.logbtn = Button(self, text="Login", command = self._login_btn_clickked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clickked(self):

        username = self.entry_1.get()

        if username == "john" :
            tm.showinfo("Login info", "Welcome John")
        else:
            tm.showerror("Login error", "Incorrect username")


root = Tk()
lf = LoginFrame(root)
root.mainloop()