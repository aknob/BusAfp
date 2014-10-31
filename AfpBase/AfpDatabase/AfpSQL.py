#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpDatabase.AfpSQL
# AfpSQL module provides the connection to the MySql Interface,
# it holds the calsses
# - AfpSQL
# - AfpSelectionTable
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
import MySQLdb
import datetime


from AfpBase import AfpUtilities
from AfpBase.AfpUtilities import *
from AfpBase.AfpUtilities.AfpBaseUtilities import *
from AfpBase.AfpUtilities.AfpStringUtilities import *
 
##   provides a low level interface to MySql
class AfpSQL(object):
   ## constructor
   # @param dbhost, dbuser, dbword, dbname - host, user, password for connection, name of databse
   # @param debug - flag for debug output
   def  __init__(self, dbhost, dbuser, dbword, dbname, debug):
      self.dbname = dbname
      self.debug = debug
      self.db_connection = None
      self.db_cursor = None      
      self.db_connection = self.connect(dbhost,dbuser,dbword, self.dbname)
      self.db_cursor = self.db_connection.cursor()
      self.db_lastrowid = 0
      self.select_clause= None
      self.version = self.get_version()
      if self.debug: print "AfpSQL Konstruktor"
   ## destructor
   def __del__(self):
      if self.db_cursor: self.db_cursor.close ()
      if self.db_connection: self.db_connection.close ()
      if self.debug: print "AfpSQL Destruktor"
   ## switch debug on
   def set_debug(self):
      self.debug = True
   ## turn debug off
   def unset_debug(self):
      self.debug = False
   ## create connection to mysql database 
   # @param sql_host, sql_user, sql_word, sql_db - host, user, password for connection, name of database
   def connect(self, sql_host, sql_user, sql_word, sql_db):
      # connect to the MySQL server
      try:
         connection = MySQLdb.connect (host = sql_host,
                                user = sql_user,
                                passwd = sql_word.decode("base64"),
                                db = sql_db)
         if self.debug: print "AfpSQL connect:", sql_host, sql_user, sql_db
      except MySQLdb.Error, e:
         print "ERROR %d in MySQL connection: %s" % (e.args[0], e.args[1])
         sys.exit (1)
      return connection 
   def get_debug(self):
      return self.debug
   def get_dbname(self):
      return self.dbname
   def get_cursor(self):
      return self.db_cursor   
   def get_select_clause(self):
      return self.select_clause
   def get_version(self):
      Befehl = "SELECT VERSION()"
      if self.debug: print Befehl
      self.db_cursor.execute (Befehl)     
      rows = self.db_cursor.fetchall ()
      return rows[0][0]
   ## extract rows from database
   # @param feldnamen -  "*" for all fields or "field.table[.alias][, ...]" alias - of the concatination of fields
   # @param select         -  "field.table (>,<,>=,<=,==) value"
   # @param dateinamen  - "table[,...]" 
   # @param order          - "[column]" name of column
   # @param limit           - "[offset,number]" offset to select root, maximal number of rows extracted
   # @param  where         -  "[field1.table1 (>,<,>=,<=,==) (field2.table2,value)[(and,or) ...]]"
   # @param link            - "[field1.table1 == field2.table2 [and ...]]"
   def extract_clauses(self, feldnamen, select, dateinamen, order = None, limit = None, where=None, link=None):
      #print feldnamen,'\n', select,'\n', dateinamen,'\n', order,'\n', limit,'\n',where,'\n',link
      if  feldnamen.strip() == "*": all_fields = True
      else: all_fields = False
      limit_clause = ""
      if not limit is None: limit_clause = limit
      dat_clause = ""
      dateien = dateinamen.split()
      lgh = len(dateien)
      if lgh == 1 and all_fields: no_indicator = True
      else: no_indicator = False
      for i in range(0,lgh):
         if dat_clause == "": komma = ""
         else: komma = ","
         if no_indicator:
            dat_clause += komma +  self.dbname + "." + dateien[i].upper() 
         else:
            dat_clause += komma +  self.dbname + "." + dateien[i].upper() + " D" + str(i)

      if all_fields:
         feld_clause = "*"
      else:
         feld_clause = ""      
         felder = feldnamen.split(",")
         concat = ""
         for feld in felder:
            if feld_clause == "": komma = ""
            else: komma = ", "
            if concat: komma = ",\" \", " 
            fld = feld.split(".")
            i = -1
            dat = ""
            cons = ""
            cone = ""
            connew = ""
            if len(fld) > 1: 
               #print "extract_clauses:", fld[1], dateien, fld[1] in dateien
               if fld[1] in dateien: i = dateien.index(fld[1])
               else: i = dateien.index(fld[1].upper())
               if i > -1: dat = "D" + str(i) + "."
               if len(fld) > 2: connew = fld[2]
            if not connew == concat:
               if concat:
                  cone = ") AS " + concat
                  komma = ", "
               if connew:
                  cons = "CONCAT("
               concat = connew
            feld_clause += cone + komma + cons + dat + "`" + fld[0] + "`"
      order_clause = ""
      if not order is None:
         order_clause = Afp_SbToDbName(order, dateien)
      where_clause = ""
      if not select is None: 
         where_clause = Afp_SbToDbName(select, dateien)
      if not where is None: 
         where_clause += " and (" + Afp_SbToDbName(where, dateien) + ")"
      if not link is None: 
         where_clause += " and (" + Afp_SbToDbName(link, dateien) + ")"
      return [feld_clause, dat_clause, where_clause, order_clause, limit_clause]
   def select_strings(self, feldnamen, select, dateinamen, order = None, limit = None, where=None, link=None):
      rows = self.select( feldnamen, select, dateinamen, order, limit, where, link)
      string_rows = Afp_ArraytoString(rows)
      return string_rows
   def select(self, feldnamen, select, dateinamen, order = None, limit = None, where=None, link=None):      
      #if self.debug: print "AfpSQL.select:", feldnamen, select, dateinamen, order, limit, where, link
      clauses = self.extract_clauses(feldnamen, select, dateinamen, order, limit, where, link)
      Befehl = "SELECT "+ clauses[0] + " FROM " + clauses[1]  # feld_clause, dat_clause
      if not clauses[2] == "": Befehl += " WHERE "+ clauses[2]# where_clause 
      if not clauses[3] == "": Befehl += " ORDER BY "+ clauses[3] # order_clause 
      if not clauses[4] == "": Befehl += " LIMIT "+ clauses[4] # limit_clause 
      if self.debug: print "AfpSQL.select:",Befehl
      self.db_cursor.execute (Befehl)     
      rows = self.db_cursor.fetchall ()
      self.select_clause= Befehl
      return rows
   def lock(self, datei, select):
      Befehl = "SELECT * FROM "  + self.dbname + "." + datei + " WHERE "  + select + " LOCK IN SHARE MODE;"
      self.db_cursor.execute(Befehl)
      if self.debug: print Befehl
   def unlock(self):
      Befehl = "ROLLBACK;"
      self.db_cursor.execute(Befehl)
      if self.debug: print Befehl
   def get_last_inserted_id(self):
      return self.db_lastrowid
   def write_unique(self, datei, felder, data, select):
      if select is None:
         self.write_insert(datei, felder, data)
      else:
         self.write_update(datei, felder, data, select)
   def write_no_unique(self, select_clause, felder, data):
      split_clause = select_clause.split(" FROM ")
      if len(split_clause) == 2:
         self.write_delete(split_clause[1])
         split_dat = split_clause[1].split(" WHERE ")
         dateien = split_dat[0].split(",")
         if len(dateien) > 1 : print "AfpSQL.write_no_unique: multiple tables not yet possible!"
         datei = dateien[0].split(" ")[0]
         self.write_insert(datei, felder, data)
   def write_delete(self, select_where):
     # delete data from database
      Befehl = "DELETE FROM " + select_where
      if self.debug: print Befehl
      res = self.db_cursor.execute (Befehl)     
      self.db_cursor.execute("COMMIT;")
      if self.debug: print  "Deleted Rows:",res
   def write_update(self, datei, felder, data, select, no_commit= False):
      Befehl = None
      flen = len(felder)
      if len(data) == flen:
         set_clause =    (" SET %(set)s WHERE ") %   {"set"  : ",".join( [str(i)+"=%s" for i in felder] ) }
         Befehl =  "UPDATE " + self.dbname + "." + datei +  set_clause + select +";" 
      else:
         print "AfpSQL.write_update: length data does not match number of fields (", flen, ",", len(data), ")" 
      if not Befehl is None:
         if self.debug: print Befehl
         self.db_cursor.execute (Befehl, data)
         if not no_commit: self.db_cursor.execute("COMMIT;")      
   def write_insert(self, datei, felder, data):
      Befehl = None      
      flen = len(felder)   
      if not "." in datei: datei = self.dbname + "." + datei
      for datarow in data:
         if len(datarow) == flen:
            value_clause =  (" ( %(items)s ) VALUES ( %(values)s );") %  {"items" : ",".join(felder), "values" : ",".join( ["%s"]*flen ) }
            Befehl = "INSERT INTO "  +  datei + value_clause 
            if self.debug: print Befehl, datarow
            self.db_cursor.execute (Befehl, datarow)
            self.db_lastrowid = self.db_cursor.lastrowid
         else:
            print "AfpSQL.write_insert: length data does not match number of fields (", flen, ",", len(datarow), ")" 
      if not Befehl is None:
         self.db_cursor.execute("COMMIT;")

## handles SQL-selections for one table
class AfpSQLTableSelection(object):
   # handles SQL-selections for one table
   def  __init__(self, mysql, tablename, debug = False, unique_feldname = None, feldnamen = None):
      self.mysql = mysql      
      self.tablename = tablename
      self.feldnamen = feldnamen
      self.unique_feldname = unique_feldname 
      self.last_inserted_id = None
      self.select = None
      self.select_clause = None
      self.debug = debug
      self.new = False
      self.manipulation = []
      self.data = []
      if self.debug: print "AfpSQLTableSelection Konstruktor", self.tablename
      if self.feldnamen is None:
         self.feldnamen = []
         db_cursor = self.mysql.get_cursor()
         db_cursor.execute ("SHOW FIELDS FROM " + self.tablename)
         rows = db_cursor.fetchall ()
         for row in rows:
            self.feldnamen.append(row[0])
   def __del__(self):
      if self.debug: print "AfpSQLTableSelection Destruktor", self.tablename
   def create_initialized_copy(self):
      return AfpSQLTableSelection(self.mysql, self.tablename, self.debug, self.unique_feldname, self.feldnamen)
   def has_changed(self, feld = None):
      changed = False
      if self.manipulation:
         if feld is None:
            changed = True
         else:
            for entry in self.manipulation: 
               values = entry[1]
               if values is None or type(values) == list:
                  changed = True
               elif type(values) == dictionary:
                  if feld in values: changed = True
      elif self.new: changed = True
      return changed
   def is_last_inserted_id(self, feldname):
      flag = False
      if feldname in self.feldnamen:
         index = self.feldnamen.index(feldname)
         if self.last_inserted_id and self.data[0][index] == self.last_inserted_id:
            flag = True
      return flag
   def set_last_inserted_id(self, feldname, row = 0):
      if self.last_inserted_id and feldname in self.feldnamen:
         index = self.feldnamen.index(feldname)
         self.data[row][index] = self.last_inserted_id
         print "set_last_inserted_id:", self.last_inserted_id, self.data[row][index], self.data
   def set_select_criteria(self):
      # feld [<>=] integer
      if self.select:
         split = self.select.split(" ")
         feldname = split[0]
         value = int(split[2])
         last_index = self.get_data_length() - 1
         self.set_value(feldname, value, last_index)
   def load_data(self, select, order = None):
      self.select = select
      self.data = map(list, self.mysql.select("*",self.select, self.tablename, order))
      self.select_clause = self.mysql.get_select_clause()
      self.manipulation = []   
   def reload_data(self):
      if self.select: self.load_data(self.select)
   def load_datei_data(self, datei, select):  
      self.select = select
      self.data = map(list, [datei.get_values()])
      self.manipulation = []      
   def set_data(self, data, select=None):
      self.select = select      
      self.data = map(list, data) 
   def new_data(self, empty = False, no_criteria = False):
      self.new = True
      self.data = []
      if not empty: self.add_data_row(no_criteria)
   def add_data_row(self, no_criteria = False):
      data = []
      for feld in self.feldnamen:
         data.append(None)
      self.data.append(data)
      if not no_criteria: self.set_select_criteria()
      return self.get_data_length() - 1
   def delete_row(self, row = 0):
      if row >= 0 and row < self.get_data_length():
         mani = [row, None]
         self.manipulate_data([mani])
   def manipulate_data(self, changes):
      # changes = [rowindex, values]
      # delete:  values  = None
      # replace: values = {feld1: value1, ... }
      #                         = [value1, value2, ...] , len == len(self.feldnamen)
      # insert: rowindex  == -1
      #            values = [value1, value2, ...] , len == len(self.feldnamen)
      for entry in changes:
         print "AfpSQLTableSelection manipulate_data:", entry
         index = entry[0]
         values = entry[1]
         typ = ""
         if type(values) == dict: typ = "dict"
         elif type(values) == list: typ = "list"
         action = "replace"
         if index < 0 or index >=  len(self.data):
            action = "insert" # type(values) == list
         elif values is None:
            action = "delete"
         if self.unique_feldname: index = 0
         if action == "delete":
            # delete data row
            del self.data[index]
         elif action == "replace" and typ == "dict":
            for key in values:
               self.set_value(key, values[key], index)
         elif action == "replace" and typ == "list" and len(values) == len(self.feldnamen):
            self.data[index] = values
         elif action == "insert"  and typ == "list" and len(values) == len(self.feldnamen):
               self.data.append(values)
               self.set_select_criteria()
         else:
            print "ERROR: AfpSQLTableSelection.manipulate_data incorrect values"
         self.manipulation.append([action, index, values])
   def get_data_length(self):
      return len(self.data)
   def get_tablename(self):
      return self.tablename
   def get_feldnamen(self):
      return self.feldnamen  
   def get_feldindices(self, felder):
      split = felder.split(",")
      indices = []
      for feld in split:
         indices.append(self.feldnamen.index(feld))
      return indices
   def get_values(self, felder = None, row = -1):
      # felder == None: complete data, resp. row
      # felder == 'Name1, Name2, ...': data of columns Name1, Name2, ..., resp. only indicated row
      result = []
      if self.data:
         if felder is None:
            if row < 0:
               result = self.data
            elif row < len(self.data):
               result.append(self.data[row])
         else:
            split = felder.split(",")
            index = []
            for feld in split:
               if feld in self.feldnamen: index.append(self.feldnamen.index(feld))
            if self.data:
               #print "AfpSQLTableSelection.get_values:",self.data, self.feldnamen
               if row < 0:
                  for data in self.data:
                     result.append(Afp_extractPureValues(index,data))
               elif row < len(self.data):
                  result.append(Afp_extractPureValues(index,self.data[row]))
      #print "AfpSQLTableSelection;",result
      return result
   def get_value(self, feld):
      wert = None
      rows = self.get_values(feld)
      #print "get_value", rows, type(rows)      
      if type(rows) == list:
         if len(rows) > 0 :
            row = rows[0] 
            if type(row) == list:
               if len(row) > 0 : wert = row[0]
            else:
               wert = row
      else:
         wert = rows
      return wert
   def get_string_value(self, feld):
      string = Afp_toString(self.get_value(feld))
      return string
   def get_value_lines(self,  felder):
      lines = []
      rows = self.get_values(felder)
      for row in rows:
         lines.append(Afp_genLineOfArr(row))
      return lines
   def spread_value(self, feldname, value):
      lgh = self.get_data_length()
      for row in range(0,lgh):
         self.set_value(feldname, value,row)
   def set_value(self, feldname, value, row = 0):
      #print "AfpSQLTableSelection.set_value:", feldname, value, type(value), self.feldnamen
      if row >= self.get_data_length():
         row = self.add_data_row()
      if feldname in self.feldnamen:
         index = self.feldnamen.index(feldname)
         #if Afp_isString(value): value = Afp_fromString(value)
         self.data[row][index] = value
         #print "AfpSQLTableSelection.set_value:", row, index, feldname, value, type(value)
         self.set_manipulation(feldname, row, value)
   def set_data_values(self, changed_data, row = 0):
      print "AfpSQLTableSelection.set_data_value:", changed_data
      for data in changed_data:
         self.set_value(data, changed_data[data], row)
   def set_manipulation(self, feldname, row, value):
      for mani in self.manipulation:
         if mani[0] == "replace" and mani[1] == row:
            mani[2][feldname] = value
            break
      else:
         self.manipulation.append(["replace", row, {feldname: value}])
   def lock_data(self):
      self.mysql.lock(self.tablename,  self.select)
   def unlock_data(self):
      self.mysql.unlock()
   def store_data_direct(self, changed_data):
      self.mysql.write_unique( self.tablename, changed_data.keys(), changed_data.values(), None) 
   #def store_data(self, changed_data, new = False):
      # writes data coming from outside using this SelectionTable
      #if new:
         #self.mysql.write_unique( self.tablename, changed_data.keys(), changed_data.values(), None)
      #elif self.unique_feldname:
         #self.mysql.write_unique( self.tablename, changed_data.keys(), changed_data.values(), self.select)
      #elif self.unique_feldname is None:
         #self.manipulate_data(changed_data) # writes data into this SelectionTable
         #self.mysql.write_no_unique(self.select_clause, self.feldnamen, self.data) 
   def store(self):
      # writes data hold directly in this SelectionTable
      print "AfpSQLTableSelection.store:",self.tablename, self.unique_feldname
      if self.unique_feldname:
         for row in range(self.get_data_length()):
            unique_value = self.get_values(self.unique_feldname, row)[0][0]
            if not unique_value:
               print "AfpSQLTableSelection.store unique new value:", self.last_inserted_id, self.get_values(None, row)[0]
               self.mysql.write_insert( self.tablename, self.feldnamen, self.get_values(None, row))
               self.last_inserted_id = self.mysql.get_last_inserted_id() 
               print "AfpSQLTableSelection.store uniquelast_inserted_id:",  self.last_inserted_id
               self.set_last_inserted_id(self.unique_feldname, row)
            else:
               select = self.unique_feldname + " = " + Afp_toString(unique_value)
               print "AfpSQLTableSelection.store unique value already set:", select, self.get_values(None, row)[0]
               self.mysql.write_unique( self.tablename,  self.feldnamen, self.get_values(None, row)[0], select)            
      else:
         new = False 
         if self.select_clause is None: 
            new = True
         else:
            print "AfpSQLTableSelection.store manipulation:", self.manipulation
            print "AfpSQLTableSelection.store data:", self.data
            if self.manipulation:
               new = True
               for mani in self.manipulation:
                  if not mani[0] == "insert": new = False
         print "AfpSQLTableSelection.store new:", new, self.new
         if new or self.new:
            print "AfpSQLTableSelection.store insert:", self.get_values()
            self.mysql.write_insert( self.tablename, self.feldnamen, self.get_values())
         else:
            print "AfpSQLTableSelection.store() no_unique:", self.get_values()            
            self.mysql.write_no_unique(self.select_clause, self.feldnamen, self.get_values())
      self.new = False
      self.manipulation = []
      
# Main   
if __name__ == "__main__":
   mysql = AfpSQL("127.0.0.1","server", "YnVzc2U=","BusAfp", False)
   #selection = AfpSQLTableSelection(mysql,"ADRESATT",False)
   #selection.load_data("KundenNr = 6467")
   #data = [['6467', u'Knoblauch', u'Mitarbeiter', u'Mitarbeiter         06467', u'Mitarbeiter         Knoblauch', u'', u'', u''], ['6467', u'Knoblauch', u'Fahrer', u'Fahrer              06467', u'Fahrer              Knoblauch', u'', u'', u'']]
   #selection.set_data(data)
   #rows = selection.get_value()
   #print "Initial: \n", rows
   #row = Afp_copyArray(rows[1])
   #row[0] = 0
   #print row
   #changes = [ [-1, row] ]
   #selection.store_data(changes)
   #print "Insert:\n",selection.get_value()
   #changes = [ [2,{"Attribut":"Fahrer 1","Name":"Knoblauch 1"}] ]
   #selection.store_data(changes)
   #print "Modify:\n",selection.get_value()  
   #changes = [ [2,None] ]
   #selection.store_data(changes)
   #print "Delete:\n",selection.get_value()
   #version = mysql.get_version()
   #print version   
   Befehl = "INSERT INTO FAHRTEN (KundenNr,Abfahrt,Zielort,Art,Datum,Zustand,Von,Nach) VALUES(6467,'2014-04-10','Hamburg','MTF',CURDATE(),'KVA','von','nach');" 
   print Befehl
   mysql.db_cursor.execute (Befehl)   
   Befehl = "SELECT LAST_INSERT_ID();"
   id = mysql.db_cursor.execute (Befehl)
   print Befehl, id
   id = mysql.db_cursor.fetchone ()
   print "fetchone",id
   id = mysql.db_cursor.fetchall ()
   print "fetchall:",id
   id = mysql.db_cursor.lastrowid
   print "lastrowid:", id
   id = mysql.db_connection.insert_id()
   print "connection insert_id:", id
