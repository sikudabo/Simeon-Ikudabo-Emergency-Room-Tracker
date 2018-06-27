from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor, protocol
import kivy
from kivy.app import App
from kivy.clock import Clock
import pymysql
import datetime
from app_essentials import *
import datetime
import smtplib
from smtp_email import *
from twilio.rest import Client
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import json







##with open('symptoms_good.txt', 'r') as f:
##    lines = f.readlines()

'''
Create a class that will start the patient/doctor chat client for patients.
'''

class ChatProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def connectionMade(self):
        #On a connection send the transport to the app classes on_connect method. 
        self.factory.app.on_connect(self.transport)
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def dataReceived(self, data):

        '''
        Handles receiving data from the server.
        '''
        data = data.decode('utf-8')
        self.factory.app.receive_msg(data)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def clientConnectionLost(self, connector, reason):
        self.factory.app.connect_lost()
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def clientConnectionFailed(self, connector, reason):
        self.factory.app.connect_failed()
######################################################################################################################################################################    

class ChatFactory(protocol.ClientFactory):

    def __init__(self, app):
        self.app = app
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def buildProtocol(self, addr):
        return ChatProtocol(self)
########################################################################################################################################################################
        



class ErApp(App):

    def __init__(self, **kwargs):
        super(ErApp, self).__init__(**kwargs)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_to_chat_login(self, *args):
        self.root.current = 'Chat Login'
        self.root.ids.chat_logs.text = ''
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_to_chat_room(self, *args):
        self.root.current = 'Chat Room'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def connect(self):
        '''
        #Docstring: method that will allow us to begin a connection to the server.
        '''

        reactor.connectTCP('localhost', 12345, ChatFactory(self))
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_connect(self, conn):

        '''
        #Docstring: Class that will handle what to do once a connection to
        the server is made.
        Param: conn: We will store the transport connection in the variable
        conn.
        '''

        self.conn = conn
        self.root.ids.chat_login_label.text = 'Connection made...'
        self.root.ids.chat_logs.text += '\nConnection made to: {}'.format(self.conn.getPeer())
        Clock.schedule_once(self.change_to_chat_room, 3)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def receive_msg(self, msg):

        self.root.ids.chat_logs.text += '\n' + msg
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def connect_lost(self):
        self.root.ids.chat_logs.text += '\nConnection to the server lost...'
        Clock.schedule_once(self.change_to_chat_login, 3)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def connect_failed(self):
        self.root.ids.chat_login_label.text = 'Connection failed! \nTry again'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def disconnect(self):
        self.root.ids.chat_logs.text += '\nDisconnecting from the server...'
        self.conn.loseConnection()
        Clock.schedule_once(self.change_to_chat_login, 3)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def send_msg(self):
        self.msg = self.root.ids.patient_msg.text
        self.dr_name = self.root.ids.dr_chat_peer.text 
        format_msg = self.username + '@' + self.dr_name + '@' + self.msg
        self.conn.write(format_msg.encode('utf-8'))
        self.root.ids.chat_logs.text += '\n' + self.username + ': ' + self.msg
        self.root.ids.patient_msg.text = ''
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        
    def change_opening_screen(self, *args):
        '''
        #Docstring: Method that will change the opening
        screen 3 seconds after the user enters. I will
        change the screen to the Options Screen.
        '''
        
        #Here I call to change the 'root' screen.
        self.root.current = 'Options'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_start(self):
        '''
        #Docstring: Method that will call change screen
        method in order to change the screen 3 seconds
        after the user enters the application.
        '''

        #Here I schedule an event to change the screen.
        Clock.schedule_once(self.change_opening_screen, 10)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_to_new_name_info(self, *args):
        '''
        #Docstring: Method that will automatically
        change the screen after the user enters
        a correct new username and password.
        '''

        self.root.current = 'New_Name_Info'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_username_password(self):
        '''
        Method that will handle when a new user selects
        a username and password. I will have to ensure
        that their username and password is not already
        in the database, and then once I have ensured
        that, the username and password can be stored
        to the database.
        '''

        #Set the new_username variable = to the new username the user selects
        #Same for the new user password
        self.new_username = self.root.ids.new_username.text
        self.new_password = self.root.ids.new_password.text
        tuple_test = (self.new_username, self.new_password)

        #Check the database to get all of the usernames, passwords, and IDS from the database
        #Fetch all of the results.
        cur.execute('''SELECT * FROM patient_login''')
        results = cur.fetchall()

        #Iterate through each result. The usernames will be in index 1 of the tuple of results.
        #If the username that the user enters matches one that's in the system, give them an error message.
        #If the username is not in the results, commit it to the database along with the password, change screen.
        if results:
            for result in results:
                if result[1] == self.new_username:
                    self.root.ids.new_user_status.text = 'Select another username! Name Taken!'
                else:
                    cur.execute('''INSERT INTO patient_login(username, password) VALUES("%s", "%s")'''%(self.new_username, self.new_password))
                    mydb.commit()
                    self.root.ids.new_user_status.text = 'Success...'
                    self.username = self.new_username
                    self.password = self.new_password
                    Clock.schedule_once(self.change_to_new_name_info, 3)

        if not results:
            cur.execute('''INSERT INTO patient_login(username, password) VALUES("%s", "%s")'''%(self.new_username, self.new_password))
            mydb.commit()
            self.root.ids.new_user_status.text = 'Success...'
            self.username = self.new_username
            self.password = self.new_password
            Clock.schedule_once(self.change_to_new_name_info, 3)
            
                
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def change_new_health_info(self, *args):
        self.root.current = 'New_Health_Info'
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def create_new_real_name(self):
        '''
        #Docstring: Method that will insert the new patients first name,
        last name, birthday, and ssn into the database.
        '''

        #Fetch the users unique identification from the database so that we can store it in the program.
        cur.execute('''SELECT ID FROM patient_login WHERE username="%s"'''%(self.new_username))
        _id = cur.fetchall()
        _id = _id[0]
        self.id = int(_id[0])

        #Store all of the patients new information in variables.
        self.first_name = self.root.ids.new_first_name.text
        self.last_name = self.root.ids.new_last_name.text
        self.birthdate = self.root.ids.new_birthdate.text
        self.ssn = self.root.ids.new_ssn.text
        
        #Try to update the patient's core information to the database.
        try:
            cur.execute('''INSERT INTO patient_core_info(ID, first_name, last_name, birthday, ssn) VALUES("%d", "%s", "%s", "%s", "%s")'''
                        %(self.id, self.first_name, self.last_name, self.birthdate, self.ssn))
            mydb.commit()
            self.root.ids.new_name_status.text = 'Success...'
            Clock.schedule_once(self.change_new_health_info, 3)

        #Add an exception handler so that the App doesn't class in case of an error.
        except:
            self.root.ids.new_name_status.text = 'Error! Try Again'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def contact_info_change(self, *args):
        '''
        #Docstring: Method that will change the screen to
        the new patient contact screen once the patient has
        entered their health information.
        '''

        self.root.current = 'New_Contact'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def new_health_info(self):
        '''
        #Method that will help us store a new users health information such as
        their current medical conditions, prior medical conditions, current medications,
        prior medications, prior surgeries, allergies, and insurance information.
        '''

        #Store the user input into variables
        self.prior_conditions = self.root.ids.new_prior_conditions.text
        self.current_conditions = self.root.ids.new_current_conditions.text
        self.current_medications = self.root.ids.new_current_medications.text
        self.prior_medications = self.root.ids.new_prior_medications.text
        self.surgeries = self.root.ids.new_prior_surgeries.text
        self.allergies = self.root.ids.new_allergies.text
        self.insurance = self.root.ids.new_insurance_provider.text

        #Now try to store all of this information into the database.
        try:
            cur.execute('''INSERT INTO patient_health_info(ID, prior_conditions, current_conditions, current_medications, prior_medications, prior_surgeries, allergies, insurance) VALUES("%d", "%s", "%s", "%s", "%s", "%s", "%s", "%s")'''
                        %(self.id, self.prior_conditions, self.current_conditions, self.current_medications, self.prior_medications, self.surgeries, self.allergies,
                          self.insurance))
            mydb.commit()
            self.root.ids.new_health_info_status.text = 'Success...'
            Clock.schedule_once(self.contact_info_change, 3)

        #Handle any errors so that the app doesn't crash. 
        except:
            self.root.ids.new_health_info_status.text = 'Error! Try again'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def goto_options_screen(self, *args):
        self.root.current = 'Options'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def new_contact_info(self):
        '''
        #Docstring: A method that will enable the user to store
        their key contact information such as their phone number,
        email address, address, city, state, and zip code. The
        phone number and email address can be used to later update
        the user on their emergency room wait time, and other information via
        text messaging and email updates.
        '''

        #Store all of the patient's contact information in variables based on their input. 
        self.phone_number = self.root.ids.new_phone_number.text
        self.email = self.root.ids.new_email.text
        self.address = self.root.ids.new_address.text
        self.city = self.root.ids.new_city.text
        self.state = self.root.ids.new_state.text
        self.zip_code = self.root.ids.new_zip.text

        #Try to store the information in the databse
        try:
            cur.execute('''INSERT INTO patient_contact(ID, phone_number, email, address, city, state, zip) VALUES("%d", "%s", "%s", "%s", "%s", "%s", "%s")'''
                            %(self.id, self.phone_number, self.email, self.address, self.city, self.state, self.zip_code))
            mydb.commit()
            self.root.ids.new_contact_status.text = 'Done...'
            #GOTO the options screen.
            Clock.schedule_once(self.goto_options_screen, 3)

        #Handle any errors with an exception to prevent the app from crashing. 
        except:
            self.root.ids.new_contact_status.text = 'Error! Try again'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def return_user_signin(self):
        '''
        #DOCSTRING: Method that will help a return user sign in and retrieve
        all of the information that they have previously entered into the
        database.
        '''

        #Store the fact that they are a return user in a Boolean expression.
        self.return_user = True

        #Store the user input in variables (username and password).
        self.username = self.root.ids.return_username.text
        self.password = self.root.ids.return_password.text
        test_tuple = (self.username, self.password)

        #Now test to see if the username and password is in the database
        cur.execute('''SELECT * FROM patient_login''')
        results = cur.fetchall()
        #ID, first_name, last_name, birthday, ssn
        tuple_list = []

        for result in results:
            tuple_list.append(result[1:3])

        if test_tuple in tuple_list:
            

            try:
                cur.execute('''SELECT ID FROM patient_login WHERE username="%s"'''
                                %(self.username))
                results = cur.fetchall()
                _id = results[0]
                self.id = _id[0]
                self.root.ids.return_user_status.text = 'Success... Press Retreive Data'

                #Flag to handle whether or not the return user has signed in. 
                self.return_user_signed_in = True

            except:
                self.root.ids.return_user_status.text = 'Error'

        else:
            self.root.ids.return_user_status.text = 'Incorrect username or password. Try again.'
            self.root.ids.return_username.text = ''
            self.root.ids.return_password.text = ''
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def go_to_retrieval(self, *args):
        self.root.current = 'Stored_Info'
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def retrieve_data(self):
        '''
        #Docstring: Method that I will bind to a button to allow the user to retrieve their data from
        the database. Will query the db where the users id matches up in the various tables, pull that
        data from the tables, and then store that data in variables.
        '''

        #Try to grab all of the users data from the database 
        try:

            #First grab the patients core information. Query the database. 
            cur.execute('''SELECT first_name, last_name, birthday, ssn FROM patient_core_info WHERE ID="%d"'''
                        %(self.id))
            results = cur.fetchall()
            results = results[0]
            self.first_name = results[0]
            self.last_name = results[1]
            self.birthdate = results[2]
            self.ssn = results[3]

            #Next grab the patients health information
            cur.execute('''SELECT prior_conditions, current_conditions, current_medications, prior_medications, prior_surgeries, allergies, insurance FROM patient_health_info WHERE ID="%d"'''
                        %(self.id))
            results = cur.fetchall()
            results = results[0]
            self.prior_conditions = results[0]
            self.current_conditions = results[1]
            self.current_medications = results[2]
            self.prior_medications = results[3]
            self.surgeries = results[4]
            self.allergies = results[5]
            self.insurance = results[6]

            #Now retrieve the patient's contact data. 
            cur.execute('''SELECT phone_number, email, address, city, state, zip FROM patient_contact WHERE ID="%d"'''
                        %(self.id))

            results = cur.fetchall()
            results = results[0]
            self.phone_number = results[0]
            self.email = results[1]
            self.address = results[2]
            self.city = results[3]
            self.state = results[4]
            self.zip_code = results[5]

            #Let the user know that it was successful
            self.root.ids.return_user_status.text = 'Successful data retrieval'
            Clock.schedule_once(self.go_to_retrieval, 3)
            Clock.schedule_once(self.patient_info_retrieval, 3)

        #Handle any errors in an exception block
        except:
            self.root.ids.return_user_status.text = 'Error Generating information'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def patient_info_retrieval(self, *args):

        '''
        #Docstring: Method that will actually enable the patient to see their
        retrieved information on a page. There will also be a screen for the
        patient to have the ability to alter their information after this
        screen if they choose to. We can use their ID to highlight where they
        should alter their information.
        '''

        self.root.ids.patient_info_status.text = 'Patient Name: {} {}'.format(self.first_name, self.last_name)
        self.root.ids.patient_info_retrieved.text += '\nBirthday: {}'.format(self.birthdate)
        self.root.ids.patient_info_retrieved.text += '\nSSN: {}'.format(self.ssn)
        self.root.ids.patient_info_retrieved.text += '\nPrior Conditions: {}'.format(self.prior_conditions)
        self.root.ids.patient_info_retrieved.text += '\nCurrent Conditions: {}'.format(self.current_conditions)
        self.root.ids.patient_info_retrieved.text += '\nCurrent Medications: {}'.format(self.current_medications)
        self.root.ids.patient_info_retrieved.text += '\nPrior Medications: {}'.format(self.prior_medications)
        self.root.ids.patient_info_retrieved.text += '\nSurgeries: {}'.format(self.surgeries)
        self.root.ids.patient_info_retrieved.text += '\nAllergies: {}'.format(self.allergies)
        self.root.ids.patient_info_retrieved.text += '\nInsurance: {}'.format(self.insurance)
        self.root.ids.patient_info_retrieved.text += '\nPhone: {}'.format(self.phone_number)
        self.root.ids.patient_info_retrieved.text += '\nEmail: {}'.format(self.email)
        self.root.ids.patient_info_retrieved.text += '\nAddress: {}'.format(self.address)
        self.root.ids.patient_info_retrieved.text += '\nCity: {}'.format(self.city)
        self.root.ids.patient_info_retrieved.text += '\nState: {}'.format(self.state)
        self.root.ids.patient_info_retrieved.text += '\nZip: {}'.format(self.zip_code)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    def alter_conditions(self):

        '''
        #Docstring: Method that will allow the patient to update
        their conditions in the database, and remove their old
        data.
        '''

        #Create a variable for the altered conditions.
        self.alter_c = self.root.ids.alter_current_conditions.text

        cur.execute('''UPDATE patient_health_info SET current_conditions="%s" WHERE ID="%d"''' %(self.alter_c, self.id))
        mydb.commit()
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_medications(self):

        '''
        #Docstring: Method that will allow the patient to update
        the medications that they are currently taking.
        '''

        #Create a variable for the altered medications.
        self.alter_m = self.root.ids.alter_current_medications.text

        cur.execute('''UPDATE patient_health_info SET current_medications="%s" WHERE ID="%d"'''%(self.alter_m, self.id))
        mydb.commit()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_surgeries(self):

        '''
        #Docstring: Method that will allow a patient to update
        the surgeries that they have had.
        '''

        #Create a variable to store the altered surgeries
        self.alter_s = self.root.ids.alter_surgeries.text

        cur.execute('''UPDATE patient_health_info SET prior_surgeries="%s" WHERE ID="%d"'''%(self.alter_s, self.id))
        mydb.commit()

    def alter_allergies(self):

        '''
        #Docstring: Method that will allow the patient to update
        the allergies that they have.
        '''

        #Create a variable to store the altered allergies
        self.alter_a = self.root.ids.alter_allergies.text

        cur.execute('''UPDATE patient_health_info SET allergies="%s" WHERE ID="%d"'''%(self.alter_a, self.id))
        mydb.commit()
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_insurance(self):

        '''
        #Docstring: Method that will allow the patient to update
        their insurance provider
        '''

        #Create a variable to store the altered insurance.
        self.alter_i = self.root.ids.alter_insurance.text

        cur.execute('''UPDATE patient_health_info SET insurance="%s" WHERE ID="%d"'''%(self.alter_i, self.id))
        mydb.commit()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_phone(self):

        '''
        #Docstring: Method that will allow the patient to update
        their phone number.
        '''

        #Create a variable to store the altered phone number
        self.alter_p = self.root.ids.alter_phone.text

        cur.execute('''UPDATE patient_contact SET phone_number="%s" WHERE ID="%d"'''%(self.alter_p, self.id))
        mydb.commit()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_email(self):

        '''
        #Docstring: Method that will allow the patient to update
        their email address.
        '''

        #Create a variable to store the altered email address
        self.alter_e = self.root.ids.alter_email.text

        cur.execute('''UPDATE patient_contact SET email="%s"WHERE ID="%d"'''%(self.alter_e, self.id))
        mydb.commit()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def alter_address(self):

        '''
        #Docstring: Method that will allow the patient to update
        their address, city, state and zip
        '''

        #Create variables to alter the addresses
        self.alter_addr = self.root.ids.alter_address.text
        self.alter_cit = self.root.ids.alter_city.text
        self.alter_st = self.root.ids.alter_state.text
        self.alter_z = self.root.ids.alter_zip.text

        cur.execue('''UPDATE patient_contact SET address="%s", city="%s", state="%s", zip="%s" WHERE ID="%d"'''
                   %(self.alter_addr, self.alter_cit, self.alter_st, self.alter_z, self.id))
        mydb.commit()
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def er_login(self):

        '''
        #Docstring: Method that will enable the user to enter their information into the ER
        login page. They will be able to enter their current symptoms and what is bringing them
        in today. They can enter that information as a "text" datatype in the MySql database.
        '''

        #Store the current patient health status in variables.
        self.er_symptoms = self.root.ids.er_symptoms.text
        self.brief_description = self.root.ids.er_brief_description.text
        try:
            #Store the data in the database
            cur.execute('''INSERT INTO patient_er_sign_in(ID, symptoms, brief_description) VALUES("%d", "%s", "%s")'''
                        %(self.id, self.er_symptoms, self.brief_description))
            mydb.commit()

        except:
            self.root.ids.er_login_status = 'Error! Please try again!'
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def select_appointment(self):

        '''
        #Docstring: Function that will allow the patient to
        select an available appointment time on a specified
        date.
        '''

        #Run a query to select all of the possible times. 
        cur.execute('''SELECT * FROM appointment_times''')
        #fetchall() query results 
        results = cur.fetchall()

        #Get the time results in a tuple
        #result_1 = results[0]
        #print(result_1[0])
        #print(results[1])

        #Within that tuple, grab each time result. 
        self.t_1 = results[0]
        self.t_1 = self.t_1[0]
        self.t_2 = results[1]
        self.t_2 = self.t_2[0]
        self.t_3 = results[2]
        self.t_3 = self.t_3[0]
        self.t_4 = results[3]
        self.t_4 = self.t_4[0]

        #Format the time result to a user friendly time. 
        self.formatted_time_1 = self.t_1.strftime('%B,%d, %Y %I:%M%p')
        self.formatted_time_2 = self.t_2.strftime('%B,%d, %Y %I:%M%p')
        self.formatted_time_3 = self.t_3.strftime('%B,%d, %Y %I:%M%p')
        self.formatted_time_4 = self.t_4.strftime('%B,%d, %Y %I:%M%p')

        #Format the buttons to neatly display the times for the user to select from
        self.root.ids.time_1.text = self.formatted_time_1
        self.root.ids.time_2.text = self.formatted_time_2
        self.root.ids.time_3.text = self.formatted_time_3
        self.root.ids.time_4.text = self.formatted_time_4
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def button1_selection(self):

        '''
        #Docstring: Method that will handle a button_1 press.
        We will record the time that the patient selected and
        store it in the db/change the screen.
        '''

        #Delete time from appointment_times table
        cur.execute('''DELETE FROM appointment_times WHERE appointment="%s"'''
                    %(self.t_1))
        mydb.commit()

        #Store it in the DB
        try:
            cur.execute('''INSERT INTO selected_appointment_times(ID, time) VALUES("%d", "%s")'''
                                %(self.id, self.t_1))
            mydb.commit()
            self.root.ids.select_appointment_error.text = "Selected: {}".format(self.formatted_time_1)
            self.selected_time = self.t_1
            self.event = Clock.schedule_interval(self.countdown_timer, 1)
            self.event()
            #Schedule the event to send the user an opening message 
            Clock.schedule_once(self.send_opening_message, 1)

        except:
            self.root.ids.select_appointment_error.text = "Error! Select another time!"
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def button2_selection(self):

        '''
        #Docstring: Method that will handle a button_2 press.
        We will record the time that the patient selected and
        store it in the db/change the screen.
        '''

        #Delete time from appointment_times table
        cur.execute('''DELETE FROM appointment_times WHERE appointment="%s"'''
                    %(self.t_2))
        mydb.commit()

        #Store it in the DB
        try:
            cur.execute('''INSERT INTO selected_appointment_times(ID, time) VALUES("%d", "%s")'''
                            %(self.id, self.t_2))
            mydb.commit()
            self.root.ids.select_appointment_error.text = "Selected: {}".format(self.formatted_time_2)
            self.selected_time = self.t_2
            self.event = Clock.schedule_interval(self.countdown_timer, 1)
            self.event()
            #Schedule the event to send the user an opening message
            Clock.schedule_once(self.send_opening_message, 1)

        #Store it in the DB
        except:
            self.root.ids.select_appointment_error.text = "Error! Select another time!"
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def button3_selection(self):

        '''
        #Docstring: Method that will handle a button_3 press.
        We will record the time that the patient selected and
        store it in the db/change the screen.
        '''

        #Delete time from appointment_times table
        cur.execute('''DELETE FROM appointment_times WHERE appointment="%s"'''
                    %(self.t_3))
        mydb.commit()

        #Store it in the DB
        try:
            cur.execute('''INSERT INTO selected_appointment_times(ID, time) VALUES("%d", "%s")'''
                            %(self.id, self.t_3))
            mydb.commit()
            self.root.ids.select_appointment_error.text = "Selected: {}".format(self.formatted_time_3)
            self.selected_time = self.t_3
            self.event = Clock.schedule_interval(self.countdown_timer, 1)
            self.event()
            #Schedule the event to send the user an opening message
            Clock.schedule_once(self.send_opening_message, 1)

        except:
            self.root.ids.select_appointment_error.text = "Error! Select another time!"
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def button4_selection(self):

        '''
        #Docstring: Method that will handle a button_4 press.
        We will record the time that the patient selected and
        store it in the db/change the screen.
        '''

        #Delete time from appointment_times table
        cur.execute('''DELETE FROM appointment_times WHERE appointment="%s"'''
                    %(self.t_4))
        mydb.commit()

        #Store it in the DB
        try:
            cur.execute('''INSERT INTO selected_appointment_times(ID, time) VALUES("%d", "%s")'''
                            %(self.id, self.t_4))
            mydb.commit()
            self.root.ids.select_appointment_error.text = "Selected: {}".format(self.formatted_time_4)
            self.selected_time = self.t_4
            self.event = Clock.schedule_interval(self.countdown_timer, 1)
            self.event()
            #Schedule the event to send the user an opening message 
            Clock.schedule_once(self.send_opening_message, 1)

        except:
            self.root.ids.select_appointment_error.text = "Error! Select another time!"
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def send_opening_message(self, *args):

        '''
        #Docstring: Will send the opening email to the user that lets them know that
        their appointment has been scheduled. We only need to schedule this event 1
        time. Also send a text messages.

        Param: args: arbitrary number of arguments that the clock will call to this method. 
        '''
        self.smtpObject = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtpObject.ehlo()
        self.smtpObject.starttls()
        self.smtpObject.login(hospital_email, hospital_password)
        self.smtpObject.sendmail(hospital_email, self.email,
                                 'Subject: Appointment\nYour appointment has been scheduled!'
                                 )
        #Send text
        twilioCli.messages.create(body='Your appointment has been scheduled!',
                                  from_=myTwilioNumber, to=self.phone_number)
        
        
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def countdown_timer(self, *args):

        '''
        #Docstring: Method that will countdown the amount of time
        until an appointment for a patient, and show the patient
        how much tme they have until their appointment. It will
        also send text and email updates based on the time that
        they have remaining until their appointment. Pass *args
        for an arbitrary number of arguments since we will be
        calling the method once per second to update the wait
        time. Call event.cancel() when the timer reaches 0. 
        '''

        #Switch to the Countdown_Timer screen so that the patient can see their countdown time. 
        self.root.current = 'Countdown_Timer'

        #Get the current time. 
        self.current_time = datetime.datetime.now()

        #Get a time delta object between the two times in a timedelta.
        self.delta = self.selected_time - self.current_time

        #Format the countdown time and display it on the label so that the patient can see their wait time.
        self.total_seconds = self.delta.total_seconds()
        self.hours, self.remainder = divmod(self.total_seconds, 3600)
        self.minutes, self.seconds = divmod(self.remainder, 60)
        self.formatted_delta = 'Days {} {}:{}:{}'.format(self.delta.days, int(self.hours), int(self.minutes), int(self.seconds))
        self.root.ids.countdown_label.text = self.formatted_delta

        #Now send them a 1 hour warning.
        if self.minutes == 59 and self.hours == 0 and self.seconds <= 2:
            #Create a simple mail transfer protocol object. 
            self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

            #Say 'ehlo' to the gmail smtp server in order to establish a connection
            self.smtpObj.ehlo()

            #Start the tls
            self.smtpObj.starttls()

            #Login to the hospital email account
            self.smtpObj.login(hospital_email, hospital_password)

            self.smtpObj.sendmail(hospital_email, self.email,
                                  'Subject: Appointment\nYou Have 1 hour remaining until your appointment!')
            self.smtpObj.quit()

            #Send a text message
            twilioCli.messages.create(body='You have 1 hour until your appointment',
                                      from_=myTwilioNumber, to=self.phone_number)

            

           

        #Now send them a 30 minute warning
        if self.minutes == 30 and self.hours == 0 and self.seconds <= 2:
            #Create a simple mail transfer protocol object. 
            self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

            #Say 'ehlo' to the gmail smtp server in order to establish a connection
            self.smtpObj.ehlo()

            #Start the tls
            self.smtpObj.starttls()

            #Login to the hospital email account
            self.smtpObj.login(hospital_email, hospital_password)

            self.smtpObj.sendmail(hospital_email, self.email,
                                  'Subject: Appointment\nYou have 30 minutes until your appointment!')
            self.smtpObj.quit()

            #Send text message
            twilioCli.messages.create(body='You have 30 minutes until your appointment!',
                                      from_=myTwilioNumber, to=self.phone_number)

            

        #Now send them a 5 minute warning and let them know it is time to be here.
        if self.minutes == 5 and self.minutes == 0 and self.seconds <= 2:
            
            #Create a simple mail transfer protocol object. 
            self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

            #Say 'ehlo' to the gmail smtp server in order to establish a connection
            self.smtpObj.ehlo()

            #Start the tls
            self.smtpObj.starttls()

            #Login to the hospital email account
            self.smtpObj.login(hospital_email, hospital_password)
            self.smtpObj.sendmail(hospital_email, self.email,
                                  'Subject: Appointment\nYou have 5 minutes until your appointment. ' +
                                  'It is hospital policy that you arrive at least 5 minutes before your appointment!')
            self.smtpObj.quit()

            #Send text message 
            twilioCli.messages.create(body='You have 5 minutes until your appointment',
                                      from_=myTwilioNumber, to=self.phone_number)

        #Now let them know that it is time for their appointment
        if self.delta.days <= 0 and self.minutes <= 0 and self.seconds <= 10:

            self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

            #Say 'ehlo' to the gmail smtp server in order to establish a connection
            self.smtpObj.ehlo()

            #Start the tls
            self.smtpObj.starttls()

            #Login to the hospital email account
            self.smtpObj.login(hospital_email, hospital_password)

            
            self.smtpObj.sendmail(hospital_email, self.email,
                                  'Subject: Appointment\nWe are ready to see you!')
            self.root.ids.countdown_label.text = 'We are ready to see you!'

            twilioCli.messages.create(body='We are ready to see you!',
                                      from_=myTwilioNumber, to=self.phone_number)
            
            self.event.cancel()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def calc_bmi(self):

        '''
        #Docstring: Method that allows the patient to track their bmi and stay on
        top of their weight to help health outcomes
        '''

        #Store height and weight in variables.
        self.weight = self.root.ids.weight.text
        self.height = self.root.ids.height.text

        self.weight = int(self.weight)
        self.height = int(self.height)
        self.height = self.height ** 2
        self.bmi = (self.weight * 703) / self.height

        self.root.ids.bmi_label.text = 'Your BMI is {}'.format(self.bmi)

        if self.bmi <= 18:
            self.root.ids.bmi_label.text += "\nYou are under weight"

        elif self.bmi >= 18 and self.bmi < 25:
            self.root.ids.bmi_label.text += '\nYou are in the normal weight range'

        elif self.bmi >= 25 and self.bmi <= 30:
            self.root.ids.bmi_label.text += '\nYou are overweight'

        elif self.bmi > 30:
            self.root.ids.bmi_label.text += '\nYou are obese'
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def immunization(self):
        '''
        #Docstring: Store data on immunization information.
        '''

        self.root.ids.immunization_label.text = ('Immunization remains the best means of preventing many infectious diseases. Recommended immunization shedules ' +
                                                 'for chidlren and adolescents can be found online at http://www.cdc.gov.vaccines/schedules/hcp/child-adolescent.html.'+
                                                 'Annual influenza vaccination is safe and effective with potential benefits in all age groups. The advisory Committee ' +
                                                 'on Inmmunization Practices (ACIP) recommends routine influenza vaccincation for all persons aged 6 months and older. ' +
                                                 'Please come to our hospital and receive a free flu vaccine each year for your entire family in order to reduce the ' +
                                                 'risk of illness in the future. Proper immunization has been proven to reduce future health expenditures during a time ' +
                                                 'when health expenditures have grown substantially in the United States during the past 50 years. ')
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def ask_symptom_question(self):

        '''
        #Docstring: A method that will allow the patient to ask a question to the machine based on their
        symptoms. The machine will list which disease the patient could potentially have!
        '''

        #Open the file that stores disease information.
        with open('symptoms_dict.json', 'r') as f:
            health = json.load(f)

            
        self.root.ids.q_logs.text = 'MGH: Ask a question.'

        data = self.root.ids.ask_q.text
        data = data.split()

        for item in data:
            for data_point in health:
                for disease, symptoms in data_point.items():
                        if item == symptoms:
                            self.root.ids.q_logs.text += '\nMGH: You could have ' + disease
                            self.root.ids.ask_q.text = ''
                            
                                
                                       
                
        
    
        
    

    
        
            

        
        
        
                
            
    

    
    
    

        

        
    








if __name__ == '__main__':
    ErApp().run()
