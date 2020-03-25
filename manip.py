from connexion import GoogleConnexion
import datetime

def export(service, calendarName, calendarID, filename, dateMin = None, dateMax = None):
    events_result = service.events().list(calendarId=calendarID, timeMin=dateMin, timeMax=dateMax).execute()["items"]
    #print(events_result)
    print("--- TEXT ON ICS FILE ---")
    textFile = "BEGIN:VCALENDER\nPROVID:-//Google Inc//Google Calendar 70.9054//EN\nVERSION:2.0\nCALSCLAE:GREGORIAN\nMETHOD:PUBLISH\nX-WR-CALNAME:" + calendarName + "\nX-WR-TIMEZONE:Europe/Paris"
    print(textFile)
    print("--- TEXT ON ICS FILE ---")

    template = "BEGIN:VEVENT\nSUMMARY:{summary}\nDTSTART;TZID={location}:{dateTimeStart}\n"
    # for e in events_result:
    #    name = e["summary"]
    #    dateStart = e["start"]["dateTime"]
    #   dateEnd = e["end"]["dateTime"]
    #    print("Nom: " + name)
    #   print("Date depart: " + dateStart)
    #    print("Date fin: " + dateEnd)
    #    print("---------------------")