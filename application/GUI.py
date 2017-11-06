from Tkinter import *

class Fn:
    def __init__(self, root, r, c, Points):

        def putValue(self, v, Points):
            if v!=0:
                self.sv.set(v)
                if Done[9*(r-1)+c]==v:
                    Points+=1
                    self.ent.config({"background": "Yellow"})
                else:
                    Points-=1
                    self.ent.config({"background": "Red"})

        def getValue(self):
            if self.ent.get() == '' or int(self.ent.get()) < 1 or int(self.ent.get()) > 9:
                return 0

            return int(self.ent.get())

        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode, sv=self.sv: putValue(self, getValue(self),Points))
        self.ent = Entry(root, textvariable=self.sv, width=3)
        self.ent.grid(row=r, column=c)


    def putValues(self, v):
        self.sv.set(v)
        if v!="":
            self.ent.config({"background": "Yellow"})
        else:
            self.ent.config({"background": "White"})



class Application(Tk):
    def __init__(self):
        self.root = Tk()
        self.root.title("Sudoku")

        self.game = Button(self.root, text="New game", command=self.game)
        self.exit = Button(self.root, text="Exit", command=self.Exit)

        self.points = Text(self.root, height=1.8, width=20)
        self.points.pack()
        self.points.insert(END, "User points: " + str(Points))
        self.points.grid(row=2, column=10, rowspan=3)

        self.game.grid(row=10, column=0, columnspan=6)
        self.exit.grid(row=10, column=3, columnspan=6)

        self.case = []
        for i in range(9):
            for j in range(9):
                self.case += [Fn(self.root, i + 1, j,Points)]


    def Exit(self):
        del (self.case)
        self.root.destroy()
        self.root.quit()


    def game(self):
        for i in range(len(self.case)):
            if (Undone[i]!=0):
                self.case[i].putValues(Undone[i])
            else:
                self.case[i].putValues('')



Undone = [
        0, 0, 0, 2, 6, 0, 7, 0, 1,
        6, 8, 0, 0, 7, 0, 0, 9, 0,
        1, 9, 0, 0, 0, 4, 5, 0, 0,
        8, 2, 0, 1, 0, 0, 0, 4, 0,
        0, 0, 4, 6, 0, 2, 9, 0, 0,
        0, 5, 0, 0, 0, 3, 0, 2, 8,
        0, 0, 9, 3, 0, 0, 0, 7, 4,
        0, 4, 0, 0, 5, 0, 0, 3, 6,
        7, 0, 3, 0, 1, 8, 0, 0, 0
    ]

Done = [
        4, 3, 5, 2, 6, 9, 7, 8, 1,
        6, 8, 2, 5, 7, 1, 4, 9, 3,
        1, 9, 7, 8, 3, 4, 5, 6, 2,
        8, 2, 6, 1, 9, 5, 3, 4, 7,
        3, 7, 4, 6, 8, 2, 9, 1, 5,
        9, 5, 1, 7, 4, 3, 6, 2, 8,
        5, 1, 9, 3, 2, 6, 8, 7, 4,
        2, 4, 8, 9, 5, 7, 1, 3, 6,
        7, 6, 3, 4, 1, 8, 2, 5, 9
    ]

Points = 0

app = Application()
app.root.mainloop()