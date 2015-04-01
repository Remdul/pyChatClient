#!/usr/bin/env python3
import socket
import sys
import threading
from random import randint
import glob
import os
import hashlib

#Default Port
WOLFRAM_ALPHA   = 'U9KT42-4PX87VYXLY'
__version__     = "0.0.1.7.0"
PORT            = 1337

class Client:
    def __init__(self, connection, address):
        self.connection     = connection
        self.address        = address
        self.name           = 'Anonymous'
        self.adminStatus    = False
        self.muteStatus     = False
    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    def getAdmin(self):
        return self.adminStatus
    def setAdmin(self, adminStatus):
        self.adminStatus = adminStatus
    def getMute(self):
        return self.muteStatus
    def setMute(self, muteStatus):
        self.muteStatus = muteStatus
    def closeSocket(self):
        self.connection.close()
    def __del__(self):
        self.closeSocket()
        
    def send(self, message):
        self.connection.sendall(bytes(message, 'utf8'))
        
        
class ChatServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port     = port
        self.host     = '192.168.3.40'
        self.server   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users    = []    #Current Connections
        self.commands = self.buildCommandList()
        
        motd  = "\n+---------------------------------+\n"
        motd += "| Welcome to 4Chat.gov. All your  |\n"
        motd += "| base are belong to us. For we   |\n"
        motd += "| are legion and we are many. If  |\n"
        motd += "| you are lost, please #commands  |\n"
        motd += "|                                 |\n"
        motd += "| If you like cake, there will be |\n"
        motd += "| some provided at the end of the |\n"
        motd += "| experiment... We promise.       |\n"
        motd += "|                 - Management    |\n"
        motd += "+---------------------------------+\n"
        self.motd = motd;
        
        try:
            self.server.bind((self.host, self.port))
        except Exception as E:
            print("Failed to Bind: {}, {}".format(socket.error, E))
            sys.exit()
        self.server.listen(10)
        
    def buildCommandList(self):
        commandDict = {
                       "SHUTDOWN"   : self.shutdownServer,
                       "LOGIN"      : self.loginClient,
                       "PM"         : self.sendPrivate,
                       "WHOLIST"    : self.whoList,
                       "ME"         : self.sendEmote,
                       "ROLL"       : self.roll,
                       "MOTD"       : self.motd,
                       "LOADEMOJI"  : self.loadEmoji,
                       "ADMIN"      : self.loginAdmin,
                       "KICK"       : self.adminKick,
                       "MUTE"       : self.adminMute,
                       "COMMANDS"   : self.commandList,
                       "GETFILE"    : self.getFile,
                       }
        return commandDict

        
    def broadcast(self, message, client):
        if client.getName() == 'Anonymous':
            self.sendClient(client, "Not Logged In.\n")
            return
        if client.getMute() == True:
            self.sendClient(client, "You have been MUTED! Fail.")
            return
        
        for user in self.users:
            try:
                message += "\n"
                user.send(message)
            except Exception as E:
                print(E)
                print("Failed to Broadcast.")
                
    def sendClient(self, client, message):
        try:
            message += "\n"
            client.send(message)
        except Exception as E:
            print(E)
            print("Failed.")
            
    def evaluateData(self, data, client):
        commandEv = data.decode().strip("\n")

        if commandEv and commandEv[0] == "#":
            args = commandEv[1:].split()
            command = args[0].upper()

            try:
                print("({}){}: Called Server Command: {}".format(client.address[0],client.getName().strip(), command))
                if command in self.commands:
                    self.commands[command](client, *args)
                    return True
            except Exception as E:
                print(E)
        return False
     
     
    # SERVER COMMANDS    
    def shutdownServer(self, client, *args):
        """(A) Shuts Down the Server"""
        if client.getAdmin():
            print("Shutting Server Down")
            self.exit()
        else:
            self.sendClient(client, "You are not an Admin. Good Try.")
            
    
    def loginClient(self, client, *args):
        """Log in as <username>"""
        if not args[1].strip().isalpha():
            return
        try:
            client.setName(args[1].strip())
            self.broadcast("{} has logged in.\n".format(client.getName()), client)
        except:
            self.sendClient(client, "Invalid Login Attempt.\nTry: #login <username>")
        return True
    
    def sendPrivate(self, client, *args):
        """Send Private Message"""
        try:
            sent = False
            for user in self.users:                    
                if user.getName() == args[1].strip():
                    data = " "
                    data = data.join(args[2:])
                    data = client.getName() + " >> " + data
                    user.connection.sendall(bytes(data, 'utf8'))
                    sent = True
            if sent == False:
                self.sendClient(client, "Invalid User.\n")
        except:
            self.sendClient(client, "Invalid Message.\nTry: #pm <username> <message>")
        return True
    
    def whoList(self, client, args=[]):
        """Who is Online"""
        wholist = "Connected:\n+----------------------+----------------------+\n"
        for user in self.users:
            wholist += "| {:20} | {:20} |\n".format(user.address[0], user.getName())
        wholist += "+----------------------+----------------------+\n"
        self.sendClient(client, wholist)
        return True
    
    def sendEmote(self, client, *args):
        """Perform an action"""
        try:
            data  = " "
            data  = data.join(args[1:])
            emote = client.getName() + " " + data
            self.broadcast(emote, client)
        except:
            self.sendClient(client, "Invalid Emote.\nTry: #me <action>")
        return True
    
    def roll(self, client, args=[]):
        """Dubs get you...nevermind"""
        postNumber = randint(40000000, 50000000)
        reply = "{} has rolled: {}".format(client.getName(), postNumber) 
        self.broadcast(reply, client)
        return True
    
    def motd(self, client, args=[]):
        """The Amazing Recurring Motd"""
        self.sendClient(client, self.motd)
        return True
    
    def loadEmoji(self, client, args=[]):
        """Show all Emoji's."""
        emojis = glob.glob('emojis-png\*.png')
        for emoji in emojis:
            self.sendClient(client, emoji)

            
    def getFile(self, client, *args):
        """ Download file from Server"""
        fileToSend = open(args[1].strip(), 'rb')
        client.connection.sendall(bytes('FILE:BEGIN:'+args[1].strip()+'\n', 'utf8'))
        
        while True:
            data = fileToSend.readline()
            if data:
                client.connection.send(data)
            else:
                break
        fileToSend.close()
        client.connection.sendall(bytes('\nFILE:END', 'utf8'))
        print("File sent")
        return True
                            
    def loginAdmin(self, client, *args):
        """You elite? Prove it"""
        try:            
            hash = hashlib.sha512()
            hash.update(args[1].encode())
            hashPass = "f030156d83ee14a902d87556b6f6183d2cf2ca63fa6aecad98cf1c5e4779416ae4964db60a4fbf17f558a769ed25d45cbed77056d9f704293aaa38ccddf64836".encode()
            if hash.hexdigest().encode() == hashPass:
                client.setName("(A)" + client.getName())
                self.broadcast("All Hail the Administrator: {}".format(client.getName()), client)
                self.sendClient(client, "Welcome, Master Administrator.")
                client.setAdmin(True)
        except:
            self.sendClient(client, "Invalid Login Attempt.\nTry: #admin <password>")

            
        return True
    def adminKick(self, client, *args):
        """(A) Kick Users"""
        try:    
            if client.getAdmin() == True :
                for user in self.users:
                    if user.getName().strip() == args[1].strip():
                        self.sendClient(user, "Administrator has booted your butt. Have a nice day! :)")
                        self.sendClient(client, "Kicked User.")
                        user.closeSocket()
            else:
                self.sendClient(client, "You are not an Admin. Good Try.")
        except:
            self.sendClient(client, "Invalid Command.\nTry: #kick <username>")
        return True
    
    def adminMute(self, client, *args):
        """(A) Mute Annoying Users"""
        try:
            if client.getAdmin() == True:
                for user in self.users:
                    if user.getName().strip() == args[1].strip():
                        self.sendClient(user, "Your tongue has been forcibly ripped out. What did you do!?")
                        self.sendClient(client, "Muted User.")
                        user.setMute(True)
            else:
                self.sendClient(client, "You are not an Admin. Good Try.")
        except:
            self.sendClient(client, "Invalid Kick.\nTry: #kick <username>")
        return True
    
    def commandList(self, client, args=[]):
        """See #COMMANDS"""
        wholist  = "\n\n+--------------+\n"
        for command in sorted(self.commands):
            docString = self.commands[command].__doc__
            wholist  += "| {:12} | {}\n".format(command, docString)
        wholist += "+--------------+\n"
        self.sendClient(client, wholist)
        return True
         
    def addClient(self, connection, address):
        print("Client connected with: {}:{}".format(address[0], str(address[1])))
        newClient = Client(connection, address)
        self.users.append(newClient)
        self.sendClient(newClient, self.motd)
        
        try:
            while True:
                data = newClient.connection.recv(1024)                    
                if self.evaluateData(data, newClient) == False:
                    reply = "<{:>10}> : {}".format(newClient.getName(), data.decode())
                    print("{}".format(reply))
                    self.broadcast(reply, newClient)
        
        except ConnectionResetError as E:
            print("Client Disconnected")
    
        finally:
            self.users.remove(newClient)
            self.broadcast("{} has disconnected.\n".format(newClient.getName()), newClient)
            del newClient
            break
            
    def run(self):
        print("Waiting for connections on port: {}".format(self.port))
        while True:
            connection, address = self.server.accept()
            threading.Thread(target=self.addClient, args=(connection, address)).start()
    
    def exit(self):
        self.server.close()

def main():
    server = ChatServer(PORT)
    server.run()
        
        
if __name__ == '__main__':
    main()
            