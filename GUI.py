from tkinter import Tk, Label, Button, Entry, ttk, LEFT, X, BOTTOM, TOP, END, OptionMenu, StringVar, Event
from tkinter.filedialog import askopenfilename, asksaveasfilename
from DateEntry import DateEntry
from manip import export, add, printEvent, getEvent

class GUI:
    def __init__(self, service):
        self.service = service
        self.createGUIApplication()
    
    def resizeTab(self, event):
        event.widget.update_idletasks()
        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())

    def createGUIApplication(self):
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
        
        self.tabs.pack(expand=1, fill='both')
        self.tabs.bind("<<NotebookTabChanged>>", self.resizeTab)
        self.disconnectButton.pack(expand=1, fill=X)
        self.window.mainloop()

    def disconnect(self):
        pass

    def creeListeCalendrier(self):
        variable = StringVar(self.window)

        listeCalendriers = self.service.calendarList().list().execute()
        self.nomEtIdCalendriers = dict()
        for c in listeCalendriers['items']:
            #if c['summary'] not in ['Contacts', 'Jours fériés en France', 'Week Numbers']:
            self.nomEtIdCalendriers[c['summary']] = c['id']

        self.calendarsList = OptionMenu(self.window, variable, *(self.nomEtIdCalendriers.keys()), command = self.setSelectedID)

        self.calendarsList.pack(expand=True, fill=X)

    def setSelectedID(self, val):
        self.selectedID = self.nomEtIdCalendriers[val]
        self.selectedName = val
        print(val + ": " + self.selectedID)

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
        self.filenameExport.insert(0, filename)

    def creeTabAjout(self):
        self.tabAdd = ttk.Frame(self.tabs)

        self.entryLine = ttk.Frame(self.tabAdd)
        self.labelAskICSFile_Add = Label(self.entryLine, text="Fichier .ics a ajouter dans le calendrier:")
        self.entryICSFile_Add = Entry(self.entryLine)
        self.buttonAskICSFile_Add = Button(self.entryLine, text = "...", command = self.askForICSFile)
        self.labelEventInFile = Label(self.tabAdd, text="", justify=LEFT)
        self.buttonAjouter = Button(self.tabAdd, text = "Ajouter", command = self.addICSFileToCalendar)

        self.labelAskICSFile_Add.pack(side=LEFT)
        self.entryICSFile_Add.pack(expand=True, fill=X, side=LEFT)
        self.buttonAskICSFile_Add.pack(side=LEFT)
        
        self.entryLine.pack()
        self.labelEventInFile.pack()
        self.buttonAjouter.pack(expand=True, fill=X)
        self.tabs.add(self.tabAdd, text="Ajout")

    def creeTabView(self):
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
        self.eventViewLabel = Label(self.tabView, text="", justify=LEFT)

        self.lineDateView.pack()
        self.buttonVisualiser.pack(expand=True, fill=X)
        self.eventViewLabel.pack()
        self.tabs.add(self.tabView, text="Visualisation")


    def visualiserEvent(self):
        dateMin = self.dateDebutViewEntry.get()
        dateMax = self.dateFinViewEntry.get()

        if(any(d == '' for d in dateMin) or any(d == '' for d in dateMax)):
            pass
        
        self.eventViewLabel['text'] = getEvent(self.service, self.selectedID, dateMin, dateMax)
        self.tabs.event_generate("<<NotebookTabChanged>>")
        

    def askForICSFile(self):
        filename = askopenfilename(title="Selectionner un fichier ICS", filetypes=(("iCalendar File", "*.ics"), ("All Files", "*.*")))
        self.entryICSFile_Add.delete(0, END)
        self.entryICSFile_Add.insert(0, filename)
        self.labelEventInFile['text']=printEvent(filename)
        self.tabs.event_generate("<<NotebookTabChanged>>") # Génère un event pour redimensionner la tab -> voir fonction resizeTab

    def addICSFileToCalendar(self):
        pass

    def exportData(self):
        dateMinArray = self.dateDebutEntry.get()
        dateMaxArray = self.dateFinEntry.get()

        dateMin = None
        if(dateMinArray[0] != '' and dateMinArray[1] != '' and dateMinArray[2] != ''): 
            dateMin = "-".join(dateMinArray[::-1]) + "T00:00:00.000000Z" # Passe d'une date tableau JJ MM YYYY a une date string YYYY-MM-JJ (avec en plus T00:00:00.000000Z <- Z pour UTC)
        
        dateMax = None
        if(dateMaxArray[0] != '' and dateMaxArray[1] != '' and dateMaxArray[2] != ''): 
            dateMax = "-".join(dateMaxArray[::-1]) + "T00:00:00.000000Z" # Passe d'une date tableau JJ MM YYYY a une date string YYYY-MM-JJ (avec en plus T00:00:00.000000Z <- Z pour UTC)

        export(self.service, self.selectedName,self.selectedID, self.filenameExport.get(), dateMin=dateMin, dateMax=dateMax)