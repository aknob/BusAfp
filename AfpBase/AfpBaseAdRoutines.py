#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseAdRoutines
# AfpBaseAdRoutines module provides classes and routines needed for adress handling,\n
# no display and user interaction in this modul.
#
#   History: \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        30 Nov. 2012 - inital code generated - Andreas.Knoblauch@afptech.de

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
from AfpBase import AfpDatabase, AfpBaseRoutines
from AfpBase.AfpDatabase import AfpSQL
from AfpBase.AfpDatabase.AfpSQL import AfpSQLTableSelection
from AfpBase.AfpBaseRoutines import *

## return dictionary to map between status integers an choice entries on screen   
def AfpAdresse_StatusMap():
   return {-1:1,0:0,1:1,5:2,6:3,9:4}
## mapping in other direction \n
# return status flöag indicated by input
# @param ind - index in screen choice selection
def AfpAdresse_StatusReMap(ind):
   return AfpDict_ReMap(AfpAdresse_StatusMap(), ind)
 
## baseclass for address handling      
class AfpAdresse(AfpSelectionList):
   ## initialize AfpAdresse class
   # @param globals - global values including the mysql connection - this input is mandatory
   # @param KundenNr - if given and sb == None, data will be retrieved this database entry
   # @param sb - if given data will  be retrieved from the actuel AfpSuperbase data
   # @param debug - flag for debug information
   # @param complete - flag if data from all tables should be retrieved durin initialisation \n
   # \n
   # either KundenNr or sb (superbase) has to be given for initialisation,otherwise a new, clean object is created
   def  __init__(self, globals, KundenNr = None, sb = None, debug = False, complete = False):
      # either KundenNr or sb (superbase) has to be given for initialisation,
      # otherwise a new, clean object is created
      AfpSelectionList.__init__(self, globals, "ADRESSE", debug)
      self.debug = debug
      self.new = False
      self.mainindex = "KundenNr"
      self.mainvalue = ""
      self.spezial_bez = []
      if sb:
         self.mainvalue = sb.get_string_value("KundenNr.ADRESSE")
         AdSelection = sb.gen_selection("ADRESSE", "KundenNr", debug)
         self.selections["ADRESSE"] = AdSelection
      else:
         if KundenNr:
            self.mainvalue = Afp_toString(KundenNr)
         else:
            self.new = True
      self.mainselection = "ADRESSE"
      self.set_main_selects_entry()
      if not self.mainselection in self.selections:
         self.create_selection(self.mainselection)
      self.selects["ADRESATT"] = [ "ADRESATT","KundenNr = KundenNr.ADRESSE"] 
      self.selects["Bez"] = []   
      if sb:
         if sb.is_open("ANMELD"): self.selects["ANMELD"] = [ "ANMELD","KundenNr = KundenNr.ADRESSE"] 
         if sb.is_open("FAHRTEN"): self.selects["FAHRTEN"] = [ "FAHRTEN","KundenNr = KundenNr.ADRESSE"] 
         if sb.is_open("RECHNG"): self.selects["RECHNG"] = [ "RECHNG","KundenNr = KundenNr.ADRESSE"] 
         if sb.is_open("VERBIND"): self.selects["VERBIND"] = [ "VERBIND","KundenNr = KundenNr.ADRESSE"] 
      self.mainselection = "ADRESSE"
      if not self.mainselection in self.selections:
         self.create_selection(self.mainselection)
      if complete: self.create_selections()
      if self.debug: print "AfpAdresse Konstruktor, KundenNr:", self.mainvalue
   ## destructor
   def __del__(self):    
      if self.debug: print "AfpAdresse Destruktor"
   ## special selection (overwritten from AfpSelectionList) \n
   # to handle the selction 'Bez' (Beziehung) which connects different address entries via a single connected list in the datafield 'Bez'
   # @param selname - name of selection (in oru case 'Bez' is implemented)
   # @param new - flag if a new empty list has t be created
   def spezial_selection(self, selname, new = False):
      AdSelection = None
      if selname == "Bez":
         #print  self.selections["ADRESSE"].get_feldnamen()
         feldnamen = self.selections["ADRESSE"].get_feldnamen()
         if new:
             AdSelection = AfpSQLTableSelection(self.mysql, "ADRESSE", self.debug, None, feldnamen) 
             AdSelection.new_data()
         else: 
            AdSelection = AfpSQLTableSelection(self.mysql, "ADRESSE", self.debug, None, feldnamen) 
            KNr = self.selections["ADRESSE"].get_value("Bez")
            if not KNr: KNr = 0
            data = []
            self.spezial_bez = []
            if KNr != 0:
               Index = feldnamen.index("Bez")
               KundenNr = int(self.mainvalue)
               while KNr !=  KundenNr and KNr != 0 :
                  if KNr < 0: KNr = - KNr
                  row = self.mysql.select("*","KundenNr = " + Afp_toString(KNr), "ADRESSE")
                  self.spezial_bez.append(KNr)
                  KNr = int(row[0][Index])
                  data.append(row[0])
               AdSelection.set_data(data)
      return AdSelection
   ## special save (overwritten from AfpSelectionList) \n
   # store the special selection 'Bez'
   # @param selname - name of selection (in oru case 'Bez' is implemented)
   def spezial_save(self, selname):
      if selname == "Bez": 
         selection = self.selections[selname]
         lgh = selection.get_data_length()
         if lgh > 0:
            KNr = int(self.mainvalue)
            bez_lgh = len(self.spezial_bez)
            for i in range(lgh):
               KundenNr = KNr
               index = -1
               if KundenNr in self.spezial_bez: 
                  index = self.spezial_bez.index(KundenNr)
                  self.spezial_bez[index] = None
               KNr = int(selection.get_values("KundenNr", i))
               self.mysql.write_update("ADRESSE", ["Bez"], [KNr], "KundenNr = " + Afp_toString(KundenNr), True)
            if KNr in self.spezial_bez: 
               index = self.spezial_bez.index(KNr)
               self.spezial_bez[index] = None
            self.mysql.write_update("ADRESSE", ["Bez"], [self.mainvalue], "KundenNr = " + Afp_toString(KNr))
         for KNr in self.spezial_bez:
            if KNr: self.mysql.write_update("ADRESSE", ["Bez"], ["0"], "KundenNr = " + Afp_toString(KNr))
   ## get short identifier of name \n
   # currently a trigram is used, first letter of surname plus first and second letter of lastname
   def get_short_name(self):
      vorname = self.get_string_value("Vorname")
      name = self.get_string_value("Name")
      return vorname[0].lower() + name[:2].lower()
      