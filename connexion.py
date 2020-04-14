from __future__ import print_function
import datetime
import pickle
import os.path
from GUI import GUI
from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP, END, OptionMenu, StringVar, Event, messagebox, Listbox, END
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
        #self.createInterfaceSelectionCompte()
        # Cree la fenêtre
        logging.info("Création de l'interface graphique de la connexion")
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Connexion au service Google")
        self.connexionTexte = Label(self.window, text="Une connexion au service Google est nécessaire!")

        self.button = None
        self.buttonAddAccount = None
        if(GoogleConnexion.getAllTokens()):
            textButton = "Connexion a un compte enregistré"
            self.button = Button(self.window, text=textButton, command = self.createManageAccountInterface)
        
        self.buttonAddAccount = Button(self.window, text="Ajouter un compte Google", command = self.createAddAccountInterface)

        

        # Ajoute les boutons dans la fenêtre et lance la boucle
        self.connexionTexte.pack(expand = True, fill = X)
        if(self.button is not None):
            self.button.pack(expand = True, fill = X)
        self.buttonAddAccount.pack(expand = True, fill = X)
        self.window.mainloop()

    def createManageAccountInterface(self):
        self.selectionCompte = Tk()
        self.selectionCompte.title("Sélection du compte")
        self.listeCompte = Listbox(self.selectionCompte, selectmode = "single")
        self.listeCompte.insert(0, *GoogleConnexion.getAllTokens())
        self.listeCompte.pack(expand=True, fill=X)

        btnConnectWithThisPickle = Button(self.selectionCompte, text = "Se connecter avec se compte", command = lambda: self.connexionGoogle(self.listeCompte.get(self.listeCompte.curselection())))
        btnConnectWithThisPickle.pack(expand=True, fill=X)
        
        btnDisconnectThisPickle = Button(self.selectionCompte, text = "Déconnecter ce compte", command = self.deleteTokenAndRefreshList)
        btnDisconnectThisPickle.pack(expand=True, fill=X)

        btnBack = Button(self.selectionCompte, text = "Retour", command = self.selectionCompte.destroy)
        btnBack.pack(expand=True, fill=X)
        self.selectionCompte.mainloop()
    
    def deleteTokenAndRefreshList(self):
        GoogleConnexion.deleteToken(self.listeCompte.get(self.listeCompte.curselection()))
        self.listeCompte.delete(0, END)
        self.listeCompte.insert(0, *GoogleConnexion.getAllTokens())

    def createAddAccountInterface(self):
        self.flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, scope=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
        flow_info = self.flow.step1_get_authorize_url()
        self.createComfirmNumberWindow(flow_info)

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

        # Code pour le nom du compte
        frameName = ttk.Frame(self.comfirmNumberWindow)
        labelAccountName = Label(frameName, text = "Nom du compte")
        entryAccountName = Entry(frameName)
        labelAccountName.pack(side=LEFT)
        entryAccountName.pack(side=LEFT)

        # Code pour le code
        frameCode = ttk.Frame(self.comfirmNumberWindow)
        label = Label(frameCode, text="Code:")

        self.codeEntry = Entry(frameCode, width=50)
        label.pack(side=LEFT)
        self.codeEntry.pack(side=LEFT)

        # Code pour le bouton
        btnComfirm = Button(self.comfirmNumberWindow, text = "Valider le code", command = lambda: self.validateCodeAndSaveToPickle(entryAccountName.get()))

        frameUrl.pack()
        frameName.pack()
        frameCode.pack()
        btnComfirm.pack()
        self.comfirmNumberWindow.mainloop()

    def connexionGoogle(self, name):
        self.connectToGoogle(name)
        self.window.destroy()
        self.selectionCompte.destroy()

        gui = GUI(self.service)

    @staticmethod
    def getAllTokens():
        return [f.split(".pickle")[0] for f in os.listdir("./") if f.endswith(".pickle")]
    
    @staticmethod
    def deleteToken(name):
        if(os.path.exists(name + '.pickle')):
            os.remove(name + '.pickle')

    def validateCodeAndSaveToPickle(self, name):
        if(name == ''):
            messagebox.showinfo("Nom", "Vous devez donner un nom a ce compte")
            return
            
        logging.info("Validation du code...")
        code_auth = self.codeEntry.get()
        try:
            creds = self.flow.step2_exchange(code=code_auth)
            # Save the credentials for the next run
            with open(name + '.pickle', 'wb') as token:
                pickle.dump(creds, token)

            self.service = build('calendar', 'v3', credentials=creds)
            self.comfirmNumberWindow.destroy()
            self.window.destroy()
            self.createInterface()
        except FlowExchangeError:
            messagebox.showerror("Code invalide", "Le code entrée n'est pas un code valide")
            logging.warning("Mauvais code de validation! (Code = " + code_auth + ")")

    def connectToGoogle(self, name):
        logging.info("Connexion au compte google")
        creds = None
        if os.path.exists(name + '.pickle'):
            logging.info('Token de connexion trouvé')
            with open(name + '.pickle', 'rb') as token:
                creds = pickle.load(token)
            self.service = build('calendar', 'v3', credentials=creds)
        else:
            logging.error("Le token '" + name + "' est introuvable...")

        
    
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