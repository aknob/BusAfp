#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseRoutines
# AfpBaseRoutines module provides the base class for all 'Selection Lists', \n
#                             and Afp specific utility routines with or without database access \n
# it holds the calsses
# - AfpSelectionList
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

import sys
import AfpDatabase.AfpSQL
from AfpDatabase.AfpSQL import AfpSQLTableSelection

import AfpUtilities
from AfpUtilities import *
from AfpUtilities.AfpStringUtilities import *
from AfpUtilities.AfpBaseUtilities import *

# definition routines
## get all possible module with own graphical interfaces (screens)
def Afp_graphicModulNames():
   return ["Adresse","Charter"]
## get all possible internal moduls
def Afp_internalModulNames():
   return ["Finance","Einsatz"]
## get modul short names - used for filename generation
def Afp_getModulShortName(modul):
   if modul == "Einsatz": return "Ein"
   return modul[:2]
## return possible user-moduls \n
# - check if needed python moduls are present has to be implemented
def Afp_ModulNames():
   modules = Afp_graphicModulNames()
   # check if appropriate python files exists
   # AfpXXRoutines, AfpXXDialog, AfpXXScreen
   return modules
## get all possible afp-modul names
def Afp_allModulNames():
   modules = []
   mods = Afp_graphicModulNames()
   for mod in mods:
      modules.append(mod)
   mods = Afp_internalModulNames()
   for mod in mods:
      modules.append(mod)
   return modules
## check if modul is available
# @param input - name of modul or main table name
def Afp_getModulName(input):
   modul = None
   modules = Afp_ModulNames()
   if input:
      modul = input
      if input == "Fahrten": modul = "Charter"
   if modul and not modul in modules: return None
   return modul
## get all python-modules needed for a afp-modul
# @param modul - name of afp-modul
def Afp_ModulPyNames(modul):
   md = Afp_getModulShortName(modul)      
   parent = "Afp" + modul + "."
   files = [parent + "Afp" + md + "Screen", parent + "Afp" + md + "Dialog", parent + "Afp" + md + "Routines" ]
   if modul in Afp_internalModulNames():
      if modul == "Finance":
         return [files[2]]
      else:
         return files[1:3]
   elif modul in Afp_graphicModulNames():
      if modul == "Adresse":
         return [files[0]]
      else:
         return files
   return None
## get all python-modul file names for a afp-modul
# @param modul - name of afp-modul
# @param delimiter - path delimiter
# @param path - rootpath to python-modules
def Afp_ModulFileNames(modul, delimiter, path):
   files = []
   names = Afp_ModulPyNames(modul)
   for name in names:
      name = name.replace(".",delimiter)
      fname = Afp_addRootpath(path, name + ".py")
      files.append(fname)
   return files
## get information if all python-modul files exist for a afp-modul
# @param modul - name of afp-modul
# @param delimiter - path delimiter
# @param path - rootpath to python-modules
def Afp_existsModulFiles(modul, delimiter, path):
   filenames = Afp_ModulFileNames(modul, delimiter, path)
   if filenames:
      exists = True
      for file in filenames:
            exists = exists and Afp_existsFile(file)
      return exists
   return False
## get 'modul info' (timestamp) of all python-modul files for a afp-modul
# @param modul - name of afp-modul
# @param delimiter - path delimiter
# @param path - rootpath to python-modules
def Afp_getModulInfo(modul, delimiter, path):
   filenames = Afp_ModulFileNames(modul, delimiter, path)
   line = ""
   for file in filenames:
      split = file.split(delimiter)
      time = Afp_getFileTimestamp(file)
      line += split[-1] + ": " + Afp_toString(time.date()) + " " + Afp_toString(time.time() )+ '\n'
   return line
 
## look if text represents the name of archieved file (only used for compability of already created data) \n
# should return None for actuel created data
# @param text - text to be analysed
# @param delimiter - path delimiter
def Afp_archivName(text, delimiter):
   filename = None
   if text and "." in text and len(text) < 30:
      is_name = False
      is_archiv = False
      if "Archiv" == text[:6]: 
         is_name = True
         is_archiv = True
      else:
         mods = Afp_allModulNames()
         for mod in mods:
            if mod == text[:len(mod)]: is_name = True
      if is_name:
         if is_archiv:
            filename = Afp_pathname(text[6:], delimiter, True) 
         else:
            filename = Afp_pathname(text, delimiter, True) 
   return filename
   
##  starts a programfile with the associated program
# @param filename - name of file to be opened
# @param globals - global variables to hold file associations
# @param debug - flag for debug messages
# @param noWait - flag if execution of python program should be continued direct after starting execution of file
def Afp_startFile(filename, globals=None, debug = False, noWait = False):
   if debug: print "Afp_startFile:",filename
   program = None
   if globals and not globals.os_is_windows() and "." in filename:
      split = filename.split(".")
      ext = "." + split[-1]
      program = globals.get_value(ext)
   #Afp_startProgramFile(program, debug, filename, "--invisible")
   Afp_startProgramFile(program, debug, filename, None, noWait)

##   dynamic import of a python module from modulname,
# a handle to the modul will be returned
# @param modulname -  name of modul to be imported, in python modul syntax "package.modul"
# @param globals - global variables including the path delimiter to be used for filesystem pathes
def Afp_importPyModul(modulname, globals):
   deli = globals.get_value("path-delimiter")
   path = globals.get_programpath()
   if not path[-1] == deli: path += deli
   split = modulname.split(".")
   modul = split[-1]
   for i in range(len(split)-1):
      path += split[i] + deli
   if globals.is_debug(): print "Afp_importPyModul:", modulname, modul, path
   return AfpPy_Import(modul, path)
## dynamic import of 'Afp' modules,
#  depending on the modul there are one to three pythonfiles to be imported
# @param modulname - name of Afp-modul to be imported
# @param globals        - global variables
def Afp_importAfpModul(modulname, globals):
   moduls = []
   modulfiles = Afp_ModulPyNames(modulname)
   for mod in modulfiles:
      modul =  Afp_importPyModul(mod, globals)
      moduls.append(modul)
   if moduls:
      return moduls
   return None

##  write available data in 'Selection List' into a file
# @param selectionlist -  nselection list where data is extracted from
# @param fname - name and path of output file
def Afp_printSelectionListDataInfo(selectionlist, fname):
   info = selectionlist.get_data_info()
   fout = open(fname , 'w') 
   for entry in info:
      fout.write(entry +  ':\n')
      for name in info[entry]:
         fout.write("   " + name + "." + entry  + '\n')
   fout.close()
   
##  provide a list from a SQLTableSelection object -
#    mostly to allow additional selection
# @param table_sel - input AfpSQLTableSelection object for which an additional selection has to be made
# @param select     - filter to get possible additional selections from database
# @param ident      - identification column for filtered data entries 
# @param order     - order in which list is displayed
def Afp_getListe_fromTableSelection(table_sel, select, ident, order = None):
   attributs = table_sel.create_initialized_copy()
   attributs.load_data(select, order)
   manipulate = []
   deleted = 0
   if table_sel.get_data_length():
      for i in range(attributs.get_data_length()):
         for j in range(table_sel.get_data_length()):
            # delete entries already in table_sel
            if table_sel.get_values(ident, j) == attributs.get_values(ident, i):
               manipulate.append([i - deleted, None])
               deleted += 1
   if manipulate:
      attributs.manipulate_data(manipulate)
   liste = []
   for i in range(attributs.get_data_length()):
      liste.append(attributs.get_values(ident, i)[0][0])
   # return a slice to be shown (liste) and the complete values (attributs.get_values()) for further use
   return liste, attributs.get_values()

# with database access

##   retrieve a list of database entries with same "KundenNr" from table
# @param mysql - database where values are retrieved from
# @param table  - name of database table where values are retrieved from
# @param KNr      - value of "KundenNr" for values to be retrieved
# @param debug  - flag for debug messages
# @param felder  - names of tablecolumns from which values are catched
# @param filter_feld  - name tablecolumn where additional filter is used
# @param wanted_values  - values which are accepted in the tablecolumn 'filter_feld'
def Afp_selectSameKundenNr(mysql, table, KNr, debug = False, felder = None, filter_feld = None, wanted_values = None):
   selection = AfpSQLTableSelection(mysql, table, debug, False)
   selection.load_data("KundenNr = " + Afp_toString(KNr))
   if filter_feld and wanted_values:
      values = selection.get_values(filter_feld)
      lgh = len(values)
      for i in range(lgh-1,-1,-1):
         delete = True
         for want in wanted_values:
            if  values[i] == want: delete = False
         if delete: selection.delete_row(i)
   return selection.get_values(felder)
##  get special account from 'KtNr' table
#     return the accountnumber
# @param mysql - database where values are retrieved from
# @param ident  - identifier of account to be selected
def Afp_getSpecialAccount(mysql, ident):
   rows = mysql.select("KtNr","KtName = \"" + ident + "\"","KTNR")
   if rows: return rows[0][0]
   else: return 0
##  get individual account from 'KtNr' table
#     return the accountnumber
# @param mysql - database where values are retrieved from
# @param KNr  -  'KundenNr' of account to be selected
# @param typ   -  typ of account to be selected for this 'KNr'
def Afp_getIndividualAccount(mysql, KNr, typ = "Debitor"):
   # first step individual account
   KundenNr = Afp_toString(KNr)
   rows = mysql.select("KtNr","KtName = \"" + KundenNr + "\" AND Bezeichnung = \"" + typ + "\"","KTNR")
   if rows:
      return rows[0][0]
   if typ == "Debitor" or typ == "Kreditor":
      # extract name of Adress
      name = None
      rows = mysql.select("Name","KundenNr = " +KundenNr,"ADRESSE")
      if rows:
         name = rows[0][0]
      # second step, try sample account with max, first three letters of name
      if name:
         for i in range(3,0,-1):
            search = "DIV." + name[:i].upper()
            rows = mysql.select("KtNr","KtName = \"" + search + "\" AND Bezeichnung = \"" + typ + "\"","KTNR")
            if rows:
               return rows[0][0]
      # third step, try global sample account
      rows = mysql.select("KtNr","KtName = \"DIVER\" AND Bezeichnung = \"" + typ + "\"","KTNR")
      if rows:
         return rows[0][0]
   return 0

##   base class of all Afp-database objects
# common class to hold and manipulate the data for a given afp-module 
class AfpSelectionList(object):
   ## initialize AfpSelectionList class
   # @param globals - global values including the mysql connection - this input is mandatory
   # @param listname - name of this selction list
   # @param debug - flag for debug information
   def  __init__(self, globals, listname, debug = False):
      self.mysql = globals.get_mysql()
      self.globals = globals
      self.listname = listname
      self.mainindex = None
      self.mainvalue = None
      self.mainselection = None
      self.selects = {}
      self.selections = {}
      self.debug = debug
      self.new = False
      if self.debug: print "AfpSelectionList Konstruktor",listname
   ## destructor
   def __del__(self):   
      if self.debug: print "AfpSelectionList Destruktor" 
   ## return if debug flag is set
   def is_debug(self):
      return self.debug
   ## return if data is new (not yet stored in database)
   def is_new(self):
      return self.new
   ## return globals
   def get_globals(self):
      return self.globals
   ## return mysql connection
   def get_mysql(self):
      return self.mysql   
   ## return name of this SelectionList
   def get_listname(self):
      return self.listname
   ## return main index of this SelectionList
   def get_mainindex(self):
      return self.mainindex
   ## return the names of all Tableselections
   # @param include_mainselection - flas if mainselection name should be included
   def get_selection_names(self, include_mainselection = False):
      names = []
      for sel in self.selects:
         append = True
         if sel == self.mainselection and not include_mainselection: append = False
         if append:
            names.append(sel)
      return names
   ## return column name to be connected to mainindex for indicated selection
   # @param selname - name of selection where target column is extracted
   def get_select_target(self, selname):
      target = None
      if self.selects[selname]:
         select = self.selects[selname][1]
         split = select.split("=")
         target = split[0].strip()
         if  "." in target: target = target.split(".")[0]
      return target
   ## return an afp-unique identifier of this SelectionList
   def get_identifier(self):
      return self.listname + self.get_string_value()
   ## return the name of involved persons
   # @param rev - reverse, first name, followed by surname
   # @param selname - name of TableSelection where to retrieve names
   def get_name(self, rev = False, selname = "ADRESSE"):
      name = ""
      sel = self.get_selection(selname)
      if sel:
         if rev:
            name = sel.get_string_value("Name") + " " + sel.get_string_value("Vorname")
         else:
            name = sel.get_string_value("Vorname") + " " + sel.get_string_value("Name")
      return name
   ## show data in console (used for debug)
   def view(self):
      # convenience routine for debug purpose
      print "AfpSelectionList.view():", self.get_listname()
      for sel in self.selections: 
         print sel, self.selections[sel].data
   ## get the user-relevant data in a line \n
   # this routine may (or rather should) be overwritten
   def line(self): 
      row = self.get_value_rows(None, None, 0)
      zeile = Afp_genLineOfArr(row)
      return zeile
   ## generate the customised select_clause of this SelectionList for indicated TableSelection
   # @param selname - name of TableSelection
   def evaluate_selects(self, selname):
      select_clause = None
      if selname is None: selname = self.mainselection
      if selname in self.selects:
         if self.selects[selname] == []:
            select_clause = []
         else:
            select = self.selects[selname][1]
            if select[0] == "!": 
               # fixed fromula, no evaluation
               select_clause = select[1:]
            else:
               sels = select.split("=")
               feld = sels[1].lstrip()
               #print feld
               if "." in feld: value = self.get_string_value(feld, True)
               else: value = feld
               if value:
                  select_clause = sels[0] + "= " + value
      return select_clause
   ## set the customised select_clause for the main selection
   def set_main_selects_entry(self):  
      if self.mainselection and self.mainindex and self.mainvalue:         
         selname = self.mainselection
         self.selects[selname] = [selname, self.mainindex + " = " + self.mainvalue, self.mainindex]
   ## overwrite customised selects with new self.mainvalue
   def reset_selects(self):
      self.set_main_selects_entry()
      self.reload_selection(self.mainselection)
      for selname in self.selects:
         if selname in self.selections and not selname == self.mainselection :   
            self.reload_selection(selname)
   # selection handling
   ## return if a TableSelection exists in selections
   # @param selname - name of TableSelection
   def exists_selection(self, selname):
      if selname is None: selname = self.mainselection
      return selname in self.selections
   ## constitute selection formally, no data attached
   # @param selname - name of TableSelection
   def constitute_selection(self, selname):
      selection = None
      if selname is None: selname = self.mainselection
      if selname in self.selects:        
         sel_vals = self.selects[selname]
         if len(sel_vals) > 1:
            implicit = False
            unique = None
            if len(sel_vals) > 2: unique = sel_vals[2]
            #print "create_selection:", sel_vals, unique
            selection = AfpSQLTableSelection(self.mysql, sel_vals[0], self.debug, unique)
      return selection  
   ## create selection - retrieve values from database
   # @param select - name of TableSelection
   # @param allow_new - allow creation of a new TableSelection with no data attached
   def create_selection(self, select, allow_new = True):
      #print self.selects[select]
      if allow_new and self.new: new = True
      else: new = False
      selection = self.constitute_selection(select)
      select_clause = self.evaluate_selects(select)
      print "AfpSelectionList.create_selection:", select, select_clause, new, selection
      if selection is None and select_clause == []:
         if new: selection = self.spezial_selection(select, True)
         else:   selection = self.spezial_selection(select)
      elif selection and select_clause:
         if new: selection.new_data()
         else:   selection.load_data(select_clause)
      elif selection is None and select == self.mainselection:
         selection = AfpSQLTableSelection(self.mysql, select, self.debug, self.mainindex)
      if not selection is None:
         self.selections[select] = selection
   ## create all TableSelections
   def create_selections(self):
      for select in self.selects:
         if not select in self.selections:
            self.create_selection(select)
   ## attach new data to selection
   # @param selname - name of TableSelection
   def reload_selection(self, selname):
      selection = self.get_selection(selname)
      select_clause = self.evaluate_selects(selname)
      if selection and select_clause:
         selection.load_data(select_clause)
   ## return selection, create new if not existend
   # @param name - if given, name of TableSelection, otherwise get main selection
   def get_selection(self, name = None):
      selection = None
      if name is None: selname = self.mainselection
      else: selname = name
      #print "AfpSelectionList.get_selection:", selname in self.selections, selname, self.selections
      if not selname in self.selections:  
         self.create_selection(selname)
         #print "AfpSelectionList.get_selection created:", selname in self.selections, selname, self.selections
      if selname in self.selections: 
         selection = self.selections[selname]  
      else:
         selname = selname.upper()
         if not selname in self.selections:  
            self.create_selection(selname)
         if selname in self.selections: 
            selection = self.selections[selname]
      return selection
   ## clear data in selections
   # @param keep - list of names of selections not cleared
   def clear_selections(self, keep):
      self.mainvalue = None
      for sel in self.selections:
         if not sel in keep: 
            if sel == self.mainselection:
               self.selections[sel].new_data(False, True)
            else:
               self.selections[sel].new_data(True)
   ## delete selection completely
   # @param selname - name of TableSelection 
   # -  main selection can not be deleted
   def delete_selection(self, selname):
      if selname in self.selections and not selname == self.mainselection:
         del self.selections[selname]
   ## retrieve a selection row and deliver it as a single TableSelection \n
   # use set_row_to_selection_values to write manipulated values to the row again
   # @param selname - name of TableSelection 
   # @param row - index of row in TableSelection where data is retrieved
   def get_selection_from_row(self, selname, row):
      select = self.get_selection(selname)
      selection = select.create_initialized_copy()
      if row is None:
         selection.new_data()
      else:
         rows = select.get_values(None, row)         
         selection.set_data(rows)
      print "AfpSelectionList.get_selection_from_row:",selname, row, selection
      return selection
   ## delete a selection row from a TableSelection
   # @param selname - name of TableSelection 
   # @param row - index of row in TableSelection to be deleted
   def delete_row(self, selname, row):
      self.get_selection(selname).delete_row(row)
      
   ## special selection handling routine to be overwritten for individual selection programming
   # @param selname - name of special TableSelection 
   # @param new - iflag if a new selection without data should be created
   def spezial_selection(self, selname, new = False):
      return None
   ## special selection save routine to be overwritten for individual selection programming
   # @param name - name of special TableSelection 
   def spezial_save(self, name = None):
      return None
      
   ## get number of rows in indicated TableSelection
   # @param name - name of special TableSelection 
   def get_value_length(self, name = None):
      return self.get_selection(name).get_data_length()
   ## extract values from a single TableSelection
   # @param sel - if given name of TableSelection
   # - sel == None: data from mainselection, resp. row
   # - sel == 'Name': data from selection 'name', resp. row
   # @param felder - column names to be retrieved
   # - felder == 'Name1, Name2, ...': data from columns 'Name1, Name2, ... of selection
   # @param row - index of row in TableSelection
   def get_value_rows(self, sel = None, felder = None, row = -1):
      if sel is None and felder is None and row == -1:
         return self.mainvalue
      if sel is None:
         selname = self.mainselection
      else:
         selname = sel
      selection = self.get_selection(selname)
      if selection is None:
         return None
      else:
         return selection.get_values(felder, row)
   ## extract values from a different TableSelections
   # @param felder - column and selection names where data has to be retrieved from
   # - felder == None: complete data from mainselection
   # - felder == 'Feld1.Name1, Feld2.Name2, ...': data from column 'Feld1' of selection 'Name1', etc.
   def get_values(self, felder = None):
      if felder is None:
         return self.get_value_rows()
      else: 
         result = []
         fsplit = felder.split(",")
         for feld in fsplit:
            wert = self.get_value(feldname)
            result.append(wert)
         return [result]
   ## extract one value from a TableSelection
   # @param DateiFeld - column.selection name where data has to be retrieved from
   def get_value(self, DateiFeld = None):
      if DateiFeld is None:
         return self.mainvalue
      split = DateiFeld.split(".")
      feld = split[0]
      selname = self.mainselection
      if len(split) > 1: selname = split[1]
      selection = self.get_selection(selname)
      if selection is None:
         return None
      else:
         return selection.get_value(feld)  
   ## retrieve text from selection, eventually import extern file data into textfield  \n
   # - only needed for intermediate use, may be removed later
   # @param DateiFeld - column.selection name where data has to be retrieved from
   def get_ausgabe_value(self, DateiFeld = None):
      value = self.get_value(DateiFeld)
      if value:
         if Afp_isString(value):
            if len(value) == 16 and value[:6] == "Archiv" and value[-4:] == ".sbt":
               fname = self.globals.get_value("archivdir") + Afp_archivName(value, self.globals.get_value("path-delimiter"))
               wert = Afp_importFileData(fname)
            else:
               wert = value
         else:
            wert = Afp_toString(value)
      else:
         wert = ""
      return wert
   ## extract one value from a TableSelection, return it as a string
   # @param DateiFeld - column.selection name where data has to be retrieved from
   # @param quoted_string - retuns values as a string, returns strings in quotes
   def get_string_value(self, DateiFeld = None, quoted_string = False):
      value = self.get_value(DateiFeld)
      if value:
         if quoted_string:
            wert = Afp_toQuotedString(value)
         else:
            wert = Afp_toString(value)
      else:
         wert = ""
      return wert
   ## extract values from a single TableSelection, return values as strings
   # @param sel - if given name of TableSelection
   # @param felder - column names to be retrieved
   # @param row - index of row in TableSelection
   def get_string_rows(self,  sel = None, felder = None, row = -1):
      rows = self.get_value_rows(sel, felder,row)
      strings =  Afp_ArraytoString(rows)
      return strings
   ## set a database lock on the main selection (table) of the SelectionList
   def lock_data(self):
      self.get_selection().lock_data()   
   ## remove a database lock from the main selection (table) of the SelectionList
   def unlock_data(self):
      self.get_selection().unlock_data()
   ## propgate new mainvalue to the dependent TableSelections
   def spread_mainvalue(self):
      print "AfpTableSelectionList.spread_mainvalue"
      target = None
      # mainindex 
      source = self.mainindex + "." + self.mainselection
      value = Afp_fromString(self.mainvalue)
      # mainindex filled into all depending selections
      for sel in self.selections:
         if not sel == self.mainselection and self.selections[sel].data:
            select = self.selects[sel][1]
            print "AfpTableSelectionList.spread_mainvalue select:", sel, select, self.selections[sel].data
            if source in select:
               split = select.split("=")
               target = split[0].strip()
               if  "." in target: target = target.split(".")[0]
               print "AfpTableSelectionList.spread_mainvalue target:", sel, target, value
               if len(split) > 1 and "-" in split[1]:
                  self.selections[sel].spread_value(target, -value)
               else:
                  self.selections[sel].spread_value(target, value)
   ## sample newly created unique identifier value od dependent selection to the appropriate entries in the main selectrion
   # @param selname - name of TableSelection where new identifier has been created
   def resample_value(self, selname):
      print "AfpTableSelectionList.resample_value initiated:", selname
      target = None
      source = None 
      value = None 
      # uniqueindex
      selarr = self.selects[selname]
      if len(selarr) > 2:
         source = selarr[2] + "." + selname
      target = selarr[1].split("=")[1].strip()
      #print "AfpTableSelectionList.resample_value source:",source
      if source:
         split = source.split(".")
         #print "AfpTableSelectionList.resample_value split:", source, split
         if self.get_selection(split[1]).is_last_inserted_id(split[0]):
            value = self.get_value(source)
            #print "AfpTableSelectionList.resample_value executed:", source, target, value
            # uniqueindex filled back into mainselection
            self.set_value(target, value)
   ## set a single value of individual TableSelection 
   # @param DateiFeld - column.selection name where data has to be written to
   # @param value - new vaolue of above column
   def set_value(self, DateiFeld, value):
      split = DateiFeld.split(".")
      feld = split[0]
      selname = self.mainselection
      if len(split) > 1: selname = split[1]
      selection = self.get_selection(selname)
      selection.set_value(feld, value)
   ## set multiple  values of indicated TableSelection 
   # @param changed_data - dictionary with changed_data[column] = value
   # @param name - name of TableSelection where data should be written to
   # @param row - index of row in TableSelöection where data should be written to
   def set_data_values(self, changed_data, name = None, row = 0):
      #print "AfpSelectionList.set_data_values()",changed_data
      selection = self.get_selection(name)
      selection.set_data_values(changed_data, row)  
   ## set a row in a TableSelection to the modified values beeing hold in a single TableSelection \n
   # - this single TableSelection should have been extracted with get_selection_from_row from the destination TableSelection \n
   # - it is assumed that both TableSelections have the same tablename
   # @param value_selection - TableSelection holding the changed values
   # @param row - index of row in original TableSelection where data should be written to
   def set_row_to_selection_values(self, value_selection, row = -1):
      if row is None: row = -1
      selection = self.get_selection(value_selection.get_tablename())
      value_row = value_selection.get_values(None)[0]
      mani = [row, value_row]
      print "AfpSelectionList.set_row_to_selection_values:", mani
      selection.manipulate_data([mani])
   ## store complete SelectionList
   def store(self):
      #print "AfpTableSelectionList.store()", self.mainselection
      #print "AfpTableSelectionList.store() selections:", self.selections
      if self.mainselection:
         select = self.selections[self.mainselection]
         select.store()
         if self.new:
            self.mainvalue = select.get_string_value(self.mainindex)
            # spread mainvalue into selections
            # self.spread_value()
            self.spread_mainvalue()
            print "AfpTableSelectionList.store: new mainvalue spreaded to other selections", self.mainvalue
      #print "AfpTableSelectionList.store() selections 2:", self.selections
      for sel in self.selections:
         if not (sel == self.mainselection) and self.selections[sel].has_changed():
            if self.selects[sel] == []:
               self.spezial_save(sel)
            else:
               self.selections[sel].store()
            # eventually spread unique index back to mainselection
            self.resample_value(sel)
      # second try to catch all spreaded values
      for sel in self.selections:
         if self.selections[sel].has_changed():
            if self.selects[sel] == []:
               self.spezial_save(sel)
            else:
               self.selections[sel].store()
   ## get data info (column names of all attached TableSelections)
   def get_data_info(self):
      info = {}
      for entry in self.selections:
         info[entry] = self.get_selection(entry).feldnamen
      return info
    
   ## routine to retrieve payment data from SelectionList \n
   # may be overwritten, default implementation: return "Preis" and "Zahlung" column from main selection
   def get_payment_values(self):
      return self.get_value("Preis"),self.get_value("Zahlung")
   ## routine to set payment data in SelectionList \n
   # may be overwritten, default implementation: "Zahlung" and "ZahlDat" columns of main selection are set
   # @param payment - amount that already has been payed
   # @param datum - date of last payment
   def set_payment_values(self, payment, datum):
      self.set_value("Zahlung", payment)
      self.set_value("ZahlDat", datum)
   ## complete data to be stored in archive \n
   # - may be overwritten if necessary
   # @param new_data - data to be completed and written into "ARCHIV" TableSelection \n
   # new_data should already hold the values ["Gruppe"],[ "Bem"], ["Extern"]:
   # - Gruppe: (group) 3rd level identification
   # - Bem:  remark on this entry
   # - Extern:  name of archived file (relativ to archiv path) \n
   # it will be completed by:
   # - Art: (kind) 1st level identification, will be set to "BusAfp"
   # - Typ: (type) 2nd level identification, will be set to SelectionList listname
   def add_to_Archiv(self, new_data):
      archiv_select_value = None
      selection = self.get_selection("ARCHIV")
      if selection:
         archiv_select_field = self.listname[:4] + "Nr"
         if self.listname == "Charter" or self.listname == "Einsatz":
            archiv_select_field = "MietNr"
            if self.listname == "Einsatz": archiv_select_value = "FahrtNr.FAHRTEN"
         if self.listname == "Touristik":
            archiv_select_field = "AnmeldNr"
         row = selection.get_data_length()
         new_data["Art"] = "BusAfp"
         new_data["Typ"] = self.listname
         if archiv_select_value:
            new_data[archiv_select_field] = self.get_value(archiv_select_value)
         else:
            new_data[archiv_select_field] = self.get_value()
         new_data["KundenNr"] = self.get_value("KundenNr")
         new_data["Datum"] = self.globals.today()
         selection.set_data_values(new_data, row)
      else:
         print "WARNING SelectionList.add_to_Archiv called but not implemented for", self.listname
     