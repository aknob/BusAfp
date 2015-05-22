#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpEinsatz.AfpEinRoutines
# AfpEinRoutines module provides classes and routines needed for handling of vehicle operations,\n
# no display and user interaction in this modul.
#
#   History: \n
#        05 May 2015 - attach to calendar- Andreas.Knoblauch@afptech.de \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        11 Mar. 2014 - inital code generated - Andreas.Knoblauch@afptech.de

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

import AfpBase
from AfpBase import AfpBaseRoutines
from AfpBase.AfpBaseRoutines import *

## class to handle vehicle operations (Einsatz)
class AfpEinsatz(AfpSelectionList):
    ## initialize class AfpEinsatz
    # @param globals - global values including the mysql connection - this input is mandatory
    # @param EinsatzNr - identifier of a certain operation incident
    # @param MietNr - if given, identifier of a charter incident
    # @param ReiseNr - if given, identifier of a touristic entry
    # @param typ - if MietNr or ReiseNr is given, typ how start and enddate of input data have to be interpreted
    # @param debug - flag for debug information \n
    # \n
    # either EinsatzNr or ((MietNr or ReiseNr) and typ) has to be given for initialisation, otherwise a new, clean object is created
    def  __init__(self, globals, EinsatzNr, MietNr = None, ReiseNr = None, typ = None, debug = False):
        AfpSelectionList.__init__(self, globals, "Einsatz", debug)
        self.debug = debug
        self.mainindex = "EinsatzNr"
        if EinsatzNr:     
            self.new = False
            self.mainvalue = Afp_toString(EinsatzNr)
        else:
            self.mainvalue = ""
        self.mainselection = "EINSATZ"
        self.set_main_selects_entry()
        if not self.mainselection in self.selections:
            self.create_selection(self.mainselection)
        self.selects["FAHRTEN"] = [ "FAHRTEN","FahrtNr = MietNr.EINSATZ"] 
        self.selects["FAHRTI"] = [ "FAHRTI","FahrtNr = FahrtNr.FAHRTEN"] 
        self.selects["REISEN"] = [ "REISEN","FahrtNr = ReiseNr.EINSATZ"] 
        self.selects["FAHRER"] = [ "FAHRER","EinsatzNr = EinsatzNr.EINSATZ"] 
        self.selects["BUSSE"] = [ "BUSSE","Name = Bus.EINSATZ"] 
        self.selects["FremdAdresse"] = [ "ADRESSE","KundenNr = FremdNr.EINSATZ"]  
        self.selects["FahrtAdresse"] = [ "ADRESSE","KundenNr = KundenNr.FAHRTEN"]  
        self.selects["ReiseAdresse"] = [ "ADRESSE","KundenNr = KundenNr.REISEN"]  
        if MietNr or ReiseNr: self.set_new(MietNr, ReiseNr, None, typ)
        self.calendar = None
        self.calendar_modul = None
        self.calendar_modul = Afp_importPyModul("AfpCalendar.AfpCalRoutines", globals)
        if self.calendar_modul:
            self.calendar = self.calendar_modul.AfpCalendar(globals, debug)
        if self.debug: print "AfpEinsatz Konstruktor:", self.mainindex, self.mainvalue 
    ## destructor
    def __del__(self):    
        if self.debug: print "AfpEinsatz Destruktor"
      
    ## clear current SelectionList to behave as a newly created List 
    # @param MietNr - if given, identifier of charter this operation should be attached to
    # @param ReiseNr -  if given, identifier of touristic tour this operation should be attached to
    # @param infoindex -  if given, index of info the data should be extracted from
    # @param typ -  if given, typ how start and enddate of input data have to be interpreted (None, start, end)
    def set_new(self, MietNr =  None, ReiseNr = None, infoindex = None,  typ = None):
        data = {}
        keep = []
        select = "" 
        if MietNr:
            data["MietNr"] = MietNr
            select = "FAHRTEN"
        elif ReiseNr:
            data["ReiseNr"] = ReiseNr
            select = "REISEN"
        else:
            self.set_value("EinsatzNr", 0)
            self.set_value("Bus", "")
            keep.append("EINSATZ")
            keep.append("FAHRTEN")
            keep.append("REISEN")
            keep.append("FahrtAdresse")
            keep.append("ReiseAdresse")
            self.clear_selections(keep)
        if data and select:
            print "AfpEinsatz.set_new:", infoindex, typ, data, select
            self.set_data_values(data,"EINSATZ")
            selection = self.get_selection(select)
            print "AfpEinsatz.set_new:", selection, selection.select, selection.data
            data["Datum"] = selection.get_value("Abfahrt")
            data["EndDatum"] = selection.get_value("Fahrtende")
            info = self.get_Fahrtinfo(infoindex, typ)         
            if info:
                data["Datum"] = info[0]
                data["Zeit"] = info[1] 
                data["StellOrt"] = info[2]
                if info[0] and info[1]:
                    dattime = Afp_toDatetime(info[0], info[1]) 
                    endtime = self.gen_arrivaltime(dattime, typ)
                    if endtime:
                         data["EndDatum"] = endtime.date()
                         data["EndZeit"] = endtime.time()
                    diff1 = Afp_toTimedelta(self.globals.get_value("stell-difference","Einsatz"))
                    if diff1: dattime -= diff1
                    data["StellDatum"] = dattime.date()
                    data["StellZeit"] = dattime.time()
                    if typ == "end":
                        dattime = self.gen_arrivaltime(dattime, "minus")
                    else:
                        diff2 = Afp_toTimedelta(self.globals.get_value("start-difference","Einsatz"))
                        if diff2: dattime -= diff2
                    data["AbDatum"] = dattime.date()
                    data["AbZeit"] = dattime.time()
            self.set_data_values(data, "EINSATZ")
        self.new = True

    ## update all calendar entries
    def update_calendar(self):
        if self.calendar:
            print "AfpEinsatz.update_calendar: Calendar modul available"
            self.add_vehicle_to_calendar()
            self.add_driver_to_calendar()
        else:
            print "AfpEinsatz.update_calendar: Calendar modul not available!"
    ## add calendar changes due to vehicle modifications to calendar
    def add_vehicle_to_calendar(self): 
        Einsatz = self.get_selection()
        print "AfpEinsatz.add_vehicle_to_calendar new:", self.new, "has changed:", Einsatz.has_changed(None, True)
        if self.new or Einsatz.has_changed(None, True):
            orig = Einsatz.manipulation_get_value("Bus", True)
            new = Einsatz.get_value("Bus")
            email = self.globals.get_value("mail-sender")
            print "AfpEinsatz.add_vehicle_to_calendar orig:", orig, "new:", new
            uid = self.get_value("Datei")
            default_calendar = self.globals.get_value("calendar-default","Einsatz")
            if not default_calendar: default_calendar = "Default"
            if not orig is None:
                if not orig: orig = default_calendar
                self.calendar.gen_new_target(orig, email)
                self.calendar.add_event_to_target("delete", None, None, None, uid)
            if not new: new = default_calendar
            self.calendar.gen_new_target(new, email)
            start = self.get_datetime("Ab")# start == None: wenn Zeit fehlt auf 0:00 oder festen Wert setzen?
            ende = self.get_datetime("End") # ende == None: wenn Zeit fehlt auf 23:59oder festen Wert setzen?
            summary = self.get_cal_summary()
            print "AfpEinsatz.add_vehicle_to_calendar times:", start, ende
            if not uid: 
                uid = self.gen_cal_uid()
                self.set_value("Datei", uid)
            content = self.get_cal_content()
            location = self.get_value("StellOrt")
            if self.new:
                self.calendar.add_event_to_target("new", start, ende, summary, uid, content, location)
            else:
                self.calendar.add_event_to_target("replace", start, ende, summary, uid, content, location)
    ## add calendar changes due to driver modifications to calendar
    def add_driver_to_calendar(self): 
        print "AfpEinsatz.add_driver_to_calendar"
        if self.exists_selection("FAHRER"):
            FahrSel = self.get_selection("FAHRER")
            if FahrSel.has_changed():
                indices = FahrSel.manipulation_get_indices()
                # look if rows have been deleted
                for i, ind in enumerate(indices):
                    if ind is None:
                        FNr = FahrSel.manipulation_get_value("FahrerNr", True, i)
                        # to do: rename column 'ExText' to 'UID'
                        uid = FahrSel.manipulation_get_value("ExText", True, i)
                        email = AfpAdresse(self.get_globals(), FNr).get_value("Mail")
                        if Afp_isMailAddress(email):
                            self.calendar.gen_new_target(None, email)
                            self.calendar.add_event_to_target("delete", None, None, None, uid)
                # look if rows have been changed
                for i in range(FahrSel.get_data_length()):
                    changed = False
                    row = -1
                    while not changed and i in indices[row+1:]:
                        row = indices.index[i]
                        if self.driver_cal_changed(row):
                            changed = True
                    if changed:
                        Fahrer = AfpFahrer(self.get_globals(), self, row, self.is_debug())
                        email = Fahrer.get_value("Mail","ADRESSE")
                        if Afp_isMailAddress(email):
                            self.calendar.gen_new_target(None, email)
                            start = Fahrer.get_datetime()
                            ende = Fahrer.get_datetime(True)
                            summary = self.get_cal_summary()
                            uid = Fahrer.get_value("ExText", row)
                            if not uid: 
                                uid = self.gen_driver_uid(row)
                                self.set_data_values({"ExText": uid},"FAHRER", row)
                            content = self.get_cal_content()
                            content += "\n" + Fahrer.get_cal_content()
                            location = Fahrer.get_value("AbOrt")
                            if location is None: location = self.get_value("StellOrt")
                            self.calendar.add_event_to_target("replace", start, ende, summery, uid, content, location)
    ## decide whether a new or modified calendar entry is needed                            
    def driver_cal_changed(self, row):
        Fahrer = self.get_selection("Fahrer")
        kept = Fahrer.manipulation_get_value("Datum", False, row) is None
        kept = kept and Fahrer.manipulation_get_value("EndDatum", False, row) is None
        kept = kept and Fahrer.manipulation_get_value("Von", False, row) is None
        kept = kept and Fahrer.manipulation_get_value("Bis", False, row) is None
        kept = kept and Fahrer.manipulation_get_value("Abfahrt", False, row) is None
        kept = kept and Fahrer.manipulation_get_value("AbZeit", False, row) is None
        return not kept
    ## individual store routine (overwritten from SelectionList)    
    def store(self):
        super(AfpEinsatz, self).store()
        if self.calendar: 
            self.update_calendar()  
            if self.get_selection().has_changed() or self.get_selection("FAHRER").has_changed():
                self.new = False
                super(AfpEinsatz, self).store()
            self.calendar.drop_on_targets()
            self.calendar.clear_targets()
    ## check if attached data is of the input typ
    # @param typ - typ to be checked
    def is_typ(self, typ):
        if self.get_value(typ +"Nr"):
            return True
        else:
            return False
    ## return typ-string to be displayed
    def get_typ(self):
        typ = ""
        if self.is_typ("Miet"):
            selection = self.get_selection("FAHRTEN")
            if selection.get_data_length() > 1:
                typ = "+ Mietfahrten +"
            else:
                typ = "Mietfahrt"
        elif self.is_typ("Reise"):
            selection = self.get_selection("REISEN")
            if selection.get_data_length() > 1:
                typ = "+ Reisen +"
            else:
                typ = "Reise"
        return typ
    ## extract date, time and address from possibly given data
    # @param index - index of row in given data
    # @param typ -  how dates of input data have to be interpreted
    def get_Fahrtinfo(self, index , typ = None):
        info = None
        if self.is_typ("Miet"):
            rows = self.get_value_rows("FAHRTI","Datum,Abfahrtszeit,Adresse1,Adresse2")
            sel = self.selections["FAHRTI"]
            print "AfpEinsatz.get_fahrtinfo sel:",sel.select, sel.data
            print "AfpEinsatz.get_fahrtinfo rows:", rows
            if index is None:
                for i, row in enumerate(rows):
                    if (typ == "start" and "Hin Ab" in row[3]) or (typ == "end" and "Her Ab" in row[3]):
                        index = i
            if not index is None:
                info = rows[index][:3]
        print "AfpEinsatz.get_fahrtinfo:", index, typ, info
        return info
    ## get appropriate datetime value from date and time entry
    # @param name - name of timevalue to be composted
    def get_datetime(self, name):
        date = self.get_value(name + "Datum")
        time = self.get_value(name + "Zeit")
        if date and time:
            return Afp_toDatetime(date, time)
        else:
            return None
    ## generate approximated time of arrival
    # @param start - datetime object holding starttime
    # @param typ - typ for result generation (None, start, end, minus)
    def gen_arrivaltime(self, starttime, typ):
        endtime = None
        if self.is_typ("Miet"):
            if self.get_value("Art", "FAHRTEN") == "Transfer":
                km = self.get_value("Km", "FAHRTEN")
                if km:
                    if typ == "end" or typ == "minus": km = km/4
                    else: km = km/2
                    kmph = self.globals.get_value("km-per-hour","Einsatz")
                    if not kmph: kmph = 60
                    hours = int(km/kmph) + 1
                    if typ == "minus":
                        endtime = starttime - Afp_fromString(Afp_toString(hours) + ":00")
                    else:
                        endtime = starttime + Afp_fromString(Afp_toString(hours) + ":00")
        return endtime
     ## return summary of calnedar entry
    def get_cal_summary(self):
        if self.get_value("MietNr"):
            summary = self.get_string_value("Zielort","Fahrten") + " " + self.get_string_value("Art","Fahrten") + " " + self.get_string_value("Name","FahrtAdresse")
        else:
            summary = "AfpEinsatz: Calendar-Summery not implemented!"
        return summary
    ## return content of calendar entry
    def get_cal_content(self):
        if self.get_value("MietNr"):
            content = "Zielort: " + self.get_string_value("Zielort","Fahrten") + "\n"
            content += "Abfahrtszeit: " + self.get_string_value("Zeit") + " " + self.get_string_value("Datum") + "\n"
            content += "Stellzeit: " + self.get_string_value("StellZeit") + " " + self.get_string_value("StellDatum") + "\n"
            content += "Stellort: " + self.get_string_value("StellOrt") + "\n"
        else:
            content = "AfpEinsatz: Calendar-Content not implemented!"
        return content
    ## generate unified id for this vehicle operation calendar entr\y  \n
    # id will be generated in the following manner: \n
    # VOP-xxxxx-Name@database-host
    # - VOP - abbraviation for 'vehicle operation'
    # - xxxxx - internal identification numer of vehicle operation
    # - Name - name of product used
    # - database-host - name or ip of database host used to store values
    def gen_cal_uid(self):
        ENr = self.get_string_value("EinsatzNr") 
        if ENr:
            uid = "VOP-" + ENr + "-" + self.globals.get_value("name") + "@"+  self.globals.get_value("database-host")
        else:
            uid = None
        return uid
    ## generate unified id for this driver calendar entr\y  \n
    # id will be generated in the following manner: \n
    # DRV-xxxxx-yyyzz-Name@database-host
    # - DRV - abbraviation for 'driver operation'
    # - xxxxx - internal identification numer of vehicle operation
    # - yyy - short form of driver identification
    # - zz - short form of driver identification
    # - Name - name of product used
    # - database-host - name or ip of database host used to store values
    # @param index - row index for driver in selection
    def gen_driver_uid(self, index):
        ENr = self.get_string_value("EinsatzNr")
        if ENr:
            uid = "DRV-" + ENr + "-" + self.get_string_value("Kuerzel","FAHRER") + Afp_toString(index)
            uid += self.globals.get_value("name") + "@"+  self.globals.get_value("database-host")
        else:
            uid = None
        return uid
    ## extract complete working days and hours from given time interval
    # @param time - timeval interval to be analysed
    def get_einsatztage(self, time):
        day = self.globals.get_value("hours-per-day","Einsatz")
        hday = self.globals.get_value("hours-per-halfday","Einsatz")
        if type(time) == float:
            time = Afp_floatHoursToTime(time)
        days, hours = Afp_daysFromTime(time, day, hday)
        #print "AfpEinsatz.get_einsatztage:", time, "=", days, hours, "bei",day, hday
        return days, hours
    ## extract spesen from working days and hours
    # @param tage - complete working days
    # @param std - hours  (Stunden) not fitting into a complete working days
    def get_spesen(self, tage, std = None):
        spesen = 0.0
        if tage:
            pro_tag = self.globals.get_value("spesen-per-day","Einsatz")
            spesen += tage * pro_tag
        if std:
            pro_std =  self.globals.get_value("spesen-per-hour","Einsatz")
            max = 0
            max_value = 0.0
            if pro_std:
                for entry in pro_std:
                    val = int(entry)
                    if val <= std and val >= max:
                        max = val
                        max_value = pro_std[entry]
            spesen += max_value
        return spesen
    ## create list of drivers to be displayed 
    # @param indices - if given, indices of drivers which should be inserted 
    def create_FahrerList(self, indices = None):
        FahrerList = []
        if indices:
            for ind in indices:
                FahrerList.append(AfpFahrer(self.globals, self, ind, self.debug))
        else:
            for ind in range(self.get_value_length("FAHRER")):
                 FahrerList.append(AfpFahrer(self.globals, self, ind, self.debug))
        return FahrerList
    ## add appropriate SelectionList for output  
    def add_Ausgabe(self):
        if self.get_value("FremdNr.EINSATZ"):
            if "AUSGABE" in self.selections:
                self.delete_selection("AUSGABE")
            if self.get_value("ReiseNr.EINSATZ"):
                Fahrten = "\"Reisen\""
            else:
                Fahrten = "\"Fahrten\""       
            self.selects["AUSGABE"] = [ "AUSGABE","!Art = \"Fremdeinsatz\" and Typ = " + Fahrten] 

## class for driver handling      
class AfpFahrer(AfpSelectionList):
    ## initialize class AfpFahrer
    # @param globals - global values including the mysql connection - this input is mandatory
    # @param Einsatz - operation SelectionList this driver entry should be attached to
    # @param index - index of driver in operation SelectionList this object refers to
    # @param debug - flag for debug information \n
    def  __init__(self, globals, Einsatz, index = 0, debug = False):
        AfpSelectionList.__init__(self, globals, "FAHRER", debug)
        self.debug = debug
        self.mainindex = "EinsatzNr"
        self.mainselection = "FAHRER"
        self.archiv_select_field = None
        self.selections["FAHRER"] = Einsatz.get_selection_from_row("FAHRER",index)
        self.selections["EINSATZ"] = Einsatz.get_selection("EINSATZ")
        self.selections["BUSSE"] = Einsatz.get_selection("BUSSE")
        if Einsatz.get_value("ReiseNr"):
            self.archiv_select_field = "ReiseNr"
            self.selections["Fahrt"] = Einsatz.get_selection("REISEN")
            self.selections["FahrtAdresse"] = Einsatz.get_selection("ReiseAdresse")
        else:
            self.archiv_select_field = "MietNr"
            self.selections["Fahrt"] = Einsatz.get_selection("FAHRTEN")
            self.selections["FahrtAdresse"] = Einsatz.get_selection("FahrtAdresse")
        self.selects["ADRESSE"] = [ "ADRESSE","KundenNr = FahrerNr.FAHRER"] 
        self.archiv_select_value = self.get_value(self.archiv_select_field + ".EINSATZ")
        select = self.archiv_select_field + " = " + Afp_toString(self.archiv_select_value) + " AND Gruppe = \"Einsatz\""
        selection = AfpSQLTableSelection(self.get_mysql(), "ARCHIV", self.debug)
        selection.load_data(select)
        self.selections["ARCHIV"] = selection
        if self.debug: print "AfpFahrer Konstruktor:", self.mainindex, self.mainvalue
    ## destructor
    def __del__(self):    
        if self.debug: print "AfpFahrer Destruktor"
    ## get appropriate datetime value from date and time entry
    # @param end - flag if endtime should be usde, otherwise starttime is returned
    def get_datetime(self, end = False):
        date = None
        time = None
        if end:
            date = self.get_value(name + "EndDatum")
            time = self.get_value(name + "Bis")
            default = "24:00"
        else:
            time = self.get_value("Von")
            default = "0:00"
        if date is None: date = self.get_value("Datum")    
        if time is None: time = Afp_fromString(default)
        if date and time:
            return Afp_toDatetime(date, time)
        else:
            return None
    ## return content of calendar entry
    def get_cal_content(self):
        content = "Fahrer: " + self.get_name() + "\n"
        content += "Einsatzbeginn: " + self.get_string_value("Von") + " " + self.get_value("Datum") + "\n"
        content += "Einsatzende: " + self.get_string_value("Bis") + " " + self.get_value("EndDatum") + "\n"
        content += "Abfahrtszeit: " + self.get_string_value("AbZeit") + " " + self.get_value("Abfahrt") + "\n"
        content += "Abfahrtsort: " + self.get_string_value("AbOrt") + "\n"
        return content
    ## add appropriate SelectionList for output  
    def add_Ausgabe(self):
        if "AUSGABE" in self.selections:
            self.delete_selection("AUSGABE")
        if self.get_value("ReiseNr.EINSATZ"):
            Fahrten = "\"Reisen\""
        else:
            Fahrten = "\"Fahrten\""
        self.selects["AUSGABE"] = [ "AUSGABE","!Art = \"Einsatz\" and Typ = " + Fahrten] 
    ## complete data to be stored in archive \n
    # - overwritten from parent
    # @param new_data - data to be completed and written into "ARCHIV" TableSelection \n
    def add_to_Archiv(self, new_data):
        selection =self.get_selection("ARCHIV")
        row = selection.get_data_length()
        new_data["Art"] = "BusAfp"
        if self.archiv_select_field == "ReiseNr": new_data["Typ"] = "Touristik"
        else: new_data["Typ"] = "Charter"
        new_data[self.archiv_select_field] = self.archiv_select_value
        new_data["KundenNr"] = self.get_value("FahrerNr")
        if new_data["Bem"]: new_data["Bem"] += " " + self.get_string_value("Kuerzel")
        else: new_data["Bem"] = self.get_string_value("Kuerzel")
        new_data["Datum"] = self.globals.today()
        #print new_data
        selection.set_data_values(new_data, row)
      
      
   