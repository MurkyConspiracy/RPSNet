import socket
import sys
import json
import random
from os import path
from functools import partial

try:
    import tkinter
    from tkinter import *
    from tkinter import messagebox
except ImportError:
    print("Please install Tkinter to run this APP!!")
    sys.exit(0)

class game():

    '''__init__

    This function creates a game client object which handles all game data, as well as handles all outgoing and incoming connection
    game client objects need to call startGui() method to start the game

    game objects include:
    gameWinds || A list of windows used to control the offline game GUI
    onlineWinds || A list of windows used to control the login screen GUI
    version || Version identifier
    LFLAG || Login flag is set to true when player logs in
    WFLAG || Wafer flag is set to true if game data is loaded from Game.Dat, or an account is finished creation
    REQdata || A dictionary filled with *ALL* player requests, incoming/outgoing
    players || A list of every registered player
    InSel || The incoming request selection variable for the Online Gui
    OutSel || The outgoing request selection variable for the Online Gui
    OMove || Outgoing move selected
    name || Client name
    wins || Client wins
    losses || Client losses
    gameStates || All possible offline game states
    RPSStates || All possible offline game moves
    lossWords || Snarky phrases when the bot wins
    winWords || Snarky phrases when the player wins
    SN || Secret Number
    REQID || Request ID for sending server requests



    REQUEST ID STRUCTURE
    1 -- Login attempt
    2 -- Get server requests that pertain to player
    3 -- Get a list of all registered players
    4 -- Send match to server to be stored
    5 -- Sends match response to server
    6 -- Gets updated score from natches
    
    '''

    def __init__(self):
        #Welcome User
        print("Welcome to RPSNet, a P2P rock paper scissors.")
        #Check if Game.Dat is already created, if so load it, if not create.
        self.gameWinds = ["", "", ""]
        self.onlineWinds = ["", "", "", "", "", "", "", ""]
        self.version = 'R1.4'
        self.LFLAG = 0
        self.WFLAG = 0
        self.REQdata = {}
        self.players = []
        self.InSel = ""
        self.OutSel = ""
        self.OMove = ""
        if not path.exists("Game.Dat"):
            self.getName()
        else:
            GameDat = open("Game.Dat", "r")
            print("Game data loaded!")
            GameDat.seek(0)
            Dat = GameDat.read().splitlines()
            GameDat.close()
            self.name = Dat[0]
            self.wins = Dat[1]
            self.losses = Dat[2]
            self.gameStates = {'WIN' : 1, 'LOSS' : 2, 'TIE' : 3}
            self.RPSStates = ["Rock", "Paper", "Scissors"]
            self.lossWords = ["Major L", "Ooff", "You goofed", "So close", "Better luck next time", "Try harder", "Get good", "R.I.P."]
            self.winWords = ["Congrats...?", "I mean it was a bot.", "Are you proud of that win?", "Is this a major accomplishment for you?", "Try Hard", "Hacker"]
            self.SN = -1
            self.REQID = -1
            self.WFLAG = 1


    '''getName

    This function draws an input form for the user to select a name
    This function calls accountCreate() and sends it the players chosen name

    '''
        
    def getName(self):
        nameIn = tkinter.Tk()

        nameIn.title("RPSNet")
        nameIn.geometry("250x100")
        nameIn.pack_propagate(0)
        nameIn.resizable(0, 0)

        cLabel = Label(nameIn, text="Create account name:")
        cLabel.pack()
        cLabel.place(height = 30, width = 120, x = 5, y = 5)

        cEntry = Entry(nameIn)
        cEntry.pack()
        cEntry.place(height = 30, width = 200, x = 5, y = 30)
        
        cButton = Button(nameIn, text="Submit", command=lambda: self.accountCreate(nameIn, cEntry, cEntry.get()))
        cButton.pack()
        cButton.place(height = 30, width = 60, x = 5, y = 65)
        nameIn.mainloop()

    '''accountCreate

    checks if the players name is valid, and if so passes the data to the Game object and creates Game.Dat
    This function is the end of the account creation proccess

    '''

    def accountCreate(self, wind, entry, name):
        if name == None or name == "" or name.isdecimal() or "|" in name or "-" in name or "RPSNet" in name:
            entry.delete(0, END)
            entry.insert("end", "INVALID!")
            return

        wind.destroy()
        GameDat = open("Game.Dat", "w+")
        print("Game data created!")
        GameDat.write(name + "\n")
        GameDat.write("0\n0")
        GameDat.seek(0)
        Dat = GameDat.read().splitlines()
        GameDat.close()
        self.name = Dat[0]
        self.wins = Dat[1]
        self.losses = Dat[2]
        self.gameStates = {'WIN' : 1, 'LOSS' : 2, 'TIE' : 3}
        self.RPSStates = ["Rock", "Paper", "Scissors"]
        self.lossWords = ["Major L", "Ooff", "You goofed", "So close", "Better luck next time", "Try harder", "Get good", "R.I.P."]
        self.winWords = ["Congrats...?", "I mean it was a bot.", "Are you proud of that win?", "Is this a major accomplishment for you?", "Try Hard", "Hacker"]
        self.SN = -1
        self.REQID = -1
        self.WFLAG = 1

    '''saveDat

    This openes the Game.Dat and writes any changes to score into it
    
    '''

    def saveDat(self):
        GameDat = open("Game.Dat", "w+")
        GameDat.seek(0)
        GameDat.truncate()
        GameDat.write(self.name + "\n")
        GameDat.write(str(self.wins) + "\n" + str(self.losses))
        GameDat.close()



    '''startGui

    This starts the basic main menu for RPSNet and handles buttons to launch offline games or the online client
    This function calls doOfflineGame
    This function calls onlineGui
    
    '''


    def startGui(self):
        if self.WFLAG == 0:
            raise Exception("No account created!","Enter an account name!")
        top = tkinter.Tk()

        top.title("RPSNet   " + self.version)
        top.geometry("400x274")
        top.pack_propagate(0)
        top.resizable(0, 0)
        
        Header = Label(top, text="Welcome to: RPSNet\nA client-server based Rock Paper Scissors Games!")
        Header.pack( side = TOP)

        Welcome = Label(top, text="\n\nWelcome:  " + self.name)
        Wins = Label(top, text="Wins: " + self.wins)
        Losses = Label(top, text="Losses: " + self.losses)
        Welcome.pack( anchor = W)
        Wins.pack( anchor = W)
        Losses.pack( anchor = W)
        
        OfflineGame = Button(top, text="Play Offline", width = 20, command=self.doOfflineGame)
        OnlineGame = Button(top, text="Online Opponent", width = 20, command=self.onlineGui)
        OnlineGame.pack()
        OnlineGame.place(height = 30, width = 120, x = 67, y = 220)
        OfflineGame.pack()
        OfflineGame.place(height = 30, width = 120, x = 207, y = 220)

        self.onlineWinds[6] = Wins
        self.onlineWinds[7] = Losses

        
        top.mainloop()

    '''onlineGui

    This method creates a more complex Tkinter Gui that houses a few listboxes, a login text field and a login button
    This is where players can send and receives requests to other players
    This function calls doClinetLogin
    this function calls doIncome
    this function calls doOnlineGame
    this function calls doOutgo
    this function calls sendRequest

    '''

    def onlineGui(self):
        OnlineWind = tkinter.Tk()
        OnlineWind.title("RPSNet Online!")
        OnlineWind.geometry("300x400")
        OnlineWind.pack_propagate(0)
        OnlineWind.resizable(0, 0)


        SecretLabel = Label(OnlineWind, text="Secret Number:")
        SecretLabel.pack()
        SecretLabel.place(height = 30, width = 105, x = 0, y = 315)

        Secret = Entry(OnlineWind)
        Secret.pack()
        Secret.place(height = 30, width = 90, x = 3, y = 365)
        self.onlineWinds[5] = Secret
        
        LoginButtn = Button(OnlineWind, text="Login", command=self.doClientLogin)
        LoginButtn.pack()
        LoginButtn.place(width = 90, height = 30, x = 3, y = 335)        
        self.onlineWinds[4] = LoginButtn

        Incoming = Listbox(OnlineWind)
        Incoming.place(width = 120, height = 200, x = 15, y = 65)
        Incoming.bind('<<ListboxSelect>>', self.doIncome)
        self.onlineWinds[0] = Incoming

        IncomingLabel = Label(OnlineWind, text="Incoming Requests")
        IncomingLabel.pack()
        IncomingLabel.place(height = 30, width = 125, x = 12, y = 35)

        PlayMatch = Button(OnlineWind, text="Accept Match", state="disabled", command=lambda: self.doOnlineGame(1))
        PlayMatch.pack()
        PlayMatch.place(width = 120, height = 30, x = 15, y = 266)
        self.onlineWinds[1] = PlayMatch

        
        Sending = Listbox(OnlineWind)
        Sending.place(width = 120, height = 200, x = 155, y = 65)
        Sending.bind("<<ListboxSelect>>", self.doOutgo)
        self.onlineWinds[2] = Sending

        SendingLabel = Label(OnlineWind, text="Send Requests")
        SendingLabel.pack()
        SendingLabel.place(height = 30, width = 120, x = 155, y = 35)

        SendMatch = Button(OnlineWind, text="Send Match", state="disabled", command=lambda: self.sendRequest())
        SendMatch.pack()
        SendMatch.place(width = 120, height = 30, x = 155, y = 266)
        self.onlineWinds[3] = SendMatch


    '''doIncome

    This method checks if player is logged in, and then sets the object variable InSel to the current listbox selection
    This method sets InSel
    This method also handles the state of buttons

    '''

    def doIncome(self, evt):
        if self.LFLAG == 1:
            if not self.onlineWinds[0].curselection() == ():
                self.InSel = self.onlineWinds[0].get(self.onlineWinds[0].curselection())
                self.onlineWinds[1].config(state="normal")
            else:
                self.InSel = ""
                self.onlineWinds[1].config(state="disabled")
        else:
            return

    '''doOutgo

    This method checks if player is logged in, and then sets the object variable OutSel to the current listbox selection
    This method sets OutSel
    This method also handles the state of buttons

    '''
    
    def doOutgo(self, evt):
        if self.LFLAG == 1:
            if not self.onlineWinds[2].curselection() == ():
                self.OutSel = self.onlineWinds[2].get(self.onlineWinds[2].curselection())
                self.onlineWinds[3].config(state="normal")
            else:
                self.OutSel = ""
                self.onlineWinds[3].config(state="disabled")
                
        else:
            return

    '''sendRequest

    This method handles duplicate request sending, and blocks attempts to send a second request, if there is no other requests, you can send a new one
    This function calls doOnlineGame

    '''
        

    def sendRequest(self):
        sName = '-' + self.OutSel
        if sName in self.REQdata:
            messagebox.showerror("Oh NO!", self.OutSel + " already has a request from you!")
        else:
            self.doOnlineGame(0)

    '''setMove

    This method sends a message to the server, telling it to store the request for the other player
    this function calls getRequests
    
    '''


    def setMove(self, move, wind):
        self.OMove = move
        wind.destroy()
        self.REQID = 4
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.OutSel) + "\n" + str(self.OMove) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(4096)
            sock.close()
            decodedData = data.decode("UTF-8")

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return

        self.getRequests()


    '''sendMove

    This method sends a message to the server, telling it to complete the request for the other player
    This function calls getRequests
    this function calls doMatchComplete
    
    '''

    def sendMove(self, move, wind):
        self.OMove = move
        wind.destroy()
        self.REQID = 5
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.InSel) + "\n" + str(self.OMove) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(4096)
            sock.close()
            decodedData = data.decode("UTF-8")
            self.doMatchComplete(int(decodedData))

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return

        
        self.getRequests()


    '''doOnlineGame

    This method creates a simple Gui to pick Rock/Paper/Scissors for incoming and outgoing requests
    This function calls sendMove
    This function calls setMove
    
    '''

    def doOnlineGame(self, sendAcc):
        gameWindow = tkinter.Tk()

        gameWindow.title("RPSNet")
        gameWindow.geometry("525x95")
        gameWindow.pack_propagate(0)
        gameWindow.resizable(0, 0)

        if sendAcc == 1:
            Rock = Button(gameWindow, text="Rock", command=lambda: self.sendMove(1, gameWindow))
            Paper = Button(gameWindow, text="Paper", command=lambda:self.sendMove(2, gameWindow) )
            Scissors = Button(gameWindow, text="Scissors", command=lambda: self.sendMove(3, gameWindow))
        elif sendAcc == 0:
            Rock = Button(gameWindow, text="Rock", command=lambda: self.setMove(1, gameWindow))
            Paper = Button(gameWindow, text="Paper", command=lambda:self.setMove(2, gameWindow) )
            Scissors = Button(gameWindow, text="Scissors", command=lambda: self.setMove(3, gameWindow))

        Rock.pack()
        Rock.place(height = 30, width = 96, x = 75, y = 45)
        Paper.pack()
        Paper.place(height = 30, width = 96, x = 225, y = 45)
        Scissors.pack()
        Scissors.place(height = 30, width = 96, x = 375, y = 45)
        
        gameWindow.mainloop()
        gameWindow = None

    '''doMatchComplete

    This method creates the Gui to alert the player of the game completion status
    
    '''

    def doMatchComplete(self, winWs):
        wi = tkinter.Tk()

        wi.title("RPSNet")
        wi.geometry("200x35")
        wi.pack_propagate(0)
        wi.resizable(0, 0)

        if winWs == 1:
            wil = Label(wi, text="You Won!")
            wil.pack(fill=X)
        elif winWs == 0:
            wil = Label(wi, text="It's a tie!")
            wil.pack(fill=X)
        elif winWs == -1:
            wil = Label(wi, text="You Lost!")
            wil.pack(fill=X)

        wl = Label(wi, text="Score will update on next login!")
        wl.pack(fill=X)

    '''doClientLogin

    This method sends a message to the server, telling it to attempt a login with your secret number
    This function checks Secret Number
    This function configures all login buttons/boxes/labels
    This function calls getRequests
    This function calls settleScore
    This function calls getPlayers
    
    '''

    def doClientLogin(self):
        self.REQID = 1
        SN = self.onlineWinds[5].get()
        if not SN == None:
            if not SN.isnumeric():
                self.onlineWinds[5].delete(0, END)
                self.onlineWinds[5].insert(0, "INVALID")
                return
            else:
                self.SN = SN
        else:
            self.onlineWinds[5].delete(0, END)
            self.onlineWinds[5].insert(0, "INVALID")
            return
            
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.SN) + "\n" + str(self.version) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(1024)
            sock.close()
            decodedData = data.decode("UTF-8")

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return
        

        if decodedData == "":
            return
        if decodedData == "2":
            self.onlineWinds[5].delete(0, END)
            self.onlineWinds[5].insert("end", "FAILED")
        elif decodedData == "0":
            self.onlineWinds[5].delete(0, END)
            self.onlineWinds[5].insert("end", "CREATED")
            self.onlineWinds[5].config(state="disabled")
            self.LFLAG = 1
            self.onlineWinds[4].config(state="disabled")
            self.onlineWinds[5].delete(0, END)
            self.onlineWinds[5].insert("end", "Logged in!")
            self.onlineWinds[5].config(state="disabled")
            self.settleScore()
            self.getRequests()
            self.getPlayers()
        elif decodedData == "1":
            self.LFLAG = 1
            self.onlineWinds[4].config(state="disabled")
            self.onlineWinds[5].delete(0, END)
            self.onlineWinds[5].insert("end", "Logged in!")
            self.onlineWinds[5].config(state="disabled")
            self.settleScore()
            self.getRequests()
            self.getPlayers()

        
        return


    '''getRequests

    This method sends a message to the server, telling it to send back all requests pertaining to the player
    This function sets REQdata
    This function updates the requests listbox
        
    '''

    def getRequests(self):
        self.onlineWinds[0].delete(0, 'end')
        self.REQID = 2
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.SN) + "\n" + str(self.version) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(4096)
            sock.close()
            decodedData = data.decode("UTF-8")

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return

        playerDict = json.loads(decodedData)
        self.REQdata.clear()
        self.REQdata.update(playerDict)
        for key in self.REQdata.keys():
            if not key.startswith("-"):
                self.onlineWinds[0].insert("end", key)


        return

    '''getPlayers

    This method sends a message to the server, telling it to send back all players
    This function sets players
    This function updates the player listbox
        
    '''

    def getPlayers(self):
        self.REQID = 3
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.SN) + "\n" + str(self.version) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(4096)
            sock.close()
            decodedData = data.decode("UTF-8")

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return

        playersList = json.loads(decodedData)
        self.players = playersList
        for player in playersList:
            self.onlineWinds[2].insert("end", player)
        
        return

    '''settleScore

    This method sends a message to the server, telling it to send back all player scorings
    This function updates wins
    This function updates losses
        
    '''

    def settleScore(self):
        self.onlineWinds[0].delete(0, 'end')
        self.REQID = 6
        ADDRESS = ('3.15.166.171', 6666)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataStream = str(self.name) + "\n" + str(self.SN) + "\n" + str(self.version) + "\n" + str(self.REQID)

        decodedData = ""
        try:
            sock.connect(ADDRESS)
            sock.send(dataStream.encode('UTF-8'))
            data = sock.recv(4096)
            sock.close()
            decodedData = data.decode("UTF-8")

        except ConnectionRefusedError:
            messagebox.showinfo("Oh NO!", "Server may be down?\nPlease check your connection!")
            return

        if decodedData == "NA":
            return 
        else:
            self.wins = int(self.wins) + int(decodedData[:decodedData.index("||")])
            self.losses = int(self.losses) + int(decodedData[decodedData.index("||")+2:])
            self.saveDat()
            self.onlineWinds[6].config(text="Wins: " + str(self.wins))
            self.onlineWinds[7].config(text="Losses: " + str(self.losses))

        return
    

    '''doOfflineGame

    This method creates an offline game window to play unscored RPS
    This function handles funny comments and playing against an offline bot
    This function calls checkOfflineRole
    
    '''

    def doOfflineGame(self):
        gameWindow = tkinter.Tk()

        gameWindow.title("RPSNet")
        gameWindow.geometry("525x200")
        gameWindow.pack_propagate(0)
        gameWindow.resizable(0, 0)

        Rock = Button(gameWindow, text="Rock", command=lambda: self.checkOfflineRole(1))
        Paper = Button(gameWindow, text="Paper", command=lambda: self.checkOfflineRole(2))
        Scissors = Button(gameWindow, text="Scissors", command=lambda: self.checkOfflineRole(3))
        MyRoll = Label(gameWindow, text="My Roll: ")
        BotRoll = Label(gameWindow, text="Bot's Roll: ")
        StateText = Label(gameWindow, text="    ")


        MyRoll.pack(side=LEFT)
        MyRoll.place(height = 30, width = 145, x = 60, y = 35)
        BotRoll.pack(side=LEFT)
        BotRoll.place(height = 30, width = 145, x = 67, y = 75)
        StateText.pack(anchor = S)
        Rock.pack()
        Rock.place(height = 30, width = 96, x = 75, y = 125)
        Paper.pack()
        Paper.place(height = 30, width = 96, x = 225, y = 125)
        Scissors.pack()
        Scissors.place(height = 30, width = 96, x = 375, y = 125)

        self.gameWinds[0] = MyRoll
        self.gameWinds[1] = BotRoll
        self.gameWinds[2] = StateText
        
        gameWindow.mainloop()
        gameWindow = None
        self.gameWinds = None

        

    '''checkOfflineRole

    This method handles all the offline game logic, and sends it back to the offlineGame form
    This function handles all textboxes and labels for the offline game
    
    
    '''
    def checkOfflineRole(self, roll):
        botroll = random.randint(1,3)
        outcome = []
        if roll == 1 and botroll == 1:
            self.gameWinds[0].config(text="My Roll: Rock")
            self.gameWinds[1].config(text="Bot's Roll: Rock")
            self.gameWinds[2].config(text="It's a tie!")
            outcome.append(self.gameStates.get('TIE'))
            return outcome
        elif roll == 2 and botroll == 2:
            self.gameWinds[0].config(text="My Roll: Paper")
            self.gameWinds[1].config(text="Bot's Roll: Paper")
            self.gameWinds[2].config(text="It's a tie!")
            outcome.append(self.gameStates.get('TIE'))
            return outcome
        elif roll == 3 and botroll == 3:
            self.gameWinds[0].config(text="My Roll: Scissors")
            self.gameWinds[1].config(text="Bot's Roll: Scissors")
            self.gameWinds[2].config(text="It's a tie!")
            outcome.append(self.gameStates.get('TIE'))
            return outcome
        elif roll == 1 and botroll == 2:
            self.gameWinds[0].config(text="My Roll: Rock")
            self.gameWinds[1].config(text="Bot's Roll: Paper")
            self.gameWinds[2].config(text=self.lossWords[random.randint(0, len(self.lossWords) - 1)])
            outcome.append(self.gameStates.get('LOSS'))
            return outcome
        elif roll == 2 and botroll == 3:
            self.gameWinds[0].config(text="My Roll: Paper")
            self.gameWinds[1].config(text="Bot's Roll: Scissors")
            self.gameWinds[2].config(text=self.lossWords[random.randint(0, len(self.lossWords) - 1)])
            outcome.append(self.gameStates.get('LOSS'))
            return outcome
        elif roll == 3 and botroll == 1:
            self.gameWinds[0].config(text="My Roll: Scissors")
            self.gameWinds[1].config(text="Bot's Roll: Rock")
            self.gameWinds[2].config(text=self.lossWords[random.randint(0, len(self.lossWords) - 1)])
            outcome.append(self.gameStates.get('LOSS'))
            return outcome
        elif roll == 1 and botroll == 3:
            self.gameWinds[0].config(text="My Roll: Rock")
            self.gameWinds[1].config(text="Bot's Roll: Scissors")
            self.gameWinds[2].config(text=self.winWords[random.randint(0, len(self.winWords) - 1)])
            outcome.append(self.gameStates.get('WIN'))
            return outcome
        elif roll == 2 and botroll == 1:
            self.gameWinds[0].config(text="My Roll: Paper")
            self.gameWinds[1].config(text="Bot's Roll: Rock")
            self.gameWinds[2].config(text=self.winWords[random.randint(0, len(self.winWords) - 1)])
            outcome.append(self.gameStates.get('WIN'))
            return outcome
        elif roll == 3 and botroll == 2:
            self.gameWinds[0].config(text="My Roll: Scissors")
            self.gameWinds[1].config(text="Bot's Roll: Paper")
            self.gameWinds[2].config(text=self.winWords[random.randint(0, len(self.winWords) - 1)])
            outcome.append(self.gameStates.get('WIN'))
            return outcome

        print("Your roll: " + str(roll))
        print("Computers roll: " + str(botroll))
        raise(BrokenPipeError("A major error has occured, \nPlease report this bug!!!"))

    
        
#Run Code
Client = game()
Client.startGui()
