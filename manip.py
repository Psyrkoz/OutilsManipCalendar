from collections import defaultdict
import re
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from pytz import UTC # timezone
import logging

def removeMilliseconds(date):
    return re.sub("(\.\d{3,})", repl="", string=date)

def removeAllUselessChar(date):
    return date.replace('-', '').replace(':', '')

def convertOffsetTimeToUTCGoogleFormat(date):
    dateOffset = re.findall('\+(\d{2}):(\d{2})', date, re.M | re.I)
    if(dateOffset):
        dateOffset = dateOffset[0]
        plusPositionStart = date.find("+")
        date = date[:plusPositionStart]
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        date = date - timedelta(hours=int(dateOffset[0]), minutes=int(dateOffset[1]))
        date = removeAllUselessChar(date.isoformat()) + "Z"
    else:
        dateOffset = re.findall('-(\d{2}):(\d{2})', date, re.M | re.I)[0]
        if(dateOffset):
            dateOffset = dateOffset[0]
            minusPositionStart = date.find("-")
            date = date[:minusPositionStart]
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            date = date + timedelta(hours=int(dateOffset[0]), minutes=int(dateOffset[1]))
            date = removeAllUselessChar(date.isoformat()) + "Z"

    return date

def export(service, calendarName, calendarID, filename, dateMin = None, dateMax = None):
    events_result = service.events().list(calendarId=calendarID, timeMin=dateMin, timeMax=dateMax).execute()["items"]
    textFile = "BEGIN:VCALENDAR\nPRODID:-//Google Inc//Google Calendar 70.9054//EN\nVERSION:2.0\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nX-WR-CALNAME:" + calendarName + "\nX-WR-TIMEZONE:Europe/Paris\n"
    now = removeMilliseconds(datetime.utcnow().isoformat() + 'Z').replace(':', '').replace('-', '')
    templateDateTimeEvent = "BEGIN:VEVENT\nDTSTART:{0[start][dateTime]}\nDTEND:{0[end][dateTime]}\nDTSTAMP:" + now + "\nUID:{0[iCalUID]}\nCREATED:{0[created]}\nDESCRIPTION:{0[description]}\nLAST-MODIFIED:{0[updated]}\nLOCATION:{0[location]}\nSEQUENCE:{0[sequence]}\nSTATUS:{0[status]}\nSUMMARY:{0[summary]}\nTRANSP:OPAQUE\nEND:VEVENT\n"
    templateFullDayEvent =  "BEGIN:VEVENT\nDTSTART;VALUE=DATE:{0[start][date]}\nDTEND;VALUE=DATE:{0[end][date]}\nDTSTAMP:" + now + "\nUID:{0[iCalUID]}\nCREATED:{0[created]}\nDESCRIPTION:{0[description]}\nLAST-MODIFIED:{0[updated]}\nLOCATION:{0[location]}\nSEQUENCE:{0[sequence]}\nSTATUS:{0[status]}\nSUMMARY:{0[summary]}\nTRANSP:OPAQUE\nEND:VEVENT\n"
    for e in events_result:
        # On cree un nouveau dictionnaire basé sur une str factory pour mettre des chaine vide si la cle existe pas
        data = defaultdict(str)
        for key in e:
            data[key] = e[key]
        
        data["created"] = removeAllUselessChar(removeMilliseconds(data["created"])) # On change le format des dates pour qu'il soit accepté par Google plus tard
        data["updated"] = removeAllUselessChar(removeMilliseconds(data["updated"]))
        # Si l'event est sur toute la journee, c'est "templateFullDayEvent qu'on utilise"
        if "date" in e["start"]:
            data["start"]["date"] = removeAllUselessChar(data["start"]["date"])
            data["end"]["date"] = removeAllUselessChar(data["end"]["date"])
            textFile += templateFullDayEvent.format(data)
        # Si il est sur une période on utilise "templateDateTimeEvent"
        else:
            data["start"]["dateTime"] = convertOffsetTimeToUTCGoogleFormat(e["start"]["dateTime"])
            data["end"]["dateTime"] = convertOffsetTimeToUTCGoogleFormat(e["end"]["dateTime"])
            textFile += templateDateTimeEvent.format(data)
    textFile += "END:VCALENDAR"

    logging.info("Ajout des événements:\n" + textFile)
    with open(filename, "w") as file:
        file.write(textFile)

def printEvent(filename):
    try:
        g = open(filename,'rb')
        gcal = Calendar.from_ical(g.read())
        listEv=[]
        i=0
        for component in gcal.walk():
            if component.name == "VEVENT":
                text=""
                i+=1
                text+="\nEvènement n°" + str(i) + " :\n"
                text+="\tRésumé : " + str(component.get('summary'))+"\n"
                if len(str(component.get('dtstart').dt.isoformat())) == 10:
                    j = (component.get('dtend').dt - component.get('dtstart').dt).days
                    text+="\tDurée : " + str(j) + " j\n"
                    text+="\tDébut : " + component.get('dtstart').dt.strftime("%d/%m/%Y")+"\n"
                    if j > 1:
                        text+="\tFin : " + component.get('dtend').dt.strftime("%d/%m/%Y")+"\n"
                else:
                    text+="\tDurée : " + deltaBetweenDate(component.get('dtstart').dt.isoformat("T"),component.get('dtend').dt.isoformat("T"))+"\n"
                    text+="\tDébut : " + component.get('dtstart').dt.strftime("%d/%m/%Y, %H:%M")+"\n"
                    text+="\tFin : " + component.get('dtend').dt.strftime("%d/%m/%Y, %H:%M")+"\n"
                listEv.append(text)
        g.close()
        return listEv
    except FileNotFoundError:
        logging.error("Impossible d'ouvrir le fichier " + filename)
        return ""

def add(service, calendarID, filename):
    try:    
        g = open(filename,'rb')
        gcal = Calendar.from_ical(g.read())
        for component in gcal.walk():
            event={}
            if component.name == "VEVENT":
                if component.get('summary') is not None:
                    event['summary']=str(component.get('summary'))
                if component.get('location') is not None:
                    event['location']=str(component.get('location'))
                if component.get('description') is not None:
                    event['description']=str(component.get('description'))
                if len(str(component.get('dtstart').dt.isoformat())) == 10:
                    event['start']={'date':str(component.get('dtstart').dt.isoformat())}
                    event['end']={'date':str(component.get('dtend').dt.isoformat())}
                else:
                    event['start']={'dateTime':str(component.get('dtstart').dt.isoformat())}
                    event['end']={'dateTime':str(component.get('dtend').dt.isoformat())}
                if component.get('attendee') is not None:
                    event['attendees']=[]
                    if isinstance(component.get('attendee'), list):
                        for a in component.get('attendee'):
                            event['attendees'].append({'email':str(a).split(":")[1]})
                    else:
                        event['attendees'].append({'email':str(component.get('attendee')).split(":")[1]})
                event = service.events().insert(calendarId=calendarID, body=event).execute()
        g.close()
    except FileNotFoundError:
        logging.error("Impossible d'ouvrir le fichier " + filename)

# date supposed YYYY-MM-DD; return DD/MM/YYYY
def formatDate(date):
    return "/".join(date.split('-')[::-1])

# date supposed "YYYY-MM-DDTHH:MM:SS+XX:XX"; return DD/MM/YYYY a HH:MM:SS
def formatDateWithHour(date):
    dateSplit = date.split('T')
    date = formatDate(dateSplit[0])
    time = dateSplit[1].split('+')[0]
    time = time.split(":")
    return date + ", " + time[0] + ":" + time[1]

# dateStart et dateEnd dans ce format: "YYYY-MM-DDTHH:MM:SS+XX:XX"
def deltaBetweenDate(dateStart, dateEnd):
    dateStartArray = dateStart.split("T")[0].split("-")[::-1]
    timeStartArray = dateStart.split("T")[1].split("+")[0].split(":")
    dateEndArray = dateEnd.split("T")[0].split("-")[::-1]
    timeEndArray = dateEnd.split("T")[1].split("+")[0].split(":")
    ds = datetime(day=int(dateStartArray[0]), month=int(dateStartArray[1]), year=int(dateStartArray[2]), hour=int(timeStartArray[0]), minute=int(timeStartArray[1]), second=int(timeStartArray[2]))
    de = datetime(day=int(dateEndArray[0]), month=int(dateEndArray[1]), year=int(dateEndArray[2]), hour=int(timeEndArray[0]), minute=int(timeEndArray[1]), second=int(timeEndArray[2]))

    delta = de - ds
    delta = str(delta).split(":")
    engD = delta[0] + "h " + delta[1] + "m " + delta[2] + "s"
    delta = re.split("day,|days,",engD)
    if len(delta) > 1:
        return delta[0] + "j," + delta[1]
    else:
        return delta[0]

# dateMin: [JJ/MM/YYYY] & dateMax: [JJ/MM/YYYY]
def getEvent(service, calendarID, dateMin = None, dateMax = None):
    dateStart = None
    dateEnd = None

    if(dateMin is not None and dateMin[0] != '' and dateMin[1] != '' and dateMin[2] != ''):
        try:
            dateStart = datetime(day=int(dateMin[0]), month=int(dateMin[1]), year=int(dateMin[2]))
            dateStart = dateStart.isoformat() + "Z"
        except ValueError:
            logging.error("Date invalide, veuillez vérifier la date entrée")
    else:
        logging.warning("Date début non / mal rempli, aucune date de début ne sera prise en compte")

    if(dateMax is not None and dateMax[0] != '' and dateMax[1] != '' and dateMax[2] != ''):
        try:
            dateEnd = datetime(day=int(dateMax[0]), month=int(dateMax[1]), year=int(dateMax[2]))
            dateEnd = dateEnd.isoformat() + "Z"
        except ValueError:
            logging.error("Date invalide, veuillez vérifier la date entrée")
    else:
        logging.warning("Date de fin non / mal rempli, aucune date de fin ne sera prise en compte")

    events_result = service.events().list(calendarId=calendarID, timeMin=dateStart,
                                            timeMax=dateEnd, singleEvents=True,
                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    listEv=[]
    i = 0
    for event in events:
        text = ""
        i+=1
        # Met le résumé (si disponible) dans le texte:
        text+="\nEvènement n°" + str(i) + " :\n"
        text +="\tRésumé: "
        text += event['summary'] + "\n" if "summary" in event else "Aucun résumé disponible\n"

        # Si l'événement est sur une période donnée
        if "dateTime" in event['start']:
            dateDebut = formatDateWithHour(event['start']['dateTime'])
            dateFin = formatDateWithHour(event['end']['dateTime'])
            duree = deltaBetweenDate(event['start']['dateTime'], event['end']['dateTime'])
            text+="\tDurée : " + duree +"\n"
            text+="\tDébut : " + dateDebut + "\n"
            text+="\tFin : " + dateFin +"\n"
        # Sinon, l'évènement est sur toute la journée (clé différentes)
        else:
            dateDebut = formatDate(event['start']['date'])
            dateFin = formatDate(event['end']['date'])
            dateStartArray = event['start']['date'].split("-")[::-1]
            dateEndArray = event['end']['date'].split("-")[::-1]
            ds = datetime(day=int(dateStartArray[0]), month=int(dateStartArray[1]), year=int(dateStartArray[2]))
            de = datetime(day=int(dateEndArray[0]), month=int(dateEndArray[1]), year=int(dateEndArray[2]))

            j = (de - ds).days
            text+="\tDurée : " + str(j) + " j\n"
            text+="\tDébut : " + dateDebut + "\n"
            if j > 1:
                    text+="\tFin : " + dateFin + "\n"
        listEv.append(text)
        
    return listEv

