from __future__ import print_function
import datetime
import pickle
import os.path
from GUI import GUI
from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP, END, OptionMenu, StringVar, Event
from tkinter.filedialog import askopenfilename, asksaveasfilename
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleConnexion:

    def __init__(self):
        self.createInterface()

    def createInterface(self):
        # Cree la fenêtre
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Connexion au service Google")
        self.connexionTexte = Label(self.window, text="Une connexion au service Google est nécessaire!")

        self.buttonDisconnect = None
        if(GoogleConnexion.hasToken()):
            textButton = "Connexion en utilisant le token"
            self.buttonDisconnect = Button(self.window, text="Connection a un autre compte Google", command = self.otherAccountConnexionGoogle)
        else:
            textButton = "Connexion a un compte Google"

        self.button = Button(self.window, text=textButton, command = self.connexionGoogle)

        # Ajoute les boutons dans la fenêtre et lance la boucle
        self.connexionTexte.pack()
        self.button.pack()
        if(self.buttonDisconnect is not None):
            self.buttonDisconnect.pack()
        self.window.mainloop()

    def connexionGoogle(self):
        service = GoogleConnexion.connectToGoogle()
        self.window.destroy()

        gui = GUI(service)

    def otherAccountConnexionGoogle(self):
        os.remove('token.pickle')
        self.window.destroy()

        self.createInterface()

    @staticmethod
    def hasToken():
        return os.path.exists('token.pickle')
    
    @staticmethod
    def deleteToken():
        return os.remove('token.pickle')

    @staticmethod
    def connectToGoogle():
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service
    
    @staticmethod
    def displayEvents(service):
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])