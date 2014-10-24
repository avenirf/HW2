import direct.directbase.DirectStart
from direct.showbase.DirectObject       import DirectObject      
from direct.gui.OnscreenText            import OnscreenText 
from direct.gui.DirectGui               import *
from pandac.PandaModules                import *
import socket
from direct.showbase.ShowBase import ShowBase
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from panda3d.core import ConnectionWriter
from panda3d.core import NetDatagram
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader

### client logic
# connect to patcher to see if update is available
# connect to login server
# send login credentials

class Login_Page(DirectObject):
    def __init__(self):
        base.setBackgroundColor( 254, 254, 254 )
        # sets the background color to black because the
        # default grey color bugs me for some reason
        
        self.loginScreen()
        # draws the login screen
        
        self.usernameBox['focus'] = 1
        # sets the cursor to the username field by default
        
        self.accept('tab', self.cycleLoginBox) 
        # enables the user to cycle through the text fields with the tab key
        # this is a standard feature on most login forms
        
        self.accept('enter', self.attemptLogin)         
        # submits the login form, or you can just click the Login button
        
    def loginScreen(self):
        # creates a basic login screen that asks for a username/password
        
        boxloc = Vec3(0.0, 0.0, 0.0)
        # all items in the login form will have a position relative to this
        # this makes it easier to shift the entire form around once we have 
        # some graphics to display with it without having to change the 
        # positioning of every form element
        
        # p is the position of the form element relative to the boxloc 
        # coordinates set above it is changed for every form element
        p = boxloc + Vec3(-0.5, 0, 0.0)                                 
        self.textObject = OnscreenText(text = "Username:", pos = p, scale = 0.07,fg=(0, 0, 0, 1),align=TextNode.ALeft)
        # "Username: " text that appears beside the username box
        
        p = boxloc + Vec3(-0.1, 0.0, 0.0)
        self.usernameBox = DirectEntry(text = "" , pos = p, scale=.05, initialText="", numLines = 1)
        # Username textbox where you type in your username
        
        p = boxloc + Vec3(-0.5, -0.1, 0.0)        
        self.textObject = OnscreenText(text = "Password:", pos = p, scale = 0.07,fg=(0, 0, 0, 1),align=TextNode.ALeft)
        # "Password: " text that appears beside the password box
        
        p = boxloc + Vec3(-0.1, 0, -0.1)
        self.passwordBox = DirectEntry(text = "" , pos = p, scale=.05, initialText="", numLines = 1, obscured = 1)
        # Password textbox where you type in your password
        # Note - obscured = 1 denotes that all text entered will be replaced 
        # with a * like a standard password box
        
        p = boxloc + Vec3(0, 0, -0.2)
        self.loginButton = DirectButton(text = ("Login", "Login", "Login", "Login"), pos = p, scale = 0.075, command=self.attemptLogin)
        # The 'Login' button that will trigger the attemptLogin function 
        # when clicked
        
        p = boxloc + Vec3(-0.5, -0.4, 0)
        self.statusText = OnscreenText(text = "", pos = p, scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ALeft)
        # A simple text object that you can display an error/status messages 
        # to the user
    
    def updateStatus(self, statustext):
        self.statusText.setText(statustext)
        # all this does is change the status text.

    def composeStringMessage(self, msg):
        myPyDatagram = PyDatagram()
        myPyDatagram.addString(msg)
        return myPyDatagram
                
    def retrieveStringMessage(self,datagram):
        myIterator = PyDatagramIterator(datagram)
        msg = myIterator.getString()
        print msg, " received"
        
    def sendRequest(self):
        if(self.received):
            print "->Client request:"
            # Send a request to the server             
        msg = self.usernameBox.get()+" "+self.passwordBox.get()
        request = self.composeStringMessage(msg)
        ack = self.cWriter.send(request,self.connection)                
        print msg, " sent"
        self.received = 0
        
    def receiveResponse(self):
        print "<-Server response:"
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            # Retrieve the contents of the datagram.
            if self.cReader.getData(datagram):
                self.retrieveStringMessage(datagram)
                self.received = 1           
        
    def communicate(self):
        #print "communicate"
        self.sendRequest()
        self.receiveResponse()   
            
    def updateRoutine(self,task):
        self.communicate()
        return task.again;     
    
    def attemptLogin(self):
        # checks to make sure the user inputed a username and password:
        #       if they didn't it will spit out an error message
        #       if they did, it will try to connect to the login server 
        #               (under construction)
        
        if(self.usernameBox.get() == ""):
            if(self.passwordBox.get() == ""):
                self.updateStatus("ERROR: You must enter a username and password before logging in.")
            else:
                self.updateStatus("ERROR: You must specify a username")
            self.passwordBox['focus'] = 0
            self.usernameBox['focus'] = 1
                
        elif(self.passwordBox.get() == ""):
            self.updateStatus("ERROR: You must enter a password")
            self.usernameBox['focus'] = 0
            self.passwordBox['focus'] = 1
            
        else:
            self.updateStatus("Attempting to login...")
            print "Attempting to connect to Server with credentials: (" + self.usernameBox.get() + ", " + self.passwordBox.get() + ")"
            # this is where the networking code will get put in
            self.cManager = QueuedConnectionManager()
            self.cListener = QueuedConnectionListener(self.cManager, 0)
            self.cReader = QueuedConnectionReader(self.cManager, 0)
            self.cWriter = ConnectionWriter(self.cManager, 0)
        
            HOST = "localhost";
            PORT = 1234;
            self.connection = self.cManager.openTCPClientConnection(HOST, PORT, 10000)    
            self.received = 1
            
            if self.connection:
                    self.cReader.addConnection(self.connection)                    
            #taskMgr.add(self.updateRoutine, 'updateRoutine')
            taskMgr.doMethodLater(3, self.updateRoutine, 'updateRoutine')
            
            
    def cycleLoginBox(self):
        # function is triggered by the tab key so you can cycle between 
        # the two input fields like on most login screens
        
        # IMPORTANT: When you change the focus to one of the text boxes, 
        # you have to unset the focus on the other textbox.  If you do not 
        # do this Panda seems to get confused.
        if(self.passwordBox['focus'] == 1):
            self.passwordBox['focus'] = 0
            self.usernameBox['focus'] = 1
        elif(self.usernameBox['focus'] == 1):
            self.usernameBox['focus'] = 0
            self.passwordBox['focus'] = 1  
        
loginPage = Login_Page()

run()
