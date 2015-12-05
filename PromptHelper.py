import datetime
from pCalendar.UserCal import CalEvent

def addEventParsing(client, test=False):
    if test is False:
        addWelcome = 'Okay! You\'re going to add an event\n'
        # getMonth = 'What month? (mm)\n'
        getDay = 'What Day? (dd)\n'
        # getYear = 'What Year? (yyyy)\n'

        getStartTime = 'What is the start time? (24h hhmm)\n'
        getEndTime = 'What is the end time? (24h hhmm)\n'

        getName = 'What is the name of this event?\n'

        getNumParticipants = 'How many participants? (int)\n'


        print (addWelcome)

        # month = int(input(getMonth))
        day = int(input(getDay))
        # year = int(input(getYear))

        month = 11
        # day = 16
        year = 1990

        startTime = input(getStartTime)
        endTime = input(getEndTime)

        startDateTime = datetime.datetime(year,month,day, hour = int(startTime[:2]), minute = int(startTime[2:4]))

        endDateTime = datetime.datetime(year,month,day, hour = int(endTime[:2]), minute = int(endTime[2:4]))


        eventName = input(getName)

        numParticipants = int(input(getNumParticipants))

        participants = []
        for i in range(0,numParticipants):
            singlePart = input('Enter participant %i ID.\n'%(i+1))
            participants.append(int(singlePart))


            # print (participants)
        newEvent = CalEvent(eventName, startDateTime, endDateTime, participants= participants,uid=client.uID)
    else:
        newEvent = CalEvent("TEST EVENT", datetime.datetime(2100,10,4,12,44),datetime.datetime(2100,11,4,12,44),
                                  participants=[0,1],uid=client.uID)

    return newEvent #Return calendar event

def deleteEventParsing(theCalendar):
    deleteWelcome = 'Okay! You\'re going to delete an event\n'

    print('This calendar has the following events in it:\n')

    numEvents = len(theCalendar.cal)

    for i in range(0,numEvents):
        print('\t%i. '%(i) + str(theCalendar.cal[i]))

    choice = int(input('Which event do you want to delete? (number)'))

    return theCalendar.cal[choice] #return the selected event to delete