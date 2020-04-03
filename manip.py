from connexion import GoogleConnexion
from collections import defaultdict
import re
import datetime
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC # timezone

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
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        date = date - datetime.timedelta(hours=int(dateOffset[0]), minutes=int(dateOffset[1]))
        date = removeAllUselessChar(date.isoformat()) + "Z"
    else:
        dateOffset = re.findall('-(\d{2}):(\d{2})', date, re.M | re.I)[0]
        if(dateOffset):
            dateOffset = dateOffset[0]
            minusPositionStart = date.find("-")
            date = date[:minusPositionStart]
            date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            date = date + datetime.timedelta(hours=int(dateOffset[0]), minutes=int(dateOffset[1]))
            date = removeAllUselessChar(date.isoformat()) + "Z"

    return date

def export(service, calendarName, calendarID, filename, dateMin = None, dateMax = None):
    events_result = service.events().list(calendarId=calendarID, timeMin=dateMin, timeMax=dateMax).execute()["items"]
    textFile = "BEGIN:VCALENDAR\nPRODID:-//Google Inc//Google Calendar 70.9054//EN\nVERSION:2.0\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nX-WR-CALNAME:" + calendarName + "\nX-WR-TIMEZONE:Europe/Paris\n"
    now = removeMilliseconds(datetime.datetime.utcnow().isoformat() + 'Z').replace(':', '').replace('-', '')
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
    with open(filename, "w") as file:
        file.write(textFile)

def import(service, calendarID, filename):
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
            event['start']={'dateTime':str(component.get('dtstart').dt)}
            event['end']={'dateTime':str(component.get('dtend').dt)}
            if component.get('attendee') is not None:
                event['attendees']=[]
                if isinstance(component.get('attendee'), list):
                    for a in component.get('attendee'):
                        event['attendees'].append({'email':str(a).split(":")[1]})
                else:
                    event['attendees'].append({'email':str(component.get('attendee')).split(":")[1]})
            event = service.events().insert(calendarId=calendarID, body=event).execute()
    g.close()