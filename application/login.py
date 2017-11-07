from Tkinter import *
import tkMessageBox as tm


class LoginFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.label_1 = Label(self, text="Username: ")
        self.entry_1 = Entry(self)


        self.label_1.grid(row=0, sticky=E , pady=(40, 10))
        self.entry_1.grid(row=0, column=1, pady=(40, 10))


        self.logbtn = Button(self, text="Login", command = self._login_btn_clickked)
        self.logbtn.grid(columnspan=2, pady=(10, 10))

        self.pack()

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


root = Tk()
root.title('Authentication Box')
root.geometry('300x150')

lf = LoginFrame(root)
root.mainloop()