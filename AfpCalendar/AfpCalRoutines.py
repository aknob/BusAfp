#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpCalendar.AfpCalRoutines
# AfpFiRoutines module provides classes and routines needed for finance handling and accounting,\n
# no display and user interaction in this modul.
#
#   History: \n
#        09 April 2015 - inital code generated - Andreas.Knoblauch@afptech.de

#
# This file is part of the  'Open Source' project "BusAfp" by 
#  AfpTechnologies (afptech.de)
#
#    BusAfp is a software to manage coach and travel acivities
#    Copyright (C) 1989 - 2015  afptech.de (Andreas Knoblauch)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
#    See the GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. 
#
import icalendar
from icalendar import Calendar, Event
from icalendar import vCalAddress, vText

import AfpBase
from AfpBase import AfpUtilities, AfpBaseRoutines
from AfpBase.AfpBaseRoutines import *
from AfpBase.AfpUtilities import AfpBaseUtilities
from AfpBase.AfpUtilities.AfpBaseUtilities import Afp_getNow

## class to handle calendar interactions 
class AfpCalConnector (object):
    ## initialize AfpCalendarConnector class
    # @param globals - globals variables possibly holding smtp-server data
    # @param debug - flag for debug information
    def  __init__(self, globals, name = "AfpTech", version = "", debug = False):
        self.globals = globals
        self.debug = debug
        #self.caldav_modul = AfpPy_Import("caldav")
        self.caldav_modul = None
        self.connector_name = name
        self.connector_version = version
        self.events = None
        self.starttime = None
        self.endtime = None
        self.summary = None
        self.description = None
        self.location = None
        self.uid = None
    ## generate calendar with all inserted events    
    def generate_calendar(self):
        if self.events:
            self.calendar = Calendar()
            self.calendar.add('prodid', "-//" + self.connector_name + " calendar connector//afptech.de//")
            self.calendar.add('version', self.connector_version)
            for event in self.events:
                self.calendar.add_component(event)
    ## generates icalendar object holding one event
    # @param start - start date and time of event (python datetime object)
    # @param end - end date and time of event (python datetime object)
    # @param summary - one line summery of purpose of event
    # @param uuid - unique id of this event
    # @param description - detailed description of this event
    # @param attendees - list of names and e-mail adresses of attendees [[name1, email1], ...]
    # @param orga - name and e-mail of organizer of this event [name, email]
    # @param loc - location to start this event
     def generate_calendar_with_one_event(self,  start, end, summary, uuid = None, description=None, attendees=None, orga = None, loc=None):
        evt_data = AfpCalEventData(self.globals, self.debug)
        evt_data.set_event(start, end, summary,  uid, description, attendees, orga, loc)
        self.add_event(evt_data)
        if self.is_ready()
            self.generate_calendar()
            return self.calendar
        else
            return None
     ## add an event to the connector
    # @param summary - one line summery of purpose of event
    # @param start - start date and time of event (python datetime object)
    # @param end - end date and time of event (python datetime object)
    # @param uuid - unique id of this event
    # @param orga - name and e-mail of organizer of this event [name, email]
    # @param attendees - list of names and e-mail adresses of attendees [[name1, email1], ...]
    # @param description - detailed description of this event
    # @param loc - location to start this event
    # @param name - name of product vreation this calendar
    # @param version - version of product creation this calendar
    def add_event_direct(self, summary, start, end, uuid = None, description=None, attendees=None, orga = None, loc=None):
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', Afp_getNow(True))
        event['uid'] = uuid
        event.add('priority', 5)
        if description: event.add('descrition', description)
        organizer = vCalAddress("MAILTO:" + orga[1])
        organizer.params['cn'] = vText(orga[0])
        event['organizer'] = organizer
        if loc: event['location'] = vText(loc)
        if attendees:
            for attend in attendees:
                attendee = vCalAddress("MAILTO:"+ attend[1])
                attendee.params['cn'] = vText(attend[0])
                attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
                event.add('attendee', attendee, encode=0)
        self.events.append(event)
    ## add an event to the connector
    # @param event_data - AfpCalEventData holding relevant data for this event
    def add_event(self, event_data):
        if event_data.is_ready():
            event = Event()
            event.add('summary', event_data.summary)
            event.add('dtstart', event_data.starttime)
            event.add('dtend', event_data.endtime)
            event.add('dtstamp', Afp_getNow(True))
            event['uid'] = event_data.gt_uid()
            event.add('priority', 5)
            if event_data.description: event.add('descrition', event_data.description)
            if event_data.organizer:
                organizer = vCalAddress("MAILTO:" + event_data.organizer[1])
                organizer.params['cn'] = vText(event_data.organizer[0])
                event['organizer'] = organizer
            if event_data.location: event['location'] = vText(event_data.location)
            if event_data.attendees:
                for attend in event_data.attendees:
                    attendee = vCalAddress("MAILTO:"+ attend[1])
                    attendee.params['cn'] = vText(attend[0])
                    attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
                    event.add('attendee', attendee, encode=0)
            self.events.append(event)
    ## calendar is ready if at least one event is attached
    def is_ready(self):
        if self.events: return True
        else: return False 
    ## write calendar into ics-file
    # @param filepath - path to destination ics-file
    def write_to_ics_file(self, filepath):
        if self.calendar :
            file = open(filepath, 'wb')
            file.write(self.calendar.to_ical())
            file.close()
    # read
    def read_ics_components(self, filepath):
        g = open(filepath,'rb')
        gcal = Calendar.from_ical(g.read())
        for component in gcal.walk():
            print component.name
        g.close()
    # read events
    def read_ics_events(self, filepath):
        g = open(filepath,'rb')
        gcal = Calendar.from_ical(g.read())
        for component in gcal.walk():
            if component.name == "VEVENT":
                print component.keys()
                for key in component.keys():
                    if type(component.get(key)) == list:
                        print key,":", type(component.get(key)), component.get(key)
                    else:
                        print key,":", type(component.get(key)), vars(component.get(key)), component.get(key)
        g.close()
 
## class to handle calendar events 
class AfpCalEventData (object):
    ## initialize AfpCalendarConnector class
    # @param globals - globals variables holding host data
    # @param debug - flag for debug information
    def  __init__(self, globals, debug = False):
        self.globals = globals
        self.debug = debug
        self.events = None
        self.starttime = None
        self.endtime = None
        self.uid = None
        self.summary = None
        self.description = None
        self.location = None
        self.organizer = None
        self.attendees = []
    # set begin and end to event
    # @param start - datetime for begin of event
    # @param end - datetime for end of event
    def set_times(self. start, end):
        self.starttime = Afp_toTzDatetime(start)
        self.endtime = Afp_toTzDatetime(end)
    # set unique ID
    # param uid - if given unique ID to be used, otherwise hostconfiguration and timestamp is used
    def set_uid(self, uid = None):
        if uid:
            self.uid = uid
        else:
            self.uid = self.globals.get_value("net-name") + "@" 
                            + self.globals.get_value("database") + "." 
                            + self.globals.get_value("database-host") + ":" 
                            + Afp_toString(Afp_getNow(True))
    ## returns the uid, generates it if necessary
    def get_uid(self):
        if uid is None:
            self.set_uid()
        return self.uid
    ## set text-portions of event
    # @param sum - summary of event
    # @param desc - description of event
    def set_text(self, sum, desc = None):
        if sum: self.summary = sum
        if desc: self.description = desc
    ## add attendee to list
    # @param name - name of attendee
    # @param mail - mail address of attendee
    def add_attendee(self, name, mail):
        self.attendee.append([mail, name])
    ## set organistion values
    # @param name - name of organizer
    # @param mail - mail address of organizer
    # @param loc - location for event
    def set_organize(self. name, mail, loc):
        orga = []
        if mail: orga.append(mail)
        else: orga.append("")
        if name: orga.append(name)
        else: orga.append("")
        if orga: self.organizer = orga
        if loc: self.location = loc
    ## set complete event in one shot
    # @param start - datetime for begin of event
    # @param end - datetime for end of event
    # @param summary - summary of event    
    # @param uid - if given unique ID to be used
    # @param description - if given, description of event    
    # @param attendees - if given, attendees of event, given as [[mail, name], ...]   
    # @param organizer - if given, organizer of event, given as [mail, name]   
    # @param location - if given, location for event
    def set_event(self, start, end, summary, uid = None, description = None, attendees = None, organizer = None, location = None):
        self.set_times(start, end)
        self.set_text(summary, description)
        self.set_uid(uid)
        if attendees: self.attendees = attendees
        if organizer: self.organizer = organizer
        if location: self.location = location
    # returns if the event has minimal entries
    def is_ready(self):
        return starttime and endtime and summary
        
        
     
        
        
        