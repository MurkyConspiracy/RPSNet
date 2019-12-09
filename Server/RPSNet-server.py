import socket
import json
from _thread import *
import threading
import os

version ='R1.4'
print_lock = threading.Lock()

class ServerData():

    '''__init__

    This method creates a server object that handles all file data and request storage

    path || Player storage file name
    pathREQ || Request data file name
    pathScore || Scoring data file name
    header || Player file header text
    headerREQ || Request file header text
    headerScore || Score file header text
    playerData || List of all players
    REQdata || List of all requests
    ScoreData || List of all scoring packets

    playerData <== path
    playerREQ <== pathREQ
    ScoreData || <== ScoreData
    
    '''
    
    def __init__(self, path):
        print("Server initializing:")
        self.path = path
        self.pathREQ = self.path + "REQ"
        self.pathScore = self.path + "SCORE"
        self.header = "RPSNet Player file struct"
        self.headerREQ = "RPSNet Send/Request file struct"
        self.headerScore = "RPSNet Score settling file"
        
        print("Checking for: " + str(self.path))
        if not os.path.exists(self.path):
            try:
                print("Trying to create new " + self.path)
                dataFile = open(self.path, "w+")
                dataFile.write(self.header)
                dataFile.seek(0)
                self.playerData = dataFile.read().splitlines()
                dataFile.close()
                print("Trying to create new " + self.pathREQ)
                dataFile = open(self.pathREQ, "w+")
                dataFile.write(self.headerREQ)
                dataFile.seek(0)
                self.REQdata = dataFile.read().splitlines()
                dataFile.close()
                print("Trying to create new " + self.pathScore)
                dataFile = open(self.pathScore, "w+")
                dataFile.write(self.headerScore)
                dataFile.seek(0)
                self.ScoreData = dataFile.read().splitlines()
                dataFile.close()
                
            except PermissionError:
                print("Required permissons not met!")
                raise PermissionError("Try running python with SU permissions")
        else:
            try:
                print("Trying to read from file " + self.path)
                dataFile = open(self.path, "r+")
                dataFile.seek(0)
                self.playerData = str(dataFile.read()).splitlines()
                dataFile.close()
                print("Trying to read from file " + self.pathREQ)
                dataFile = open(self.pathREQ, "r+")
                dataFile.seek(0)
                self.REQdata = str(dataFile.read()).splitlines()
                dataFile.close()
                print("Trying to read from file " + self.pathScore)
                dataFile = open(self.pathScore, "r+")
                dataFile.seek(0)
                self.ScoreData = str(dataFile.read()).splitlines()
                dataFile.close()
            except PermissionError:
                print("Required permissons not met!")
                raise PermissionError("Try running python with SU permissions")


 
    '''saveDat

    This method loads all current list data into the files and saves them

    '''
    def saveDat(self):
        try:
            print("Appending to: " + self.path)
            dataFile = open(self.path, "a+")
            dataFile.seek(0)
            dataFile.truncate()
            dataFile.write("\n".join(self.playerData))
            dataFile.close()
            print("Appending to: " + self.pathREQ)
            dataFile = open(self.pathREQ, "a+")
            dataFile.seek(0)
            dataFile.truncate()
            dataFile.write("\n".join(self.REQdata))
            dataFile.close()
            print("Appending to: " + self.pathScore)
            dataFile = open(self.pathScore, "a+")
            dataFile.seek(0)
            dataFile.truncate()
            dataFile.write("\n".join(self.ScoreData))
            dataFile.close()
        except PermissionError:
            print("Required permissons not met!")
            raise PermissionError("Try running python with SU permissions")
 
'''_Login

This method tries to log the player in with their secrent number
If it fails, the request is denied
If no player with that name exists it creates is with the secret number
**This function populates playerData
This function calls saveDat

'''

def _Login(playerName, secretNumber, ServerObj):
    Flag = 0
    for entry in range(len(ServerObj.playerData)):
        if playerName in ServerObj.playerData[entry]:
            if ServerObj.playerData[entry] == (playerName + "||" + secretNumber):
                Flag = 1
            else:
                Flag = 2

    if Flag == 0:
        ServerObj.playerData.append((playerName + "||" + secretNumber))
        ServerObj.saveDat()
        return str(Flag)
    elif Flag == 2:
        return str(Flag)
    elif Flag == 1:
        return str(Flag)
               
'''getRequests

This method gets any requests that the player may need, and sends them back in dictionary form
This function uses a json parses to send the data in a more effecient way

'''

def getRequests(playerName, ServerObj):
    playerReqDict = {}
    for entry in ServerObj.REQdata:
        if entry[:len(entry)-3].endswith(playerName):
            sName = entry[:entry.index("||")]
            move = entry[len(entry)-1:]
            playerReqDict.update({sName : move})
        elif entry.startswith(playerName):
            sName = "-" + entry[2+entry.index("||"):len(entry)-3]
            move = str(entry[len(entry)-1:])
            playerReqDict.update({sName : move})

    return json.dumps(playerReqDict)

'''getAllPlayers

This method returns a list of all players that have registered on the server
This function uses a json parses to send the data in a more effecient way

'''

def getAllPlayers(playerName, ServerObj):
    players = []
    for player in ServerObj.playerData:
        if not "RPSNet" in player and not playerName in player:
            players.append(player[:player.index("||")])

    return json.dumps(players)

'''parseRequests

This method saves incoming requests to the file system for later use
This function calls saveDat

'''

def parseRequests(Sender, Receiver, Move, ServerObj):
    store = str(Sender) + "||" + str(Receiver) + "||" + str(Move)
    ServerObj.REQdata.append(store)
    ServerObj.saveDat()
    return store

'''parseMatch

This method returns handles accepted matches and game logic, it also handles scoring logic
This function calls saveDat

'''

def parseMatch(Sender, Receiver, ReceivedMove, ServerObj):

    PMatch = ""
    for Match in ServerObj.REQdata:
        if Match.startswith(Sender) and Receiver in Match:
            PMatch = Match


    SentMove = int(PMatch[len(PMatch)-1:])
    ReceivedMove = int(ReceivedMove)
    Outcome = 0
    if SentMove == ReceivedMove:
        Outcome = 0
    elif SentMove == 1 and ReceivedMove == 2:
        Outcome = 1
        ServerObj.ScoreData.append(Receiver + "||" + str(Outcome))
        ServerObj.ScoreData.append(Sender + "||" + "-")
    elif SentMove == 1 and ReceivedMove == 3:
        Outcome = -1
        ServerObj.ScoreData.append(Receiver + "||" + "-")
        ServerObj.ScoreData.append(Sender + "||" + "1")
    elif SentMove == 2 and ReceivedMove == 1:
        Outcome = -1
        ServerObj.ScoreData.append(Receiver + "||" + "-")
        ServerObj.ScoreData.append(Sender + "||" + "1")
    elif SentMove == 2 and ReceivedMove == 3:
        Outcome = 1
        ServerObj.ScoreData.append(Receiver + "||" + str(Outcome))
        ServerObj.ScoreData.append(Sender + "||" + "-")
    elif SentMove == 3 and ReceivedMove == 1:
        Outcome = 1
        ServerObj.ScoreData.append(Receiver + "||" + str(Outcome))
        ServerObj.ScoreData.append(Sender + "||" + "-")
    elif SentMove == 3 and ReceivedMove == 2:
        Outcome = -1
        ServerObj.ScoreData.append(Receiver + "||" + "-")
        ServerObj.ScoreData.append(Sender + "||" + "1")


    print(ServerObj.ScoreData)
    print(PMatch)

    ServerObj.REQdata.remove(PMatch)
    
    ServerObj.saveDat()

        
    return str(Outcome)

'''getScore

This method returns a list of all scoring packets for the client to handles, it also removes them from the server
This function calls saveDat

'''

def getScore(playerName, ServerObj):
    Wins = 0
    Losses = 0
    for line in ServerObj.ScoreData:
        if not "RPSNet" in line:
            if line[:line.index("||")] == playerName:
                if line[line.index("||")+2:] == "1":
                    Wins = Wins + 1
                if line[line.index("||")+2:] == "-":
                    Losses = Losses + 1
                ServerObj.ScoreData.remove(line)
    ServerObj.saveDat()
    if Wins > 0 or Losses > 0:
        return str(Wins) + "||" + str(Losses)
    else:
        return "NA"
    
'''waitForConnection

This method handles all client server interactions, sending and receiving the data from its socket
This method calls _Login
This method calls getRequests
This method calls getAllPlayers
This method calls parseRequests
This method calls parseMatch
This method calls getScore

'''

def waitForConnection(c, ServerObj):
    while True:
        data = c.recv(1024)
        if not data:
            print_lock.release()
            break

        clientData = data.decode("UTF-8").splitlines()
        print(clientData)
        requestType = clientData[3]
        if int(requestType) == 1:
            c.send(_Login(clientData[0], clientData[1], ServerObj).encode("UTF-8"))
        elif int(requestType) == 2:
            c.send(getRequests(clientData[0], ServerObj).encode("UTF-8"))
        elif int(requestType) == 3:
            c.send(getAllPlayers(clientData[0], ServerObj).encode("UTF-8"))
        elif int(requestType) == 4:
            c.send(parseRequests(clientData[0], clientData[1], clientData[2], ServerObj).encode("UTF-8"))
        elif int(requestType) == 5:
            c.send(parseMatch(clientData[1], clientData[0], clientData[2], ServerObj).encode("UTF-8"))
        elif int(requestType) == 6:
            c.send(getScore(clientData[0], ServerObj).encode("UTF-8"))
            
        #c.send(b'Connection Accepted!')
    c.close()

'''Main

This method is the main connection loop that checks for incoming requests, and sends the data off our handler
This function calls waitForConnection

'''

def Main(ServerObj):
    TCP_IP = '0.0.0.0'
    TCP_PORT = 6666
    BUFFER_SIZE = 1024
    ADDRESS = (TCP_IP, TCP_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(ADDRESS)
    print('socket binded to port', TCP_PORT)

    sock.listen(5)
    print("socket is listening")

    while True:
        c, addr = sock.accept()
        print_lock.acquire()
        print("Conected to :", addr[0], ":", addr[1])
        try:
            start_new_thread(waitForConnection, (c,ServerObj,))
        except:
            sock.close()
            print("Socket saved, closed!")
    sock.close()


Server = ServerData("Predicate")
print(Server.playerData)
print(Server.REQdata)
print(Server.ScoreData)

Main(Server)

