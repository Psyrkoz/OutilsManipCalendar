from __future__ import print_function
import datetime
import pickle
import os.path
from GUI import GUI
from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP, END, OptionMenu, StringVar, Event, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
import httplib2
import logging
import webbrowser

CLIENT_ID = "39952552618-b8ef9glbnbmresq50e4e1c7smfb08bls.apps.googleusercontent.com"
CLIENT_SECRET = "0gVxuIno5OPaSMmLiup2iLLt"
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleConnexion:

    def __init__(self):
        self.createInterface()

    def createInterface(self):
        # Cree la fenêtre
        logging.info("Création de l'interface graphique de la connexion")
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
        self.connexionTexte.pack(expand = True, fill = X)
        self.button.pack(expand = True, fill = X)
        if(self.buttonDisconnect is not None):
            self.buttonDisconnect.pack(expand = True, fill = X)
        self.window.mainloop()

    def copyUrlInClipBoard(self, urlTxt):
        self.window.withdraw()
        self.window.clipboard_clear()
        self.window.clipboard_append(urlTxt)
        self.window.update()

        messagebox.showinfo("Information", "Le lien a bien été copié dans le presse papier")

    def createComfirmNumberWindow(self, urlTxt):
        logging.info("Création de la fenêtre de connexion Google")
        self.comfirmNumberWindow = Tk()
        self.comfirmNumberWindow.title("Authentification Google")

        # Code pour l'url
        frameUrl = ttk.Frame(self.comfirmNumberWindow)
        labelUrl = Label(frameUrl, text="Lien cliquable:")
        url = Entry(frameUrl, width=50, fg="blue", bg=self.window.cget("bg"))
        url.insert(0, urlTxt)
        url.configure(state="readonly")
        url.bind("<Button-1>", lambda e: webbrowser.open_new(urlTxt))

        btnCopy = Button(frameUrl, text = "Copier le lien", command = lambda: self.copyUrlInClipBoard(urlTxt))

        labelUrl.pack(side=LEFT)
        url.pack(side=LEFT)
        btnCopy.pack(side=LEFT)

        # Code pour le code
        frameCode = ttk.Frame(self.comfirmNumberWindow)
        label = Label(frameCode, text="Code:")
        self.codeEntry = Entry(frameCode, width=50)
        label.pack(side=LEFT)
        self.codeEntry.pack(side=LEFT)

        # Code pour le bouton
        btnComfirm = Button(self.comfirmNumberWindow, text = "Valider le code", command = self.validateCodeAndSaveToPickle)

        frameUrl.pack()
        frameCode.pack()
        btnComfirm.pack()
        self.comfirmNumberWindow.mainloop()

    def connexionGoogle(self):
        self.connectToGoogle()
        self.window.destroy()

        gui = GUI(self.service)

    def otherAccountConnexionGoogle(self):
        logging.info("Déconnexion du compte Google enregistré")
        if(self.hasToken()):
            os.remove('token.pickle')
        self.connexionGoogle()

    @staticmethod
    def hasToken():
        return os.path.exists('token.pickle')
    
    @staticmethod
    def deleteToken():
        return os.remove('token.pickle')

    def validateCodeAndSaveToPickle(self):
        logging.info("Validation du code...")
        code_auth = self.codeEntry.get()
        try:
            creds = self.flow.step2_exchange(code=code_auth)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

            self.service = build('calendar', 'v3', credentials=creds)
            self.comfirmNumberWindow.destroy()
            self.window.destroy()
            g = GUI(self.service)
        except FlowExchangeError:
            messagebox.showerror("Code invalide", "Le code entrée n'est pas un code valide")
            logging.warning("Mauvais code de validation!")

    def connectToGoogle(self):
        logging.info("Connexion au compte google")
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            logging.info('Token de connexion trouvé')
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            self.service = build('calendar', 'v3', credentials=creds)
        # If there are no (valid) credentials available, let the user log in.
        else:
            logging.info("Aucun token de connexion trouvé... Lancement de la procédure de connexion.")
            self.flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, scope=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
            flow_info = self.flow.step1_get_authorize_url()
            self.createComfirmNumberWindow(flow_info)

        
    
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