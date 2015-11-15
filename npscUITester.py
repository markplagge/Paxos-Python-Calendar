import datetime

import npyscreen, curses

import pCalendar

import urwid

class CurrentCalendar(pCalendar.UserCal.Calendar):
    def __init(self, *args, **keywords):
        super(CurrentCalendar, self).__init__(*args, **keywords)

    def canAddEle(self, uuid='', startDate=datetime.datetime.now(), endDate=datetime.datetime.now(), participants=[]):
        calevt = pCalendar.UserCal.CalEvent(uid=uuid, startDate=startDate, endDate=endDate,
                                        participants=participants)
        return self.canAdd(calevt)

    def canAdd(self, calevt):
        for event in self.cal:
            if (event.willEventConflict(calevt)):
                return False
        return True
    def addLt(self, calevt):
        self.cal.append(calevt)

    def delete_item(self, id):
        pass

    def list_all(self, ):
        items = [["No Events In Calendar"], [len(self.cal)]]
        if len(self.cal) > 0:
            items = []
            for c in self.cal:
                items.append(c.listFormat)

        return items





class newCalEvent(npyscreen.FormMultiPageAction):
    users = ["User 1", "User 2", "User 3"]



    def create(self):
        super(newCalEvent, self).create()
        self.evenTitle = self.add(npyscreen.TitleText, name='Name')
        self.invitedUsers = self.add(npyscreen.TitleMultiSelect, name='Participants', values=self.users)
        new_page = self.add_page()
        self.times = self.add(npyscreen.FixedText, name="Start Times", value="Choose Start")
        self.startDate = self.add(npyscreen.DateCombo, name="StartDate")
        self.startHour = self.add(npyscreen.TitleSlider, name="startH", label=True, out_of=24, step=1)
        self.startMinute = self.add(npyscreen.TitleSlider, name="startM", lable=True, out_of=60, step=1)


        self.time2 = self.add(npyscreen.FixedText, name="End Times", value="Choose Ending")
        self.endDate = self.add(npyscreen.DateCombo, name="StartDate")
        self.endHour = self.add(npyscreen.TitleSlider, name="startH", label=True, out_of=24, step=1)
        self.endMinute = self.add(npyscreen.TitleSlider, name="startM", lable=True, out_of=60, step=1)

    def afterEditing(self):
        self.parentApp.setNextForm("MAIN")
        try:

            dt= self.startDate.value

            minute =  int(self.startMinute.value)
            hour = int(self.startHour.value)
            tm = datetime.time(hour=hour, minute=minute)
            start = datetime.datetime.combine(dt,tm)

            minute = int(self.endMinute.value)
            hour = int(self.endHour.value)
            tm = datetime.time(hour=hour, minute = minute)
            dt = self.endDate.value
            end = datetime.datetime.combine(dt,tm)
            title = self.evenTitle.value
            parts = self.invitedUsers.value

            event = pCalendar.UserCal.CalEvent(title,start,end,x.myUID,participants=parts,owner=x.myUID)
            curCalEvent = event
            if(x.canAdd(curCalEvent)):
                npyscreen.notify_confirm("Event does not conflict with local calendar. Attempting add.",
                                         title="Good News Everyone")
                npyscreen.notify_confirm(str(x))
                #Do stuff with PAXOS
                #x.addEntry(curCalEvent)
                #x.addLt(curCalEvent)



                #self.parentApp.setNextForm("MAIN")
            else:
                npyscreen.notify_confirm("Event conflicts, can not add.", title="Sorry...")
                #self.parentApp.setNextForm("MAIN")
        except:
            npyscreen.notify_confirm("Sorry, calendar is invald.",title="error")
            #self.parentApp.setNextForm("MAIN")


        #self.parentApp.switchFormNow()
        #self.parentApp.setNextForm(displayCalendar)

class MyGrid(npyscreen.GridColTitles):
    # You need to override custom_print_cell to manipulate how
    # a cell is printed. In this example we change the color of the
    # text depending on the string value of cell.
    def custom_print_cell(self, actual_cell, cell_display_value):
        if cell_display_value =='FAIL':
           actual_cell.color = 'DANGER'
        elif cell_display_value == 'PASS':
           actual_cell.color = 'GOOD'
        else:
           actual_cell.color = 'DEFAULT'
class mainMenu(npyscreen.FormMultiPage):

    def create(self):
        super(mainMenu, self).create()
        #Show calendar here
        self.add(npyscreen.FixedText, value=x.__str__())

        self.option = ""
        self.addB = self.add(npyscreen.ButtonPress,name="Add",when_pressed_function=self.addItem)
        self.delB = self.add(npyscreen.ButtonPress,name="Delete ",when_pressed_function=self.delBp)
        self.endB = self.add(npyscreen.ButtonPress,name="end",when_pressed_function=self.endBp)

    def addItem(self):
        self.option = "add"
        self.editing = False
    def delBp(self):
        self.option = "del"
        self.editing = False
    def endBp(self):
        self.option = "end"
        self.editing = False

def createCal(myCal):
    F = newCalEvent(name="Add Event" )
    F.edit()
    dt= F.startDate.value

    minute =  int(F.startMinute.value)
    hour = int(F.startHour.value)
    tm = datetime.time(hour=hour, minute=minute)
    start = datetime.datetime.combine(dt,tm)

    minute = int(F.endMinute.value)
    hour = int(F.endHour.value)
    tm = datetime.time(hour=hour, minute = minute)
    dt = F.endDate.value
    end = datetime.datetime.combine(dt,tm)
    title = F.evenTitle.value
    parts = F.invitedUsers.value

    event = pCalendar.UserCal.CalEvent(title,start,end,myCal.myUID,participants=parts,owner=myCal.myUID)


    return event
    #ce = pCalendar.UserCal.CalEvent(eventName = F.evenTitle, startTS=datetime.datetime.now(), endTS=datetime.datetime.now(),
    #             uid=-1, uRank="Nope", participants=[],
    #             insertTime=datetime.datetime.now(), owner="Nobody"):)

## Main Menu Items:
choices = u'Add Delete'.split()
## Dirty dirty globals
x = CurrentCalendar()
curCalEvent = False

selected = None






def main(*args, **keywords):

    dtm = None
    uid = 102
    #createCal(x)
    opt = "go"
    g = mainMenu()
    while opt != "end":

        if g.option == "add":
            F = newCalEvent(name="Add Event", uid = 102 )
            dtm = createCal(x)
            x.addEntry(dtm)
            g = mainMenu()
        if g.option == "end":
            break
        if g.option =="del":
            mm = npyscreen.Form(name="Delete Event")
            mm.add(npyscreen.Textfield, name="Enter Event Number")
            mm.edit()
            g = mainMenu()
        g.edit()
        opt = g.option
        g.DISPLAY()

    #F.edit()
    m = npyscreen.Form()
    #
    #try:


        #if(x.canAdd(curCalEvent)):
        #    m.add(npyscreen.notify_confirm("Event created, no local conflicts detected"))
        #else:
        #    m.add(npyscreen.notify_confirm("Event created, but a local conflict was found"))
    #except:
    #    m.add(npyscreen.notify_confirm("Sorry, invalid calendar"))

    #finally:
    #    m.display()
    #print("Created event for user " + F.evenTitle.value)
    #print(dtm)
    #urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
    #return(dtm)
    #TA = MainApp()
    #TA.run(fork=False)
    #curCalEvent = pCalendar.UserCal.CalEvent()
    #x.addEntry(curCalEvent)


    #MF = newCalEvent(name="New Calender Event")
    #menu = MainForm(name="MainMenu")
    #menu.edit()
    #if "add" in menu.result:
    #    F, dtm = createCal(x)
    #    print(x)
    #print(x)
    return dtm

def displayCal(cal):
    print("Current Calendar:")
    print(cal)

if __name__ == '__main__':
    cal = npyscreen.wrapper_basic(main)
    print(cal)
    x.addEntry(cal)
    print(x)
    #myApp = CalendarApplication()
    #myApp.run()
    #print (npyscreen.wrapper_basic(myFunction))
