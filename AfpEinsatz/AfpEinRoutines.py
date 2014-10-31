#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 11.03.2014 Andreas Knoblauch - generated

import AfpBase
from AfpBase import AfpBaseRoutines
from AfpBase.AfpBaseRoutines import *

class AfpEinsatz(AfpSelectionList):
   def  __init__(self, globals, EinsatzNr, MietNr = None, ReiseNr = None, typ = None, debug = False):
      # either VorgangsNr or BuchungsNr has to be given for initialisation,
      # otherwise a new, clean object is created
      AfpSelectionList.__init__(self, globals, "Einsatz", debug)
      self.debug = debug
      self.mainindex = "EinsatzNr"
      if EinsatzNr:     
         self.new = False
         self.mainvalue = Afp_toString(EinsatzNr)
      elif MietNr or ReiseNr:
         self.set_new(MietNr, ReiseNr, typ)
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
      if self.debug: print "AfpEinsatz Konstruktor:", self.mainindex, self.mainvalue 
   def __del__(self):    
      if self.debug: print "AfpEinsatz Destruktor"
      
   def set_new(self, MietNr =  None, ReiseNr = None, infoindex = None,  typ = None):
      self.new = True
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
         self.set_data_values(data,"EINSATZ")
         selection = self.get_selection(select)
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
  
   def is_typ(self, typ):
      if self.get_value(typ +"Nr"):
         return True
      else:
         return False
  
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
         
   def get_einsatztage(self, time):
      day = self.globals.get_value("hours-per-day","Einsatz")
      hday = self.globals.get_value("hours-per-halfday","Einsatz")
      if type(time) == float:
         time = Afp_floatHoursToTime(time)
      days, hours = Afp_daysFromTime(time, day, hday)
      #print "AfpEinsatz.get_einsatztage:", time, "=", days, hours, "bei",day, hday
      return days, hours
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
   
   def create_FahrerList(self, indices = None):
      FahrerList = []
      if indices:
         for ind in indices:
            FahrerList.append(AfpFahrer(self.globals, self, ind, self.debug))
      else:
         for ind in range(self.get_value_length("FAHRER")):
             FahrerList.append(AfpFahrer(self.globals, self, ind, self.debug))
      return FahrerList
      
   def add_Ausgabe(self):
      if self.get_value("FremdNr.EINSATZ"):
         if "AUSGABE" in self.selections:
            self.delete_selection("AUSGABE")
         if self.get_value("ReiseNr.EINSATZ"):
            Fahrten = "\"Reisen\""
         else:
            Fahrten = "\"Fahrten\""       
         self.selects["AUSGABE"] = [ "AUSGABE","!Art = \"Fremdeinsatz\" and Typ = " + Fahrten] 
      
class AfpFahrer(AfpSelectionList):
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
   def __del__(self):    
      if self.debug: print "AfpFahrer Destruktor"
   def add_Ausgabe(self):
      if "AUSGABE" in self.selections:
         self.delete_selection("AUSGABE")
      if self.get_value("ReiseNr.EINSATZ"):
         Fahrten = "\"Reisen\""
      else:
         Fahrten = "\"Fahrten\""
      self.selects["AUSGABE"] = [ "AUSGABE","!Art = \"Einsatz\" and Typ = " + Fahrten] 
   def add_to_Archiv(self, new_data, delete = False):
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
      
      
   