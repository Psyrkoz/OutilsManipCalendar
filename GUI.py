from tkinter import Tk, messagebox, Label, Button, Entry, ttk, RIGHT, LEFT, X, Y, BOTTOM, HORIZONTAL, TOP, END, BOTH, OptionMenu, StringVar, Event, Text, Scrollbar, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from DateEntry import DateEntry
from manip import export, add, printEvent, getEvent
import connexion
import logging

class GUI:
    def __init__(self, service):
        self.service = service
        self.createGUIApplication()
    
    def resizeTab(self, event):
        event.widget.update_idletasks()
        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())

    def createGUIApplication(self):
        logging.info("Création de la fenêtre graphique principale")
        # Cree la fenêtre
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Outils Manipulation calendrier Google")

        self.creeListeCalendrier()
        self.tabs = ttk.Notebook(self.window)
        self.creeTabView()
        self.creeTabAjout()
        self.creeTabExport()
        self.disconnectButton = Button(self.window, text = "Déconnexion", command = self.disconnect)
        self.exitButton = Button(self.window, text = "Quitter l'application", command = self.window.destroy)
        
        self.tabs.pack(expand=1, fill='both')
        self.tabs.bind("<<NotebookTabChanged>>", self.resizeTab)
        self.disconnectButton.pack(expand=1, fill=X)
        self.exitButton.pack(expand=1, fill=X)
        self.window.mainloop()

    def disconnect(self):
        logging.info("Déconnexion du compte google")
        self.window.destroy()
        connexion.GoogleConnexion.deleteToken()
        g = connexion.GoogleConnexion()

    def creeListeCalendrier(self):
        logging.info("Récupération de la liste des calendriers")
        variable = StringVar(self.window)

        listeCalendriers = self.service.calendarList().list().execute()
        self.nomEtIdCalendriers = dict()
        for c in listeCalendriers['items']:
            #if c['summary'] not in ['Contacts', 'Jours fériés en France', 'Week Numbers']:
            self.nomEtIdCalendriers[c['summary']] = c['id']
            logging.info("Ajout de: " + self.nomEtIdCalendriers[c['summary']] + " à la liste des calendriers")

        self.calendarsList = OptionMenu(self.window, variable, *(self.nomEtIdCalendriers.keys()), command = self.setSelectedID)

        self.calendarsList.pack(expand=True, fill=X)

    def setSelectedID(self, val):
        logging.info("Calendrier choisi: " + val)
        self.selectedID = self.nomEtIdCalendriers[val]
        self.selectedName = val
        #print(val + ": " + self.selectedID)

    def creeTabExport(self):
        logging.info("Création de la fiche d'exportation")
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
        self.buttonExport = Button(self.tabExport, text = "Exporter données", command = self.exportData)

        # Fichier
        self.lineFile = ttk.Frame(self.tabExport)
        self.filenameExportLabel = Label(self.lineFile, text = "Nom du fichier")
        self.filenameExport = Entry(self.lineFile)
        self.selectFilenameAndFolderButton = Button(self.lineFile, text = "...", command = self.selectSaveFolderAndName)
        self.filenameExportLabel.pack(side=LEFT)
        self.filenameExport.pack(expand=True, fill=X, side=LEFT)
        self.selectFilenameAndFolderButton.pack(side=LEFT)

        self.lineDate.pack()
        self.lineFile.pack(expand=True, fill=X)
        self.buttonExport.pack(expand=True, fill=X)  
        self.tabs.add(self.tabExport, text="Exportation")
        
    def selectSaveFolderAndName(self):
        filename = asksaveasfilename(title="Selectionner un fichier ICS", filetypes=(("iCalendar File", "*.ics"), ("All Files", "*.*")))
        self.filenameExport.delete(0, END)
        logging.info("Nom du fichier ICS pour l'exportation: " + filename)
        self.filenameExport.insert(0, filename)

    def creeTabAjout(self):
        logging.info("Création de la fiche d'ajout de fichier ICS")
        self.tabAdd = ttk.Frame(self.tabs)

        self.entryLine = ttk.Frame(self.tabAdd)
        self.labelAskICSFile_Add = Label(self.entryLine, text="Fichier .ics a ajouter dans le calendrier:")
        self.entryICSFile_Add = Entry(self.entryLine)
        self.buttonAskICSFile_Add = Button(self.entryLine, text = "...", command = self.askForICSFile)
        self.buttonEventInFile = Button(self.tabAdd, text = "Visualiser", state = "disabled", command = self.openEvent)
        self.buttonAjouter = Button(self.tabAdd, text = "Ajouter", command = self.addICSFileToCalendar)
        self.labelAskICSFile_Add.pack(side=LEFT)
        self.entryICSFile_Add.pack(expand=True, fill=X, side=LEFT)
        self.buttonAskICSFile_Add.pack(side=LEFT)
        
        self.entryLine.pack()
        self.buttonEventInFile.pack(expand=True, fill=X)
        self.buttonAjouter.pack(expand=True, fill=X)
        self.tabs.add(self.tabAdd, text="Ajout")

    def creeTabView(self):
        logging.info("Création de la fiche de visualisation des évènements")
        self.tabView = ttk.Frame(self.tabs)

        self.lineDateView = ttk.Frame(self.tabView)
        self.dateDebutView = Label(self.lineDateView, text = "Date début")
        self.dateDebutViewEntry = DateEntry(self.lineDateView)
        self.dateFinView = Label(self.lineDateView, text = "Date fin")
        self.dateFinViewEntry = DateEntry(self.lineDateView)
        self.dateDebutView.pack(side=LEFT)
        self.dateDebutViewEntry.pack(side=LEFT)
        self.dateFinView.pack(side=LEFT)
        self.dateFinViewEntry.pack(side=LEFT)

        self.buttonVisualiser = Button(self.tabView, text = "Visualiser", command = self.visualiserEvent)

        self.lineDateView.pack()
        self.buttonVisualiser.pack(expand=True, fill=X)
        self.tabs.add(self.tabView, text="Visualisation")


    def visualiserEvent(self):
        dateMin = self.dateDebutViewEntry.get()
        dateMax = self.dateFinViewEntry.get()

        if(any(d == '' for d in dateMin) or any(d == '' for d in dateMax)):
            pass
        
        root = Tk()
        root.title("Événements")
        scrollbar = Scrollbar(root)
        scrollbar.pack( side = RIGHT, fill = Y )
        listEv = getEvent(self.service, self.selectedID, dateMin, dateMax)
        text = Text(root, yscrollcommand = scrollbar.set )
        for line in listEv:
            text.insert(END, line)

        text.pack( side = LEFT, fill = BOTH )
        scrollbar.config( command = text.yview )
        self.tabs.event_generate("<<NotebookTabChanged>>")
        

    def askForICSFile(self):
        logging.info("Demande de fichier ICS a importer")
        filename = askopenfilename(title="Selectionner un fichier ICS", filetypes=(("iCalendar File", "*.ics"), ("All Files", "*.*")))
        logging.info("Lien du fichier a importer:" + filename)
        self.entryICSFile_Add.delete(0, END)
        self.entryICSFile_Add.insert(0, filename)
        self.buttonEventInFile['state'] = "normal"
        self.tabs.event_generate("<<NotebookTabChanged>>") # Génère un event pour redimensionner la tab -> voir fonction resizeTab

    def openEvent(self):
        root = Tk()
        root.title("Événements")
        scrollbar = Scrollbar(root)
        scrollbar.pack( side = RIGHT, fill = Y )
        listEv = printEvent(self.entryICSFile_Add.get())
        text = Text(root, yscrollcommand = scrollbar.set )
        for line in listEv:
            text.insert(END, line)

        text.pack( side = LEFT, fill = BOTH )
        scrollbar.config( command = text.yview )

    def addICSFileToCalendar(self):
        logging.info("Ajout du fichier ICS '" + self.entryICSFile_Add.get() + "' au calendrier: '" + self.selectedID + "'")
        self.buttonAjouter['state'] = "disabled"
        importation = add(self.service, self.selectedID, self.entryICSFile_Add.get())
        self.buttonAjouter['state'] = "normal"
        if importation["successful"]:
            messagebox.showinfo(title="Importation", message=importation["message"])
        else:
            messagebox.showerror(title="Importation", message=importation["message"])

    def exportData(self):
        logging.info("Exportation des données dans le fichier: " + self.filenameExport.get())
        dateMinArray = self.dateDebutEntry.get()
        dateMaxArray = self.dateFinEntry.get()

        dateMin = None
        if(dateMinArray[0] != '' and dateMinArray[1] != '' and dateMinArray[2] != ''): 
            dateMin = "-".join(dateMinArray[::-1]) + "T00:00:00.000000Z" # Passe d'une date tableau JJ MM YYYY a une date string YYYY-MM-JJ (avec en plus T00:00:00.000000Z <- Z pour UTC)
        
        dateMax = None
        if(dateMaxArray[0] != '' and dateMaxArray[1] != '' and dateMaxArray[2] != ''): 
            dateMax = "-".join(dateMaxArray[::-1]) + "T00:00:00.000000Z" # Passe d'une date tableau JJ MM YYYY a une date string YYYY-MM-JJ (avec en plus T00:00:00.000000Z <- Z pour UTC)

        export(self.service, self.selectedName,self.selectedID, self.filenameExport.get(), dateMin=dateMin, dateMax=dateMax)