from tkinter import Tk, messagebox, IntVar, Checkbutton,Label, Button, Entry, ttk, RIGHT, LEFT, X, Y, BOTTOM, HORIZONTAL, TOP, END, BOTH, OptionMenu, StringVar, Event, Text, Scrollbar, ttk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from DateEntry import DateEntry
from HeureEntry import HeureEntry
from manip import export, add, empty, printEvent, getEvent, getEventOnDay, deleteOneEvent, insertOneEvent
from datetime import datetime
from functools import partial
import connexion
import logging
import os

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
        self.creeTabInsertion()
        self.creeTabExport()
        self.creeTabSuppression()
        self.creeTabOption()
        self.exitButton = Button(self.window, text = "Quitter l'application", command = self.window.destroy)
        
        self.tabs.pack(expand=1, fill='both')
        self.tabs.bind("<<NotebookTabChanged>>", self.resizeTab)
        self.exitButton.pack(expand=1, fill=X)
        self.window.mainloop()

    def changeAccount(self):
        logging.info("Changement de compte google")
        self.window.destroy()
        g = connexion.GoogleConnexion()

    def creeListeCalendrier(self):
        logging.info("Récupération de la liste des calendriers")
        variable = StringVar(self.window)

        listeCalendriers = self.service.calendarList().list().execute()
        self.nomEtIdCalendriers = dict()
        for c in listeCalendriers['items']:
            if c["accessRole"] in ["owner", "writer"]: # Il faut avoir les droits de lecteur ET d'écriture
                self.nomEtIdCalendriers[c['summary']] = c['id']
                logging.info("Ajout de: " + self.nomEtIdCalendriers[c['summary']] + " à la liste des calendriers")

        self.selectedName = listeCalendriers['items'][0]['summary']
        self.selectedID = listeCalendriers['items'][0]['id']
        variable.set(listeCalendriers['items'][0]['summary'])
        self.calendarsList = OptionMenu(self.window, variable, *(self.nomEtIdCalendriers.keys()), command = self.setSelectedID)

        self.calendarsList.pack(expand=True, fill=X)

    def setSelectedID(self, val):
        logging.info("Calendrier choisi: " + val)
        self.selectedID = self.nomEtIdCalendriers[val]
        self.selectedName = val
        #print(val + ": " + self.selectedID)

    def creeTabSuppression(self):
        logging.info("Création de la tabulation de suppression")
        self.tabSuppr = ttk.Frame(self.tabs)

        # Date
        self.lineDateSuppr = ttk.Frame(self.tabSuppr)
        self.labelDateSuppr = Label(self.lineDateSuppr, text = "Date:")
        self.dateSuppr = DateEntry(self.lineDateSuppr)
        self.labelDateSuppr.pack(side=LEFT)
        self.dateSuppr.pack(side=LEFT)


        # Bouton
        self.btnShowEvent = Button(self.tabSuppr, text = "Afficher évènements", command = self.showEventSuppr)
        
        # Liste event
        self.eventList = ttk.Frame(self.tabSuppr)

        self.lineDateSuppr.pack()
        self.btnShowEvent.pack(expand=True, fill=X)
        self.eventList.pack()
        self.tabs.add(self.tabSuppr, text = "Suppression")

    def showEventSuppr(self):
        for children in self.eventList.winfo_children():
            children.destroy()

        date = self.dateSuppr.get()
        try:
            date = datetime(day=int(date[0]), month=int(date[1]), year=int(date[2]))
        except ValueError:
            logging.error("Date invalide, veuillez vérifier la date entrée")
            messagebox.showerror("Date invalide", "La date entrée n'est pas valide")
            return

        evt = getEventOnDay(self.service, self.selectedID, date)        
        for e in evt:
            line = ttk.Frame(self.eventList)
            Label(line, text = evt[e]["summary"] + " - " + evt[e]["heure"]).pack(side=LEFT, expand=True, fill=X)
            # Partiel empeche l'overwrite avec une lambda normal
            callback = partial(self.deleteSelectedEvent, e)
            Button(line, text = "X", command = callback).pack(side=LEFT)
            line.pack()

        self.tabs.event_generate("<<NotebookTabChanged>>")

    def deleteSelectedEvent(self, eID):
        deleteOneEvent(self.service, self.selectedID, eID)
        self.showEventSuppr()

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

    def emptyCalendar(self):
        messagebox.showinfo("Suppression des données", "La suppression va commencer après avoir appuyer sur 'Ok'")
        empty(self.service, self.selectedID)
        messagebox.showinfo("Suppression des données", "Les données ont été supprimées")

    def emptyLog(self):
        if(os.path.exists("log")):
            os.remove("log")

    def creeTabOption(self):
        logging.info("Création de la fiche des options")
        self.tabOption = ttk.Frame(self.tabs)

        self.btnEmptyCalendar = Button(self.tabOption, text = "Vider calendrier", command = self.emptyCalendar)
        self.btnEmptyLog = Button(self.tabOption, text = "Vider le fichier de log", command = self.emptyLog)
        self.btnChangeAccount = Button(self.tabOption, text = "Changement de compte", command = self.changeAccount)

        self.btnEmptyCalendar.pack(expand = True, fill = X)
        self.btnEmptyLog.pack(expand = True, fill = X)
        self.btnChangeAccount.pack(expand = True, fill = X)
        self.tabs.add(self.tabOption, text = "Options")

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

    def creeTabInsertion(self):
        logging.info("Création de la fiche d'insertion d'un évènement")
        self.tabInsert = ttk.Frame(self.tabs)



        self.lineDateDebutInsert = ttk.Frame(self.tabInsert)
        self.dateDebutInsert = Label(self.lineDateDebutInsert, text = "Date début")
        self.dateDebutInsertEntry = DateEntry(self.lineDateDebutInsert)
        self.heureDebutInsert = Label(self.lineDateDebutInsert, text = "Heure début")
        self.heureDebutInsertEntry = HeureEntry(self.lineDateDebutInsert)
        self.dateDebutInsert.pack(side=LEFT)
        self.dateDebutInsertEntry.pack(side=LEFT)
        self.heureDebutInsert.pack(side=LEFT)
        self.heureDebutInsertEntry.pack(side=LEFT)

        self.lineDateFinInsert = ttk.Frame(self.tabInsert)
        self.dateFinInsert = Label(self.lineDateFinInsert, text = "Date fin")
        self.dateFinInsertEntry = DateEntry(self.lineDateFinInsert)
        self.heureFinInsert = Label(self.lineDateFinInsert, text = "Heure fin")
        self.heureFinInsertEntry = HeureEntry(self.lineDateFinInsert)
        self.dateFinInsert.pack(side=LEFT)
        self.dateFinInsertEntry.pack(side=LEFT)
        self.heureFinInsert.pack(side=LEFT)
        self.heureFinInsertEntry.pack(side=LEFT)

        self.lineCheck = ttk.Frame(self.tabInsert)
        self.varCheckInsert = IntVar()
        self.checkFullDay = Checkbutton(self.lineCheck, text='Full Day',variable=self.varCheckInsert, onvalue=1, offvalue=0, command=self.onFullDay)
        self.checkFullDay.pack()

        self.summaryInsert = ttk.Frame(self.tabInsert)
        self.summaryInsertLabel = Label(self.summaryInsert, text = "Résumé")
        self.summaryInsertEntry = Entry(self.summaryInsert)
        self.summaryInsertLabel.pack(side=LEFT)
        self.summaryInsertEntry.pack(side=LEFT)
        

        self.descriptionInsert = ttk.Frame(self.tabInsert)
        self.descriptionInsertLabel = Label(self.descriptionInsert, text = "Description")
        self.descriptionInsertEntry = Entry(self.descriptionInsert)
        self.descriptionInsertLabel.pack(side=LEFT)
        self.descriptionInsertEntry.pack(side=LEFT)

        self.locationInsert = ttk.Frame(self.tabInsert)
        self.locationInsertLabel = Label(self.locationInsert, text = "Location")
        self.locationInsertEntry = Entry(self.locationInsert)
        self.locationInsertLabel.pack(side=LEFT)
        self.locationInsertEntry.pack(side=LEFT)

        self.buttonInsert = Button(self.tabInsert, text = "Insérez", command = self.onInsertEvent)

        self.lineDateDebutInsert.pack()
        self.lineDateFinInsert.pack()
        self.lineCheck.pack()
        self.summaryInsert.pack()
        self.descriptionInsert.pack()
        self.locationInsert.pack()
        self.buttonInsert.pack(expand=True, fill=X)
        self.tabs.add(self.tabInsert, text="Insertion")


    def onFullDay(self):
        if (self.varCheckInsert.get() == 1):
            self.heureDebutInsertEntry.disable()
            self.heureFinInsertEntry.disable()
        else:
            self.heureDebutInsertEntry.enable()
            self.heureFinInsertEntry.enable()
        
    def onInsertEvent(self):
        dateMin = self.dateDebutInsertEntry.get()
        dateMax = self.dateFinInsertEntry.get()
        
        HeureMin = self.heureDebutInsertEntry.get()
        HeureMax = self.heureFinInsertEntry.get()

        summ = self.summaryInsertEntry.get()
        des = self.descriptionInsertEntry.get()
        loca = self.locationInsertEntry.get()

        if (self.varCheckInsert.get() == 1):
            try:
                dateD = datetime(day=int(dateMin[0]), month=int(dateMin[1]), year=int(dateMin[2]))
                dateF = datetime(day=int(dateMax[0]), month=int(dateMax[1]), year=int(dateMax[2]))
            except ValueError:
                logging.error("Date invalide, veuillez vérifier les date entrée")
                messagebox.showerror("Date invalide", "Les date entrée ne sont pas valide")
                return
        else:
            try:
                dateD = datetime(day=int(dateMin[0]), month=int(dateMin[1]), year=int(dateMin[2]), hour=int(HeureMin[0]), minute=int(HeureMin[1]))
                dateF = datetime(day=int(dateMax[0]), month=int(dateMax[1]), year=int(dateMax[2]), hour=int(HeureMax[0]), minute=int(HeureMax[1]))
            except ValueError:
                logging.error("Date invalide, veuillez vérifier les date entrée")
                messagebox.showerror("Date invalide", "Les date entrée ne sont pas valide")
                return

        

        if(any(d == '' for d in dateMin) or any(d == '' for d in dateMax) or (self.varCheckInsert.get() == 0 and  (any(d == '' for d in HeureMin) or any(d == '' for d in HeureMax)))):
            messagebox.showerror(title="Insertion", message="Veuillez remplir les horraires")
        else:
            if insertOneEvent(self.service, self.selectedID, (self.varCheckInsert.get() == 1), dateMin, HeureMin, dateMax, HeureMax, summ, des, loca):
                messagebox.showinfo(title="Insertion", message="L'évènement a été inséré")
            else:
                messagebox.showerror(title="Insertion", message="Une erreur est survenu. Visitez les logs")

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
        logging.info("Création de la fenetre de visualisation")
        root = Tk()
        root.title("Événements")
        scrollbar = Scrollbar(root)
        scrollbar.pack( side = RIGHT, fill = Y )
        visu = printEvent(self.entryICSFile_Add.get())
        listEv = visu['list']
        text = Text(root, yscrollcommand = scrollbar.set )
        for line in listEv:
            text.insert(END, line)

        text.pack( side = LEFT, fill = BOTH )
        scrollbar.config( command = text.yview )

        if visu["successful"]:
            messagebox.showinfo(title="Visualisation", message=visu["message"])
        else:
            messagebox.showerror(title="Visualisation", message=visu["message"])

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
        messagebox.showinfo(title="Exportation", message="Exportation terminé")
