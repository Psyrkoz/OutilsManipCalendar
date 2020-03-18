from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP, END
from tkinter.filedialog import askopenfilename
from connexion import GoogleConnexion
from DateEntry import DateEntry

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
        
        self.tabs.pack(expand=1, fill='both')
        self.window.mainloop()
    
    def creeTabExport(self):
        self.tabExport = ttk.Frame(self.tabs)

        # Date
        self.lineDate = ttk.Frame(self.tabExport)
        self.dateDebut = Label(self.lineDate, text = "Date début")
        self.dateDebutEntry = DateEntry(self.lineDate)
        self.dateFin = Label(self.lineDate, text = "Date fin")
        self.dateFinEntry = DateEntry(self.lineDate)
        self.dateDebut.pack(side=LEFT)
        self.dateDebutEntry.pack(side=LEFT)
        self.dateFin.pack(side=LEFT)
        self.dateFinEntry.pack(side=LEFT)

        #Bouton
        self.buttonExport = Button(self.tabExport, text = "Exporter données")

        self.lineDate.pack()
        self.buttonExport.pack(expand=True, fill=X)
        self.tabs.add(self.tabExport, text="Exportation")
        

    def creeTabAjout(self):
        self.tabAdd = ttk.Frame(self.tabs)

        self.entryLine = ttk.Frame(self.tabAdd)
        self.labelAskICSFile_Add = Label(self.entryLine, text="Fichier .ics a ajouter dans le calendrier:")
        self.entryICSFile_Add = Entry(self.entryLine)
        self.buttonAskICSFile_Add = Button(self.entryLine, text = "...", command = self.askForICSFile)
        self.buttonAjouter = Button(self.tabAdd, text = "Ajouter", command = self.addICSFileToCalendar)

        self.labelAskICSFile_Add.pack(side=LEFT)
        self.entryICSFile_Add.pack(expand=True, fill=X, side=LEFT)
        self.buttonAskICSFile_Add.pack(side=LEFT)

        self.entryLine.pack()
        self.buttonAjouter.pack(expand=True, fill=X)
        self.tabs.add(self.tabAdd, text="Ajout")


    def askForICSFile(self):
        filename = askopenfilename(title="Selectionner un fichier ICS", filetypes=(("iCalendar File", "*.ics"), ("All Files", "*.*")))
        self.entryICSFile_Add.delete(0, END)
        self.entryICSFile_Add.insert(0, filename)

    def addICSFileToCalendar(self):
        pass

        