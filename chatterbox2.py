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

    def __del__(self):
        self.closeSocket()

    def closeSocket(self):
        self.connection.close()

    def send(self, message):
        self.connection.sendall(bytes(message, 'utf8'))

x = {}

def chatcommand(usage):
    
    def wrap(f):
        x[usage] = f
        return f

    return wrap
    
class ChatServer(threading.Thread):
    
    @chatcommand('login <name>')
    def loginClient(self, client, cmd, name):
        """Log in as <username>"""
        if not name.strip().isalpha():
            return
        try:
            client.name = name.strip()
            self.broadcast("{} has logged in.\n".format(client.name), client)
        except:
            self.sendClient(client, "Invalid Login Attempt.\nTry: #login <username>")

    
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port     = port
        self.host     = '192.168.1.4'
        self.server   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users    = []    #Current Connections
     
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

    @property
    def commands(self):
        commandDict = {
                       "SHUTDOWN"   : self.shutdownServer,
                       "LOADEMOJI"  : self.loadEmoji,
                       "KICK"       : self.adminKick,
                       "MUTE"       : self.adminMute,
                       "GETFILE"    : self.getFile,
                       }
        for usage in x:
            commandDict[usage.split()[0]] = x[usage]
        return commandDict

        
    def broadcast(self, message, client):
        if client.name == 'Anonymous':
            self.sendClient(client, "Not Logged In.\n")
            return
        if client.muteStatus == True:
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
        value = False
        
        commandEv = data.decode().strip("\n")
        if not (commandEv and commandEv[0] == "#"):
           return False

        args = commandEv[1:].split()
        command = args[0].upper()

        
        print("({}){}: Called Server Command: {}".format(client.address[0],client.name.strip(), command))
        if command in self.commands:
            try:
                self.commands[command](client, *args)
            except TypeError as E:
                client.send("Usage: #{}\n".format(self.commands[command].__doc__.split("\n")[0]))
            value = True

        return value
     
     
    # SERVER COMMANDS
    #@('shutdown')
    def shutdownServer(self, client, *_):
        """(A) Shuts Down the Server"""
        if client.adminStatus:
            print("Shutting Server Down")
            self.exit()
        else:
            self.sendClient(client, "You are not an Admin. Good Try.")
            

    @chatcommand('pm <username> <message>')
    def sendPrivate(self, client, *args):
        """Send Private Message"""
        try:
            sent = False
            for user in self.users:                    
                if user.name == args[1].strip():
                    data = " "
                    data = data.join(args[2:])
                    data = client.name + " >> " + data
                    user.send(data)
                    sent = True
            if sent == False:
                self.sendClient(client, "Invalid User.\n")
        except:
            self.sendClient(client, "Invalid Message.\nTry: #pm <username> <message>")
  
    @chatcommand('wholist')
    def whoList(self, client, args=[]):
        """Who is Online"""
        wholist = "Connected:\n+----------------------+----------------------+\n"
        for user in self.users:
            wholist += "| {:20} | {:20} |\n".format(user.address[0], user.name)
        wholist += "+----------------------+----------------------+\n"
        self.sendClient(client, wholist)
 
    @chatcommand('me <action>')
    def sendEmote(self, client, *args):
        """Perform an action"""
        try:
            data  = " "
            data  = data.join(args[1:])
            emote = client.name + " " + data
            self.broadcast(emote, client)
        except:
            self.sendClient(client, "Invalid Emote.\nTry: #me <action>")

    @chatcommand('roll')
    def roll(self, client, args=[]):
        """Dubs get you...nevermind"""
        postNumber = randint(40000000, 50000000)
        reply = "{} has rolled: {}".format(client.name, postNumber) 
        self.broadcast(reply, client)

    @chatcommand('motd')
    def motd(self, client, args=[]):
        """The Amazing Recurring Motd"""
        self.sendClient(client, str(x))
        self.sendClient(client, self.motd)

    
    def loadEmoji(self, client, args=[]):
        """Show all Emoji's."""
        emojis = glob.glob('emojis-png\*.png')
        for emoji in emojis:
            self.sendClient(client, emoji)

            
    def getFile(self, client, *args):
        """ Download file from Server"""
        fileToSend = open(args[1].strip(), 'rb')
        client.send('FILE:BEGIN:'+args[1].strip()+'\n')
        
        while True:
            data = fileToSend.readline()
            if data:
                client.send(data)
            else:
                break
        fileToSend.close()
        client.send('\nFILE:END')
        print("File sent")

    @chatcommand('admin <password>')             
    def loginAdmin(self, client, passwd, *_):
        """You elite? Prove it"""
        if not passwd:
            print("No passwd")
            client.send("Usage: #admin <password>")
            return
      
        hash = hashlib.sha512()
        hash.update(passwd.encode())
        hashPass = "f030156d83ee14a902d87556b6f6183d2cf2ca63fa6aecad98cf1c5e4779416ae4964db60a4fbf17f558a769ed25d45cbed77056d9f704293aaa38ccddf64836".encode()
        if hash.hexdigest().encode() == hashPass:
            client.setName("(A)" + client.name)
            self.broadcast("All Hail the Administrator: {}".format(client.name), client)
            self.sendClient(client, "Welcome, Master Administrator.")
            client.setAdmin(True)


            
        return True
    def adminKick(self, client, *args):
        """(A) Kick Users"""
        try:    
            if client.adminStatus == True:
                for user in self.users:
                    if user.name.strip() == args[1].strip():
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
            if client.adminStatus == True:
                for user in self.users:
                    if user.name.strip() == args[1].strip():
                        self.sendClient(user, "Your tongue has been forcibly ripped out. What did you do!?")
                        self.sendClient(client, "Muted User.")
                        user.setMute(True)
            else:
                self.sendClient(client, "You are not an Admin. Good Try.")
        except:
            self.sendClient(client, "Invalid Kick.\nTry: #kick <username>")
        return True

    @chatcommand('commands')
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
                    reply = "<{:>10}> : {}".format(newClient.name, data.decode())
                    print("{}".format(reply))
                    self.broadcast(reply, newClient)
        except ConnectionResetError as E:
            print("{} has disconnected".format(newClient.name))
        finally:
            self.users.remove(newClient)
            self.broadcast("{} has disconnected".format(newClient.name), newClient)
            del newClient


  

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


def chatcommand(context, func, desc):
    context.chatcommand.append(func)
    

        
if __name__ == '__main__':
    main()
            
