#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 14.02.2014 Andreas Knoblauch - generated

import AfpBaseRoutines
from AfpBaseRoutines import *
# for main execution
#import AfpGlobal
#import AfpDatabase
#from AfpDatabase import AfpSuperbase
#import AfpCharter
#from AfpCharter import AfpChRoutines


#class AfpZahlung(AfpSelectionList):
class AfpZahlung(object):
   def  __init__(self, data , multiName = None, debug = False):
      # data has to be given for initialisation,
      #AfpSelectionList.__init__(self, data.get_globals(), "Zahlung", debug)
      self.globals = data.get_globals()
      self.mysql = self.globals.get_mysql()
      self.moduls = {}
      self.debug = debug
      self.amount = []
      self.partial = []
      self.balance = []
      self.distribution = None
      self.finance_modul = None
      self.finance = None
      self.auszug = None
      self.datum = None
      self.ausgang = False
      self.selected_list = [data]
      self.append_payment_data(data)
      if multiName:
         value = data.get_value(multiName)
         if value > 0:
            feld = data.get_mainindex()
            table = data.get_tablename()
            select = multiName + " = " + Afp_toString(value)
            rows = self.mysql.select(feld, select, table)
            if len(rows) > 1:
               ident = data.get_value()
               for row in rows:
                  if row[0] != ident: 
                     self.add_selection(table, row[0])
      if not self.globals.skip_accounting():
         self.finance_modul = Afp_importAfpModul("Finance", self.globals)[0]
         if self.finance_modul:
            self.finance = self.finance_modul.AfpFinTrans(self.globals)
      print "AfpZahlung.finance:", self.finance
      if self.debug: print "AfpZahlung Konstruktor:", multiName
   def __del__(self):    
      if self.debug: print "AfpZahlung Destruktor"
      #AfpSelectionList.__del__(self)     
   def view(self):
      print "AfpZahlung.view():"
      for data in self.selected_list: data.view()
      if self.finance: self.finance.view() 
   def check_selection(self, tablename, nr):
      found = False      
      for data in self.selected_list:
         if data.get_selection().get_tablename() == tablename and data.get_value() == nr: 
            found = True
      return found
   ## check if statement of account (Auszug) exists, if not create one
   # @param auszug - identifier of statemen of account
   def check_auszug(self, auszug):
      datum = None
      if self.finance:
         check = self.finance.check_auszug(auszug)
         if check:
            datum = self.finance.get_value("BuchDat.AUSZUG")         
      else:
         check =  True
         datum = self.globals.today()
      if check:   
         self.auszug = auszug
         if datum: self.datum = datum
      return check
   ## check if statement of account (Auszug) exists, if not create one
   # @param auszug - identifier of statemen of account
   # @param datum -  the date when statement has been recorded
   def set_auszug(self, auszug, datum):
      if auszug == self.auszug and datum is None: return
      self.auszug = auszug 
      if self.finance:
            if datum is None: datum = self.globals.today()
            self.finance.set_auszug(auszug, datum)
      else:
         datum = self.globals.today()
      self.datum = datum
      print "AfpZahlung.set_auszug:", self.auszug, self.datum
   def append_payment_data(self, data):
      amount, partial = data.get_payment_values()
      self.amount.append(amount)
      self.partial.append(partial)
      if self.partial[-1] is None: self.partial[-1] = 0.0      
      self.balance.append(int(100* (self.amount[-1] - self.partial[-1])))      
      print "AfpZahlung.append_payment_data()", self.amount, self.partial, self.balance
   def set_payment_data(self, index):
      data = self.selected_list[index]
      payment = float(self.distribution[index])/100
      tablename = data.get_selection().get_tablename()
      if Afp_isEps(payment):
         sum = self.partial[index] + payment
         today = data.get_globals().get_value("today")
         data.set_payment_values(sum, today)
         self.add_payment_transaction(payment, data)
         self.partial[index] = sum
   def add_selection(self, tablename, nr):
      added = False
      sellist = None
      if not self.check_selection(tablename, nr):
         if tablename == "FAHRTEN":
            modul = self.get_modul("AfpChRoutines")
            if modul:
               sellist = modul.AfpCharter(self.globals, nr, None, self.debug)
         if tablename == "RECHNG":
            sellist = AfpRechnung(self.globals, nr, self.debug)
        #if tablename == "ANMELD":
            #sellist = AfpAnmeldung(self.globals, nr)
            #self.preis += sellist.get_value("Preis")
            #self.anzahlung += sellist.get_value("Zahlung")
         if sellist:
            sellist.lock_data()
            self.selected_list.append(sellist)
            self.append_payment_data(sellist)
            self.distribution = None
            added = True
      return added
   def add_payment_transaction(self, payment, data = None):
      # data == None: multiple payment to be booked through intermediate account
      if self.debug: print "AfpZahlung.add_payment_transaction():", payment, data
      if self.finance: 
         self.finance.add_payment(payment, self.datum, self.auszug, self.get_KundenNr(), self.get_name(), data)
   def remove_selection(self, index):
      if index < len(self.selected_list):
         del self.selected_list[index]
         del self.amount[index]
         del self.partial[index]
         del self.balance[index]
   def get_modul(self, name):
      if not name in self.moduls:
         modul = AfpPy_Import(name)
         if modul: self.moduls[name] = modul
      if name in self.moduls:
         return self.moduls[name]
      else:
         return None
   def get_mysql(self):
      return self.mysql
   def get_debug(self):
      return self.debug  
   def get_data(self):
      return self.selected_list[0]
   def get_value(self,DateiFeld):
      return self.get_data().get_value(DateiFeld)
   def get_string_value(self,DateiFeld):
      #print DateiFeld
      return self.get_data().get_string_value(DateiFeld)
   def get_name(self):
      data = self.get_data()
      name = data.get_string_value("Vorname.ADRESSE") + " " + data.get_string_value("Name.ADRESSE") 
      return name  
   def get_KundenNr(self):
      KNr = self.get_data().get_value("KundenNr")
      return KNr
   def get_preis(self):
      preis = 0.0
      for prs in self.amount:
         preis += prs
      return Afp_toString(preis)
   def get_anzahlung(self):
      anzahlung = 0.0
      for anz in self.partial:
         anzahlung += anz
      return Afp_toString(anzahlung)
   def get_gutschrift(self):
      return ""
   def get_display_list(self):
      liste = []
      for entry in self.selected_list:
         liste.append(entry.get_listname()[:2] + ": " + entry.line())
      return liste
   ## distributes the given payment to all selected data entries \n
   # should only be called once, when all data has been gathered
   # @param value - amount of payment
   def distribute_payment(self, value):
      if Afp_isEps(value):
         self.generate_distribution(value)
         lgh = len(self.selected_list)
         # charge payment on intermediate account
         if lgh > 1: 
            self.add_payment_transaction(value)
         # execute each gathered payment
         for i in range(lgh):
            self.set_payment_data(i)
   ## core routine to generate distribution of payment to selected data, \n
   # pure integer calculation on cent basis is used.
   # @param value - amount of payment
   def generate_distribution(self, value):
      # pure integer calculation on cent basis
      if Afp_isEps(value):
         distribute = int(value*100)
         balance = 0
         for bal in self.balance:
            balance += bal
         if distribute >= balance:
            self.distribution = self.balance
            if distribute > balance:
               self.distribution[0] += distribute -  balance
         else:
            #lgh = len(self.selected_list)
            lgh = len(self.amount)
            self.distribution = [0]*lgh  
            filled = 0
            while filled < lgh and distribute > lgh - filled:
               entries = lgh - filled
               per_entry = int(distribute/entries)
               #print "while:", distribute, per_entry, filled
               kept = 0
               spend = 0
               for i in range(0,lgh):
                  amount_left = self.balance[i] - self.distribution[i]
                  if amount_left:
                     if per_entry < amount_left:
                        self.distribution[i] += per_entry
                        spend += per_entry
                     else:
                        spend += self.balance[i] - self.distribution[i] 
                        self.distribution[i] = self.balance[i]
                        filled += 1
                  #print i, amount_left, self.distribution[i], spend
               distribute -= spend
            #print "end while", filled, distribute, spend
            if distribute > 0:
               self.distribution[0] += distribute
   def store(self):
      for entry in self.selected_list: entry.store()
      if self.finance: self.finance.store()

class AfpRechnung(AfpSelectionList):
   def  __init__(self, globals, RechNr = None, debug = False, complete = False):
      # either FahrtNr or sb (superbase) has to be given for initialisation,
      # otherwise a new, clean object is created
      AfpSelectionList.__init__(self, globals, "Rechnung", debug)
      self.debug = debug
      self.new = False
      self.mainindex = "RechNr"
      self.mainvalue = ""
      self.spezial_bez = []
      if RechNr:
         self.mainvalue = Afp_toString(RechNr)
      else:
         self.new = True
      self.mainselection = "RECHNG"
      self.set_main_selects_entry()
      if not self.mainselection in self.selections:
         self.create_selection(self.mainselection)   
      #  self.selects[name of selection]  [tablename,, select criteria, optional: unique fieldname]
      self.selects["ADRESSE"] = [ "ADRESSE","KundenNr = KundenNr.RECHNG"] 
      self.selects["FAHRTEN"] = [ "FAHRTEN","RechNr = RechNr.RECHNG"] 
      if complete: self.create_selections()
      if self.debug: print "AfpRechnung Konstruktor, RechNr:", self.mainvalue
   def __del__(self):    
      if self.debug: print "AfpRechnung Destruktor"
      #AfpSelectionList.__del__(self)  
   def set_new(self, KundenNr):
      self.new = True
      data = {}
      keep = []
      if KundenNr:
         data["KundenNr"] = KundenNr
      else:
         data["KundenNr"] = self.get_value("KundenNr")
         keep.append("ADRESSE")
      data["Zustand"] = "offen"
      data["Datum"] = self.globals.get_string_value("today")
      #print data
      #print keep
      self.clear_selections(keep)
      self.set_data_values(data,"RECHNG")
      if KundenNr:
         self.create_selection("ADRESSE", False)
         self.set_value("Name", self.get_name(True))
   def line(self):
      zeile = self.get_string_value("RechNr").rjust(8) + " " + self.get_string_value("Datum") + " " + self.get_string_value("Wofuer") + " " 
      zeile += self.get_string_value("Zahlbetrag").rjust(10) + " " + self.get_string_value("Zahlung").rjust(10)
      return zeile  
   def set_zustand(self):
      if self.get_value("Zustand") == "offen" and self.get_value("Zahlung") >= self.get_value("ZahlBetrag"):
         self.set_value("Zustand","bezahlt")
   def set_payment_values(self, payment, datum):
      AfpSelectionList.set_payment_values(self, payment, datum)
      self.set_zustand()
      if self.get_value("MietNr"):
         self.set_value("Zahlung.FAHRTEN", payment)
         self.set_value("ZahlDat.FAHRTEN", datum)
  
            
# Main      
if __name__ == "__main__":
   #mysql = AfpSQL.AfpSQL("127.0.0.1","server", "YnVzc2U=","BusAfp", False)
   #set = AfpGlobal.AfpSettings(False)
   #globals = AfpGlobal.AfpGlobal(mysql, set)
   #sb = AfpSuperbase.AfpSuperbase(globals, False)
   #sb.open_datei("ADRESSE")
   #sb.open_datei("ARCHIV")
   #sb.open_datei("AUSGABE")
   #sb.open_datei("FAHRTI")
   #sb.open_datei("FAHRTEX")
   #sb.open_datei("FAHRTVOR")
   #sb.open_datei("FAHRTEN")
   #sb.open_datei("RECHNG")
   #sb.CurrentIndexName("FahrtNr")   
   #sb.select_key(1436)
   #sb.CurrentIndexName("Zielort")   
   #Charter = AfpChRoutines.AfpCharter(globals,None,sb,True,True)
   #Test = AfpZahlung(Charter)
   #amount = [500.00,500.00,700.00,250.00]
   #amount = [500.00,500.00,700.00]
   #partial = [250.00,250.00,300.00,200.00]
   #partial = [250.00,250.00,250.00]
   #partial = [550.00,500.00,700.00,250.00]
   #balance = []
   #for i in range(0,len(amount)):
      #balance.append(int(100*(amount[i] - partial[i])))
   #Test.amount = amount
   #Test.partial = partial
   #Test.balance = balance
   #print partial
   #Test.distribute_payment(1000.00)
   #print Test.partial
    print "Hallo"  
      
   