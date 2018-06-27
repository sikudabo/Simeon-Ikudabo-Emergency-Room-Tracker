from twisted.internet import protocol, reactor

class ServerProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.state = 'Register'
        self.name = None

        #self.factory is a reference to the factory class that will store persistent information, such as the dictionary of users/transports. 
        #Create a state machine. Change it once we register the client. 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    def connectionMade(self):

        '''
        #Docstring: Handle an event in which we
        receive and accept a connection from a
        client. Send a welcome message 
        '''
        print('Connection from client at address: {}'.format(self.transport.getPeer()))
        welcome_message = 'Welcome to the MGH doctor chat!'
        ehlo_message = '\nEnter ehlo to connect to chat room'
        self.transport.write(welcome_message.encode('utf-8'))
        self.transport.write(ehlo_message.encode('utf-8'))
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def connectionFailed(self, reason):
        '''
        #Docstring: Handle a failed client connection attempt.
        '''
        print('Connection from a client failed')
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    def dataReceived(self, data):

        '''
        #Docstring: When data is first recieved, we need to decode that
        data. We also need to get the username of the patient
        who is sending the data, and get the peer name for the
        doctor that they are attempting to send the data to.
        '''

        #Decode the data that we have received from the client. 
        data = data.decode('utf-8')

        #Split the message on the delimiter '@'. Store the username, peername and message. 
        self.user, self.peer, self.msg = data.split('@')

        formatted_msg = '\n' + self.user + ': ' + self.msg
        entered_chat = '\n' + self.user + ' has entered the chatroom!'
        not_in_chat = '\n' + self.peer + ' is not currently in the chatroom.'

        #If the state is register, register the username and the transport that user is on.
        #Aler their peer that they have entered the chatroom. 
        if self.state == 'Register':
            self.factory.users[self.user] = self.transport
            #Change the state machine. 
            self.state = 'Chat'
            for peer, t in self.factory.users.items():
                if peer == self.peer:
                    t.write(entered_chat.encode('utf-8'))

        #Send the message to the peer. State who the message is from
        for peer, t in self.factory.users.items():
            if self.peer == peer:
                t.write(formatted_msg.encode('utf-8'))

        #If the peer isnot in the chatroom, let the client know. 
        if self.peer not in self.factory.users.keys():
            self.transport.write(not_in_chat.encode('utf-8'))
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
    def connectionLost(self, reason):

        '''
        Handle the event in which a connection is lost. Delete that
        user from the users dictionary in the factory class.
        '''

        print('Connection lost to client: {}, user: {}'.format(self.transport.getPeer(), self.user))

        #Delete the user who has lost their connection from the dictionary of users. 
        if self.user in self.factory.users.keys():
            del self.factory.users[self.user]
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        

class ServerFactory(protocol.Factory):

    def __init__(self):
        #Create an empty dict to store users and their transports. 
        self.users = {}

    def buildProtocol(self, addr):
        return ServerProtocol(self)

reactor.listenTCP(12345, ServerFactory())
reactor.run()
        
