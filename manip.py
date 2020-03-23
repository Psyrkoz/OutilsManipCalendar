from connexion import GoogleConnexion
import datetime

def export(service, calendarID, filename, dateMin = None, dateMax = None):
    events_result = service.events().list(calendarId=calendarID, timeMin=dateMin, timeMax=dateMax).execute()["items"]

    for e in events_result:
        name = e["summary"]
        dateStart = e["start"]["date"]
        dateEnd = e["end"]["date"]
        print("Nom: " + name)
        print("Date depart: " + dateStart)
        print("Date fin: " + dateEnd)
        print("---------------------")