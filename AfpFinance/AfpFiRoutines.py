#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 14.02.2014 Andreas Knoblauch - generated

## @package AfpFinance.AfpFiRoutines
# AfpFiRoutines module provides classes and routines needed for finance handling and accounting,\n
# no display and user interaction in this modul.
#
#   History: \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        14 Feb. 2014 - inital code generated - Andreas.Knoblauch@afptech.de

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

## calss to handle finance depedencies
class AfpFinance(AfpSelectionList):
   ## initialize class
   # @param globals - global values including the mysql connection - this input is mandatory
   # @param debug - flag for debug information
   # @param Von - identifier of a certain incident
   # @param VorgangsNr - identifier of a certain action
   # @param BuchungsNr - identifier of a certain entry
   # @param complete - flag if data from all tables should be retrieved durin initialisation \n
   # \n
   # either Von, VorgangsNr or BuchungsNr has to be given for initialisation, otherwise a new, clean object is created
   def  __init__(self, globals, debug = False, Von = None, VorgangsNr = None, BuchungsNr = None,  complete = False):
      AfpSelectionList.__init__(self, globals, "BUCHUNG", debug)
      self.file = None
      self.transfer = None
      self.debug = debug
      if Von or VorgangsNr or BuchungsNr:     
         self.new = False
         if BuchungsNr:
            self.mainindex = "BuchungsNr"
            self.mainvalue = BuchungsNr
         elif VorgangsNr:
            self.mainindex = "VorgangsNr"
            self.mainvalue = VorgangsNr
         else:
            self.mainindex = "Von"
            self.mainvalue = Von
      else:
         # empty object to hold financial accounting data
         self.new = True
         self.mainindex = "VorgangsNr"
         self.mainvalue = ""
      self.mainselection = "BUCHUNG"
      self.set_main_selects_entry()
      if not self.mainselection in self.selections:
         self.create_selection(self.mainselection)
      self.selects["AUSZUG"] = [ "AUSZUG","Auszug = Beleg.BUCHUNG"] 
      self.selects["Konto"] = [ "KTNR","KtNr = Konto.BUCHUNG"] 
      self.selects["Gegenkonto"] = [ "KTNR","KtNr = Gegenkonto.BUCHUNG"] 
      if self.debug: print "AfpFinance Konstruktor:", self.mainindex, self.mainvalue 
   ## destructor
   def __del__(self):    
      if self.debug: print "AfpFinance Destruktor"

## class to sample all entries needed for one action
class AfpFinTrans(AfpSelectionList):
   ## initialize class
   # @param globals - global values including the mysql connection - this input is mandatory
   # a new, clean object is created
   def  __init__(self, globals):
      AfpSelectionList.__init__(self, globals, "BUCHUNG", globals.is_debug())
      self.file = None
      self.transfer = None
      # just empty object to hold financial accounting data
      self.new = True
      self.mainindex = "BuchungsNr"
      self.mainvalue = ""
      self.mainselection = "BUCHUNG"
      self.set_main_selects_entry()
      if not self.mainselection in self.selections:
         self.create_selection(self.mainselection)
      self.selects["AUSZUG"] = [ "AUSZUG","Auszug = Beleg.BUCHUNG"] 
      if self.debug: print "AfpFinTrans Konstruktor:", self.mainindex, self.mainvalue 
   ## destructor
   def __del__(self):    
      if self.debug: print "AfpFinTrans Destruktor"
   ## set identifier of statement of account (Auszug)
   # @param auszug - identifier of statement of account (xxnnn - xx identifier of bankaccount, nnn number)
   # @param datum, - idate of statement of account 
   def set_auszug(self, auszug, datum):
      if auszug == self.get_value("Auszug.AUSZUG"): return
      ausname = Afp_getStartLetters(auszug) 
      if not ausname: return
      today = self.globals.today()
      if datum is None: datum = today
      self.selects["Auszugkonto"] =  [ "KTNR","KtName = \"" + ausname.upper() + "\""] 
      self.create_selection("Auszugkonto", False)
      ktnr = self.get_value("KtNr.Auszugkonto")
      if ktnr is None: 
         print "WARNING: Account not found for ", auszug
         return
      self.set_value("Auszug.AUSZUG", auszug)
      self.set_value("BuchDat.AUSZUG", datum)
      self.set_value("Datum.AUSZUG", today)
      self.set_value("KtNr.AUSZUG", ktnr)
   ## set output to file instead of internal database (not yet implemented)
   # @param fhandle - filehandle for output file
   def set_output_file(self, fhandle):
      self.file = fhandle
   ## set payment through indermediate account (payment has to be split)
   def set_payment_transfer(self):
      self.transfer = self.get_special_accounts("ZTF")
   ## add default values to payment data (if specific routines fail)
   # @param data - data dictionary to be modified, will be returned
   def add_payment_data_default(self, data):
      if not "Gegenkonto" in data:
         data["Gegenkonto"] = -1
      if not "Von" in data:
         data["Von"] = "AfpFinance: data not available"
      return data
   ## flip booking, add remark
   # @param data - data dictornary to be modified and returned
   # @param bem - remark to be added
   def set_storno_values(self, data, bem = "-STORNO-"):
      #data["Betrag"] = - data["Betrag"]
      Konto = data["Konto"]
      data["Konto"] = data["Gegenkonto"]
      data["Gegenkonto"] = Konto
      data["Bem"] = data["Bem"] + " " + bem
      return data
   ## retrieve special account from database
   # @param ident - identifier of account
   def get_special_accounts(self, ident):
       return Afp_getSpecialAccount(self.get_mysql(), ident)
   ## get name of account
   # @param nr - number of account of which name is searched
   def get_account_name(self, nr):
       rows = self.get_mysql().select("Bezeichnung","KtNr = " + Afp_toString(nr),"KTNR")
       if rows: return rows[0][0]
       else: return None
   ## add tax identifier to account, due to german tax laws
   # @param konto - number of account
   # @param stkenn - identifier fo tax
   def get_tax_account(self, konto, stkenn):
      steuer = 0
      if stkenn == "UV": steuer = 300000 
      elif stkenn == "UH": steuer = 200000 
      elif stkenn == "VV": steuer = 900000 
      elif stkenn == "VH": steuer = 800000 
      return steuer + konto
   ##  add entries for adhoc discount during payment (only usable for invoice)
   # @param data - incident data where discount is given
   def data_create_skonto_accounting(self, data):
      acc = None
      if data.get_listname() == "Rechnung":
         preis = data.get_value("RechBetrag")
         zahlung = data.get_value("Zahlung")
         if zahlung < preis and zahlung >= data.get_value("ZahlBetrag"):
            kdnr = data.get_value("KundenNr.RECHNG")
            name = data.get_name(True)
            beleg =  data.get_string_value("RechNr.RECHNG")
            konto =  data.get_value("Debitor.RECHNG")
            today = self.globals.today()
            skonto = preis - zahlung
            sgkt = self.get_special_accounts("SKTO")
            sbem = "Skonto: " + name
            von = data.get_identifier()
            acc = {"Datum": today,"Konto": konto, "Gegenkonto ": sgkt,"Beleg": beleg,"Betrag": skonto,"KtName": name ,"GktName": "SKTO","KundenNr": kdnr,"Bem":  sbem,"Von": von}
      return acc
   ## add one payment entry according to input
   # @param payment - amount of payment
   # @param datum - date when  payment has benn recorded
   # @param auszug -  statement of account wher payment has benn recorded
   # @param KdNr -  number of address this payment is assigned to
   # @param Name -  name of the address this payment is assigned to
   # @param data -  incident data where financial values have to be extracted, if == None: payment is assigne to transferaccount
   # @param reverse -  accounting data has to be swapped
   def add_payment(self, payment, datum, auszug, KdNr, Name, data = None, reverse = False):
      print "AfpFinTrans.add_payment:", payment, datum, auszug, KdNr, Name, data 
      if auszug: self.set_auszug(auszug, datum)
      accdata = {}
      accdata["Datum"] = datum
      accdata["Betrag"] = payment
      accdata["Beleg"] = auszug
      accdata["KundenNr"] = KdNr
      accdata["Art"] = "Zahlung"
      accdata["Eintrag"] = self.globals.today()
      if data is None: 
         # received payment, has to be distributed
         self.set_payment_transfer()         
         accdata["Konto"] = self.get_value("KtNr.AUSZUG")
         accdata["Gegenkonto"] = self. transfer
         accdata["Bem"] = "Mehrfach (" + Name + ")"
      else:
         # distribute according to data-types
         if self.transfer: 
            accdata["Konto"] = self.transfer
            accdata["Bem"] = "Mehrfach (" + Name + "): " + data.get_name()
         else: 
            accdata["Konto"] = self.get_value("KtNr.AUSZUG")
            accdata["Bem"] = "Zahlung: " + Name
         accdata = self.add_payment_data(accdata, data)
      accdata = self.add_payment_data_default(accdata)
      if reverse: accdata = self.set_storno_values(accdata, "Auszahlung")
      sel =  self.get_selection()
      index = sel.add_data_row(True)
      sel.set_data_values(accdata, index)
      # possible Skonto has to be accounted during payment
      accdata = self.data_create_skonto_accounting(data)
      if accdata:
         index = sel.add_data_row(True)
         sel.set_data_values(accdata, index)
   ## extract payment relevant data from 'data' input
   # @param paymentdata - payment data dictionary to be modified and returned
   # @param data - incident data where relevant values have to be extracted
   def add_payment_data(self, paymentdata, data):
      # has to return the account number this payment has to be charged ("Gegenkonto"), the identifier ("Von")
      paymentdata["Von"] = data.get_identifier() 
      if data.get_listname() == "Charter":
         paymentdata = self.add_payment_data_charter(paymentdata, data)
      return paymentdata
   ## financial transaction entries are generated according to incident data given
   # @param data - incident data where entries are created from
   # @param storno - flag if incident should be cancelled
   def add_financial_transactions(self, data, storno = False):
      print "AfpFinTrans.add_financial_transactions"
      today = self.globals.today()
      accdata = self.add_financial_transaction_data(data)
      if accdata:
         sel = self.get_selection()
         for acc in accdata:
            if not "Von" in acc: acc["Von"] = data.get_identifier()
            acc["Art"] = "Intern"
            acc["Eintrag"] = today
            if storno: acc = self.set_storno_values(acc)
            index = sel.add_data_row(True)
            sel.set_data_values(acc, index)
   ## financial transaction data is delivered in a list of dictionaries from incident data \n
   # this routine splits into the different incident routines. \n
   # REMARK: as it is planned to hold the financial tarnsactions for all the different incidents central in this deck \n
   # no use is made of the object-orientated approach, but this routine is used to split into the appropriate extraction routine.
   # @param data - incident data enrties are extracted from \n
   # this routine has to return a list of the following data: \n
   #[{"Datum":   .                                 "Konto":  ,                 "Gegenkonto ":   ,            "Betrag":  ,"Beleg":  ,     "Bem":  },{}, ...] \n
   # [date where accounting gets valid, first accountnumber, second accountnumber, balance, receiptnumber, remark]
   def add_financial_transaction_data(self, data):
      print "AfpFinTrans.add_financial_transaction_data"
      if data.get_listname() == "Charter":
         accdata = self.add_transaction_data_charter(data)
      else:
         return None
      for acc in accdata:
         acc["VorgangsNr"] = 0
      return accdata
   ## shift a payment from the internal general account to the specified account
   # @param data - incident data according to which payment has to be shifted
   def add_internal_payment(self, data):
      # shifts an already received payment to another account if necessary
      print "AfpFinTrans.add_internal_payment"
      accdata = {}
      listname = data.get_listname()
      if listname == "Charter":
         accdata = self.add_internal_payment_charter(accdata, data)      
      if accdata:
         today = self.globals.today()
         accdata["Datum"] = today
         accdata["Bem"] = "Anzahlung " + listname
         accdata["Art"] = "Zahlung intern" 
         accdata["Von"] = data.get_identifier()  
         accdata["Beleg"] = "Intern"  
         accdata["Eintrag"] = today
         sel = self.get_selection()
         index = sel.add_data_row(True)
         sel.set_data_values(accdata, index) 
   ## overwritten 'store' of the AfpSelectionList, the parent 'store' is called and a common action-number spread.          
   def store(self):
      print "AfpFinTrans.store 0:",self.new, self.mainindex
      self.view()
      AfpSelectionList.store(self)
      print "AfpFinTrans.store 1:",self.new, self.mainindex 
      self.view()
      if self.new:
         self.new = False
         VNr = self.get_value("BuchungsNr")
         print "VorgangsNr:", VNr
         changed_data = {"VorgangsNr": VNr}
         for i in range(0, self.get_value_length()):
            self.set_data_values(changed_data, None, i)
         print "AfpFinTrans.store 2:",self.new, self.mainindex 
         for d in self.selections: print d,":", self.selections[d].data
         AfpSelectionList.store(self)
   ## Charter: deliver payment transaction data
   # @param paymentdata - payment data dictionary to be modified and returned
   # @param data - Charter data where relevant values have to be extracted
   def add_payment_data_charter(self, paymentdata, data):
      RNr = data.get_value("RechNr.Fahrten")
      if RNr: self.add_payment_data_rechnung(paymentdata, data)
      else: paymentdata["Gegenkonto"] = Afp_getSpecialAccount(self.get_mysql(), "MFA")
      return paymentdata   
   ## Charter: deliver financial transaction data
   # @param data - Charter data where relevant values have to be extracted
   def add_transaction_data_charter(self, data):
      print "AfpFinTrans.add_transaction_data_charter"
      accdata = []
      if data.exists_selection("RECHNG") or data.get_value("RechNr"):
         accdata = self.add_transaction_data_rechnung(data)
      return accdata
   ## Charter: deliver internal payment transaction data
   # @param paymentdata - payment data dictionary to be modified and returned
   # @param data - Charter data where relevant values have to be extracted
   def add_internal_payment_charter(self, paymentdata, data):
      print "AfpFinTrans.add_internal_payment_charter:"
      #for d in self.selections: print d,":", self.selections[d].data
      #for d in data.selections: print d,":", data.selections[d].data
      zahlung = data.get_value("Zahlung.RECHNG")
      if Afp_isEps(zahlung):
         paymentdata["Betrag"] = zahlung
         paymentdata["Konto"] = Afp_getSpecialAccount(self.get_mysql(), "MFA")
         paymentdata["KundenNr"] = data.get_value("KundenNr")        
         paymentdata = self.add_payment_data_rechnung(paymentdata, data)
      return paymentdata
   ## Rechnung (Invoice): deliver payment transaction data
   # @param paymentdata - payment data dictionary to be modified and returned
   # @param data - Rechnung data where relevant values have to be extracted
   def add_payment_data_rechnung(self, paymentdata, data):
      paymentdata["Gegenkonto"] = data.get_value("Debitor.RECHNG") 
      print "AfpFinTrans.add_payment_data_rechnung:",paymentdata
      if not paymentdata["Gegenkonto"]:
         paymentdata["Gegenkonto"]  = Afp_getIndividualAccount(self.get_mysql(), data.get_value("KundenNr"))
         print "AfpFinTrans.add_payment_data_rechnung fallback:", paymentdata
      return paymentdata 
   ## Rechnung (Invoice): deliver financial transaction data
   # @param data - Rechnung data where relevant values have to be extracted
   def add_transaction_data_rechnung(self, data):
      print "AfpFinTrans.add_transaction_data_rechnung"
      accdata = []
      datum = data.get_value("Datum.RECHNG")
      preis =  data.get_value("RechBetrag.RECHNG")
      if Afp_isEps(preis):
         von =  data.get_identifier()
         bem = "Rechnung"
         if data.get_value("Fahrt.RECHNG"):
            bem = "Charter"
            if von[:8] == "Rechnung":
               von = "Charter" + data.get_string_value("Fahrt.RECHNG")
         kdnr = data.get_value("KundenNr.RECHNG")
         name = data.get_name(True)
         bem += " " + name
         beleg =  data.get_string_value("RechNr.RECHNG")
         konto =  data.get_value("Debitor.RECHNG")
         gkonto = self.get_tax_account(data.get_value("Kontierung.RECHNG"), "U" + data.get_string_value("Ust.RECHNG"))
         gktname = self.get_account_name(data.get_value("Kontierung.RECHNG"))
         # Skonto
         acc = self.data_create_skonto_accounting(data)
         if acc: accdata.append(acc)
         # second account involved
         gkonto2 = 0
         if data.get_value("Konto2.RECHNG") and Afp_isEps(data.get_value("Preis2.RECHNG")):
            gkonto2 = data.get_value("Konto2.RECHNG")
            gkt2 = self.get_account_name(gkonto2)
            preis2 = data.get_value("Betrag2.RECHNG")
            preis -= preis2         
         acc = {"Datum": datum,"Konto": konto, "Gegenkonto": gkonto,"Beleg": beleg,"Betrag": preis,"KtName": name,"GktName": gktname,"KundenNr": kdnr,"Bem":  bem,"Von": von}
         accdata.append(acc)
         if gkonto2:
            acc = {"Datum": datum,"Konto": konto, "Gegenkonto ": gkonto2,"Beleg": beleg,"Betrag": preis,"KtName": name,"GktName": gkt2,"KundenNr": kdnr,"Bem":  bem,"Von": von}
            accdata.append(acc)
      return accdata
               