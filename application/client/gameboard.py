# Imports----------------------------------------------------------------------
from Tkinter import *
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

class Fn:
    '''
    Class of the cell of the game board
    '''
    def __init__(self, root, r, c):

        def putValue(v, active):
            '''
            This function is called when number is changed. Will make a request to server asking
            if the value is correct.
            @param v: value
            @param active: true if cell is active
            '''

            try:
                value = int(v)
                if active and value != 0:
                    #it has to be -1
                    root.controller.send_guess(r-1, c, value)
            except ValueError:
                pass


        def getValue(self):
            '''
            Get the value of the cell
            @return: value of the cell, if cell is on the game board and is not empty
            '''
            if self.ent.get() == '' or int(self.ent.get()) < 1 or int(self.ent.get()) > 9:
                return 0

            return int(self.ent.get())

        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode, sv=self.sv: putValue(getValue(self), root.active))
        large_font = ('Verdana', 15)
        self.ent = Entry(root, textvariable=self.sv, width=2,font=large_font,justify='center')

        # Define place of the cell on the grid
        if (r+2)%3==0:
            self.ent.grid(row=r, column=c, pady=(5, 0))
        if (c)%3==0:
            self.ent.grid(row=r, column=c, padx=(5, 0))
        else:
            self.ent.grid(row=r, column=c)


    def putValues(self, v, disabled=False):
        '''
        Write value in the cell
        @param v: value
        @param disabled: true if cell is disabled, default: false
        '''
        self.sv.set(v)
        if disabled:
            self.ent.config(state="disabled")
        else:
            self.ent.config(state="normal")
            self.ent.config({"background": "White"})



class GameBoard(Frame):
    '''
    Main class for the game session
    '''
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.configure(background='SkyBlue2')

        # Define the controller class
        self.controller = controller

        self.active = False
        self.Points = []
        self.Clients = []

        # Button to exit from the session
        self.exit = Button(self, text="Exit", command=self.Exit)

        # Leader Board: shows the players and their scores
        self.points = Text(self, height=6, width=20, font=('Verdana', 10))
        self.points.pack()
        self.points.grid(row=2, column=10, rowspan=4, padx=10)
        self.points.config(state='disabled')

        self.exit.grid(row=10, column=3, columnspan=6, pady=10)

        # Array to store the cells in
        self.case = []
        for i in range(9):
            for j in range(9):
                self.case += [Fn(self, i + 1, j)]

        # Initialize empty board
        self.empty_board()


    def updatePlayers(self, players):
        '''
        Update Leader Board with players and their scores
        @param players: list of the players and scores
        '''
        self.points.config(state='normal')
        self.points.delete('1.0', END)
        self.Clients = list(players)
        LOG.debug('game players... %s' % players)
        self.Points = players.values()
        res = ""
        for k,v in players.items():
            res += str(k) + " " + str(v) + "\n"
        print res
        self.points.insert(END, res)
        self.points.config(state='disabled')


    def clearBoard(self):
        '''
        Clear the game board
        '''
        self.active = False
        self.Points = []
        self.Clients = []
        self.points.delete('1.0',END)
        self.empty_board()


    def initBoard(self, board):
        '''
        Initialize the game board
        @param board: game board
        '''
        self.active = False
        for i in range(len(self.case)):
            x = i / 9
            y = i % 9
            if board[x][y] == "-":
                self.case[i].putValues('', disabled=False)
            else:
                self.case[i].putValues(int(board[x][y]), disabled=True)

        self.active = True


    def Exit(self):
        '''
        Exit from the session
        '''
        self.controller.exit_game()
        self.controller.show_frame("SessionsFrame")
        self.controller.get_sess()


    def empty_board(self):
        '''
        Initialize an empty game board.
        Real game board set when game begins (sent from server and parsed).
        '''
        for i in range(len(self.case)):
            self.case[i].putValues('', disabled=True)

