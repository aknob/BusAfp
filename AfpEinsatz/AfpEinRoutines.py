#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpEinsatz.AfpEinRoutines
# AfpEinRoutines module provides classes and routines needed for handling of vehicle operations,\n
# no display and user interaction in this modul.
#
#   History: \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        11 Mar. 2014 - inital code generated - Andreas.Knoblauch@afptech.de

#
# This file is part of the  'Open Source' project "BusAfp" by 
#  AfpTechnologies (afptech.de)
#
#    BusAfp is a software to manage coach and travel acivities
#    Copyright (C) 1989 - 2014  afptech.de (Andreas Knoblauch)
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
      if MietNr or ReiseNr: self.set_new(MietNr, ReiseNr, typ)
      if self.debug: print "AfpEinsatz Konstruktor:", self.mainindex, self.mainvalue 
   ## destructor
   def __del__(self):    
      if self.debug: print "AfpEinsatz Destruktor"
      
   ## clear current SelectionList to behave as a newly created List 
   # @param MietNr - if given, identifier of charter this operation should be attached to
   # @param ReiseNr -  if given, identifier of touristic tour this operation should be attached to
   # @param infoindex -  if given, index of info the data should be extracted from
   # @param typ -  if given, typ how start and enddate of input data have to be interpreted
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
         print "AfpEinsatz.set_new:", data, select
         self.set_data_values(data,"EINSATZ")
         selection = self.get_selection(select)
         print "AfpEinsatz.set_new:", selection, selection.select, selection.data
         data["Datum"] = selection.get_value("Abfahrt")
         data["EndDatum"] = selection.get_value("Fahrtende")
         info = self.get_Fahrtinfo(infoindex, typ)         
         if typ:
            #if typ == "start": data["Datum"] = Afp_addDaysToDate(selection.get_value("Abfahrt"), 1, "-")
            if typ == "end": data["EndDatum"] = Afp_addDaysToDate(selection.get_value("Fahrtende"), 1)
         if info:
            data["Datum"] = info[0]
            data["Zeit"] = info[1]
            data["Stellort"] = info[2]
         self.set_data_values(data,"EINSATZ")
      self.new = True
  
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
         if index is None:
            for row in rows:
               if (typ == "start" and "Hin Ab" in row[3]) or (typ == "end" and "Her Ab" in row[3]):
                  index = row.index()
         if not index is None:
            info = rows[index][:3]
      return info
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
   # @param hours - hours not fitting into a complete working days
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
      
      
   