#!/usr/bin/env python3
from tkinter import *
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText
import datetime, socket, threading, random

class ChatClient():
    '''
        A chat client built using socket and tkinter for the GUI
    '''
    def __init__(self):
        self.username = ''
        self.server = ''
        self.port = ''

        # Tkinter init
        self.root = Tk()
        self.root.title("Simple Chat Client")
        self.root.geometry("550x340")
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Top Menu bar
        self.menubar.add_cascade(label="Connect", command=self.ConnectWin)
        self.menubar.add_cascade(label="Exit", command=self.Quit)
        
        # Chat room name
        self.room_name = StringVar()
        Label(self.root, textvariable=self.room_name, bg='#2C2C34', fg='#A8A8A3').pack()
        
        # Chatbox
        self.buttonFrame = Frame(self.root)
        self.chatBox = ScrolledText(self.buttonFrame, height=18, width=50)
       
        self.chatBox.pack(side=LEFT)
        self.userBox = Listbox(self.buttonFrame, height=18, width=20)
        self.userBox.pack(side=RIGHT)
        self.buttonFrame.pack(fill = BOTH)
        
        # Chat text entry
        self.entryFrame = Frame(self.root)
        self.chatText = Entry(self.entryFrame, width=70)
        self.chatText.pack(fill = BOTH, side=LEFT)
        
        self.send_button = Button(self.entryFrame, text="Send", command=lambda: self.Send(self.chatText.get()), width=20, state=DISABLED)
        self.send_button.pack(side=RIGHT)
        self.entryFrame.pack(fill = BOTH)
        
        self.Stylize()
        
        #self.root.overrideredirect(True) #!!! Work on functionality using this
        self.root.mainloop()
    
    def Stylize(self):
        '''
        Handles the stylization settings of the entire GUI
        '''
        # Colours
        self.user_colours = {}
        self.colour_list = ['FF0000', '33CC33', '0099FF', 'FFCC00', 'FF6600', 'FFFFFF', 'CC3399', '9933FF']

        self.default_text = '#A8A8A3'
        self.theme_bg = '#2C2C34'
        self.entry_bg = '#111110'
        self.entry_text = '#A8A8A3'
        self.send_bg = '#3366FF'
        self.send_text = '#FFFFFF'

        # Frames
        self.root.configure(background = self.theme_bg)
        self.entryFrame.configure(background = self.theme_bg)
        self.buttonFrame.configure(background = self.theme_bg)

        self.chatBox.configure(background = self.theme_bg, foreground = self.default_text)
        self.userBox.configure(background = self.theme_bg, foreground = self.default_text)
        self.chatText.configure(background = self.entry_bg, foreground = self.entry_text)
        
        # Buttons
        self.send_button.configure(background = self.send_bg, foreground = self.send_text)
                
        # Tags
        self.chatBox.tag_add('user', '0.5', '1.0')
        self.chatBox.tag_configure('user', font='helvetica 10 bold', foreground="#A8A8A3")
        self.chatBox.tag_add('server', '0.0', '1.0')
        self.chatBox.tag_configure('server', foreground="#3366FF")
        for colour in self.colour_list: 
            self.chatBox.tag_add(colour,'1.0','end')
            self.chatBox.tag_configure(colour, foreground='#{}'.format(colour))
        

    
    def ConnectWin(self):
        # Base window creation
        self.connectWin = Toplevel(self.root)
        self.connectWin.geometry("240x100")
        self.connectWin.title("Connect to...")
        self.connectWin.protocol('WM_DELETE_WINDOW', self.connectWin.destroy)
        
        # Master Frame
        self.masterFrame = Frame(self.connectWin)
        
        # Label Frame
        self.labelFrame = Frame(self.masterFrame)
        Label(self.labelFrame, text="User Name: ", bg='#2C2C34', fg='#A8A8A3').pack()
        Label(self.labelFrame, text="Server IP: ", bg='#2C2C34', fg='#A8A8A3').pack()
        Label(self.labelFrame, text="Server Port: ", bg='#2C2C34', fg='#A8A8A3').pack()
        self.labelFrame.pack(side=LEFT)
        
        # Entry Frame
        self.entryFrame = Frame(self.masterFrame)
        uname_input = Entry(self.entryFrame, width=15)
        uname_input.pack()
        server_ip = Entry(self.entryFrame, width=15)
        server_ip.pack()
        server_port = Entry(self.entryFrame, width=15)
        server_port.pack()
        self.entryFrame.pack(side=RIGHT)
        self.masterFrame.pack()
        
        # Bottom Frame
        self.botFrame = Frame(self.connectWin)
        self.connect_button = Button(self.botFrame, text="Connect", command=lambda: self.Connect(uname_input.get(), server_ip.get(), server_port.get()))
        self.connect_button.pack()
        self.botFrame.pack(side=BOTTOM)
        
        # Stylization
        self.connectWin.configure(background = self.theme_bg)
        self.masterFrame.configure(background = self.theme_bg)
        self.labelFrame.configure(background = self.theme_bg)
        
        uname_input.configure(background = self.entry_bg, foreground = self.entry_text)
        server_ip.configure(background = self.entry_bg, foreground = self.entry_text)
        server_port.configure(background = self.entry_bg, foreground = self.entry_text)
        
        self.connect_button.configure(background = self.send_bg, foreground = self.send_text)
        #self.connectWin.overrideredirect(True)
        
        
    def Connect(self, username, server, port):
        # Close the Connect window.
        self.connectWin.destroy()

        self.username = username
        self.server = server
        self.port = port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(200)
        
        try :
            # Start a new thread for the connection
            self.StartThread()
            # Set the chatroom name based on the host IP; eventually get a hostname from the server (!!!)
            self.room_name.set("{}'s room".format(self.server))
            self.send_button.config(state=NORMAL)
            
        except socket.error as socketerror: 
            print("Error: {}".format(socketerror))    
        except :
            print('Unable to connect')
            #sys.exit()
            
    def Display(self, text, name):       
        self.GetColour(name)

        if name == 'SERVER':
            self.chatBox.insert('end','[{:%H:%M}] {}: \n'.format(datetime.datetime.now().time(), name),('user'))
            self.chatBox.insert('end', '{}\n'.format(text), 'server')
        else:
            self.chatBox.insert('end','[{:%H:%M}] {}: '.format(datetime.datetime.now().time(), name), (self.user_colours[name]))
            self.chatBox.insert('end', '{}\n'.format(text), '')
        # Scroll chat box dynamically
        self.chatBox.yview('end')
    
    # !!! --------------------------------------------------------------
    def GetColour(self, name): #!!!
        # For person in #wholist , assign colour
        if name not in self.user_colours:
            self.SetUserColour(name) 
        return self.user_colours[name]
    
    def SetUserColour(self, name): #!!!
        # If the user is not in the self.user_colours dict, assign a random colour
        if name not in self.user_colours:
            self.user_colours[name] = random.choice(self.colour_list)
        else:
            pass
    
    def IsEmote(self, text):
        ''' Check if text contains an emoticon !!! '''
        pass
    # end !!! --------------------------------------------------------------
    
    def UpdateUsers(self, data):
        ''' 
        Takes #wholist data, removes formatting, and displays result to user window.
        '''
        user_list = data
        self.userBox.delete(0, END)
        # Remove formatting
        user_list = user_list[1:]
        del user_list[-1]
        user_list = [x.strip(' ') for x in user_list]
        for item in user_list:
            if item == '\n':
                user_list.remove('\n')
                
        # Insert into a username list IP, name
        self.online_users = {}
        for x in range(0, len(user_list), 2):
            self.online_users[user_list[x+1]] = user_list[x]
            self.userBox.insert(END, user_list[x+1])
            self.SetUserColour(user_list[x+1]) #!!!
        
        
        #print(online_users)
        
            
    def Send(self, text):
        # Clear the chat bar
        self.chatText.delete(0, 'end')
        # Send the text to the server
        try:
            self.sock.sendall(bytes('{}'.format(text).encode()))
        except socket.error as socketerror: 
            print("Error: {}".format(socketerror))

    def ReceiveMessages(self):
        self.sock.connect((self.server, int(self.port)))
        self.sock.sendall(bytes('#login {}'.format(self.username).encode()))
        
        print('Connected to {}. Start sending messages'.format(self.server))
        while True:
            try: 
                received = self.sock.recv(1024)
                if received:
                    received = received.decode()
                    newstr = received.split(':', 1)
                    
                    if len(newstr) > 1:
                        name = newstr[0].strip('< >')
                        if(name == 'Connected'):
                            # Format wholist for display
                            self.UpdateUsers(received.split('|'))
                        else:
                            self.Display(newstr[1].strip(), name)
                    else:
                        self.Display(received.strip(), 'SERVER')
                        if received.strip()[-15:] == ' has logged in.': #last 15chars
                            print(received.strip()) #!!!
                            self.sock.sendall(b'#wholist') 
                        elif received.strip()[-18:] == ' has disconnected.':
                            print(received.strip()) #!!!
                            self.sock.sendall(b'#wholist')
                            
            except socket.error as socketerror:
                print(socketerror)
                break
            except:
                self.Quit()
                break

    def StartThread(self):
        threading.Thread(target=self.ReceiveMessages).start()

    def Quit(self):
        self.sock.close()
        self.root.destroy()

       
if __name__ == '__main__':
    client = ChatClient()