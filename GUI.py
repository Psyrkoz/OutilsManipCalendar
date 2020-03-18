from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP
from connexion import GoogleConnexion

class GUI:
    def __init__(self):
        if(GoogleConnexion.hasToken()):
            self.service = GoogleConnexion.connectToGoogle() # Si le token existe, on se connecte directement
            self.createGUIApplication()
        else:
            self.createGUIConnexion()

    def connexionGoogle(self):
        self.service = GoogleConnexion.connectToGoogle()
        self.window.destroy()

        self.createGUIApplication()

    def createGUIConnexion(self):
        # Cree la fenêtre
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Connexion au service Google")
        self.connexionTexte = Label(self.window, text="Une connexion au service Google est nécessaire!")
        self.button = Button(self.window, text="Connexion", command = self.connexionGoogle)

        # Ajoute les boutons dans la fenêtre et lance la boucle
        self.connexionTexte.pack()
        self.button.pack()
        self.window.mainloop()
    
    def createGUIApplication(self):
        # Cree la fenêtre
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Outils Manipulation calendrier Google")
        self.tabs = ttk.Notebook(self.window)
        self.creeTabAjout()
        self.creeTabExport()

        # Ajoute les éléments dans la fenêtre et lance la boucle
        self.tabs.add(self.tabAdd, text="Ajout")
        self.tabs.add(self.tabExport, text="Exportation")
        self.tabs.pack(expand=1, fill='both')
        self.window.mainloop()
    
    def creeTabExport(self):
        self.tabExport = ttk.Frame(self.tabs)
        # TODO: Crée la tab d'exportation

    def creeTabAjout(self):
        self.tabAdd = ttk.Frame(self.tabs)

        self.entryLine = ttk.Frame(self.tabAdd)
        self.label = Label(self.entryLine, text="Fichier .ics a ajouter dans le calendrier:")
        self.entry = Entry(self.entryLine)
        self.button = Button(self.entryLine, text = "...", command = self.askForICSFile)
        self.buttonAjouter = Button(self.tabAdd, text = "Ajouter", command = self.addICSFileToCalendar)

        self.label.pack(side=LEFT)
        self.entry.pack(expand=True, fill=X, side=LEFT)
        self.button.pack(side=LEFT)

        self.entryLine.pack()
        self.buttonAjouter.pack(expand=True, fill=X)


    def askForICSFile(self):
        pass

    def addICSFileToCalendar(self):
        pass

        