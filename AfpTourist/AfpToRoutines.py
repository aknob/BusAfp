#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpTourist.AfpToRoutines
# AfpToRoutines module provides classes and routines needed for tourist handling,\n
# no display and user interaction in this modul.
#
#   History: \n
#        15 Jan. 2016 - inital code generated - Andreas.Knoblauch@afptech.de \n

#
# This file is part of the  'Open Source' project "BusAfp" by 
#  AfpTechnologies (afptech.de)
#
#    BusAfp is a software to manage coach and travel acivities
#    Copyright© 1989 - 2016  afptech.de (Andreas Knoblauch)
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
from AfpBase import *
from AfpBase.AfpDatabase import AfpSQL
from AfpBase.AfpDatabase.AfpSQL import AfpSQLTableSelection
from AfpBase.AfpBaseRoutines import *
from AfpBase.AfpBaseAdRoutines import AfpAdresse_getListOfTable

## extract all available tourist entries for given address indenifier
# @param globals - global values to be used
# @param knr - address identifier to be used
def AfpTourist_getAnmeldListOfAdresse(globals, knr):
    rows = []
    raw_rows, name = AfpAdresse_getListOfTable(globals, knr, "ANMELD","Anmeldung,Info,Preis,AnmeldNr")
    #print "AfpTourist_getAnmeldListOfAdresse raw_row:", raw_rows, name, knr
    if raw_rows:
        for entry in raw_rows:
            ANr = entry[-1]
            Anmeld = AfpTourist(globals, ANr)
            row = Anmeld.get_value_rows("REISEN","Abfahrt,Zielort")[0]
            row += entry
            #print "AfpTourist_getAnmeldListOfAdresse row:", row
            rows.append(row)
    print "AfpTourist_getAnmeldListOfAdresse rows:", rows, name
    return rows, name  

## read all route names from table
# @param mysql - sql object to access datatable
def AfpTourist_getRouteNames(mysql):
    rows = msql.select("Name,TourNr","","TNAME")
    namen = []
    idents = []
    for row in rows:
        namen.append(row[0])
        idents.append(row[1])
    return namen, idents
        
##  get the list of indecies of tourist table,
# @param mysql - database where values are retrieved from
# @param index  -  name sort criterium initially selected
# @param datei  -  name table to be used as primary
def AfpTourist_getOrderlistOfTable(mysql, index, datei = "REISEN"):
    if datei == "ANMELD":
        keep = ["RechNr"]
        indirect = None
    else:
        keep = ["Abfahrt"]
        if index == "Anmeldung":
            keep.append("RechNr")
        else:
            keep.append("Kennung")
        keep.append("Zielort")
        indirect = ["Zielort","Abfahrt"]
    #liste = Afp_getOrderlistOfTable(mysql, datei, keep, indirect)
    if index == "Kennung":
        liste = {'Abfahrt':'date', 'Kennung':'string','RechNr':'float'}
    else:
        liste = {'Abfahrt':'date', 'Zielort':'string','RechNr':'float'}
    return liste

## baseclass for tourist handling         
class AfpTourist(AfpSelectionList):
    ## initialize AfpTourist class
    # @param globals - global values including the mysql connection - this input is mandatory
    # @param AnmeldNr - if given and sb == None, data will be retrieved this database entry
    # @param sb - if given data will  be retrieved from the actuel AfpSuperbase data
    # @param debug - flag for debug information
    # @param complete - flag if data from all tables should be retrieved durin initialisation \n
    # \n
    # either AnmeldNr or sb (superbase) has to be given for initialisation,otherwise a new, clean object is created
    def  __init__(self, globals, AnmeldNr = None, sb = None, debug = None, complete = False):
        AfpSelectionList.__init__(self, globals, "Tourist", debug)
        if debug: self.debug = debug
        else: self.debug = globals.is_debug()
        self.finance = None
        self.new = False
        self.mainindex = "AnmeldNr"
        self.mainvalue = ""
        self.spezial_bez = []
        if sb:
            self.mainvalue = sb.get_string_value("AnmeldNr.ANMELD")
            Selection = sb.gen_selection("ANMELD", "AnmeldNr", debug)
            self.selections["ANMELD"] = Selection
        else:
            if AnmeldNr:
                self.mainvalue = Afp_toString(AnmeldNr)
            else:
                self.new = True
        self.mainselection = "ANMELD"
        self.set_main_selects_entry()
        if not self.mainselection in self.selections:
            self.create_selection(self.mainselection)   
        #  self.selects[name of selection]  [tablename,, select criteria, optional: unique fieldname]
        self.selects["ADRESSE"] = [ "ADRESSE","KundenNr = KundenNr.ANMELD"] 
        self.selects["REISEN"] = [ "REISEN","FahrtNr = FahrtNr.ANMELD"] 
        self.selects["PREISE"] = [ "PREISE","Kennung = PreisNr.ANMELD"] 
        self.selects["ANMELDER"] = [ "ANMELDER","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ANMELDEX"] = [ "ANMELDEX","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ARCHIV"] = [ "ARCHIV","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["AUSGABE"] = [ "AUSGABE","Typ = Zustand.ANMELD"] 
        #self.selects["RECHNG"] = [ "RECHNG","RechNr = RechNr.ANMELD","RechNr"] 
        #self.selects["ERTRAG"] = [ "ERTRAG","FahrtNr = FahrtNr.ANMELD"] 
        #self.selects["EINSATZ"] = [ "EINSATZ","ReiseNr = FahrtNr.ANMELD"] 
        self.selects["TORT"] = [ "TORT","OrtsNr = Ab.ANMELD"] 
        if complete: self.create_selections()
        if not self.globals.skip_accounting():
            self.finance_modul = Afp_importAfpModul("Finance", self.globals)[0]
            if self.finance_modul:
                self.finance = self.finance_modul.AfpFinanceTransactions(self.globals)
        print "AfpTourist.finance:", self.finance
        if self.debug: print "AfpTourist Konstruktor, AnmeldNr:", self.mainvalue
    ## destuctor
    def __del__(self):    
        if self.debug: print "AfpTourist Destruktor"
        #AfpSelectionList.__del__(self) 
    ## decide whether payment is possible or not
    def is_payable(self):
        payable = False
        zustand = self.get_string_value("Zustand")
        if AfpTourist_isPayable(zustand): payable = True
        return payable
    ## charter will be tracked with financial transaction (accounted)
    def is_accountable(self):
        zustand = self.get_value("Zustand.FAHRTEN")
        return AfpTourist_needsTransaction(zustand)
    ## clear current SelectionList to behave as a newly created List 
    # @param KundenNr - KundenNr of newly seelected adress, == None if adress is kept
    # @param keep_flag -  flags which data should be kept while creation this copy
    # - [0] == True: address should be kept (should coincident with KundenNr == None)
    # - [1] == True: contact should be kept 
    # - [2] == True: Fahrtinfo should be kept 
    # - [3] == True: Fahrtextra should be kept 
    # - [4] == True: the rest of the data should be kept 
    def set_new(self, KundenNr, keep_flag = None):
        self.new = True
        data = {}
        keep = []
        if KundenNr:
            data["KundenNr"] = KundenNr
        else:
            data["KundenNr"] = self.get_value("KundenNr")
            keep.append("ADRESSE")
        if keep_flag:
            if keep_flag[1]: # contact kept
                data["Kontakt"] = self.get_value("Kontakt")
                data["Name"] = self.get_value("Name")
                keep.append("Kontakt")
            if keep_flag[2] and "FAHRTI" in self.selections: # Fahrtinfo kept
                keep.append("FAHRTI")
                self.selections["FAHRTI"].new = True
            if keep_flag[3] and "FAHRTEX" in self.selections: # Fahrtextra kept
                keep.append("FAHRTEX")
                self.selections["FAHRTEX"].new = True
                data["Extra"] = self.get_value("Extra") 
                data["Preis"] = self.get_value("Preis") 
                data["PersPreis"] = self.get_value("PersPreis") 
            elif keep_flag[4] and not "FAHRTEX" in self.selections: # Fahrtextra kept
                data["Preis"] = self.get_value("Preis") 
                data["PersPreis"] = self.get_value("PersPreis") 
            if keep_flag[4]: # data kept
                data["Abfahrt"] = self.get_value("Abfahrt") 
                data["Fahrtende"] = self.get_value("Fahrtende") 
                data["Abfahrtsort"] = self.get_value("Abfahrtsort") 
                data["Zielort"] = self.get_value("Zielort") 
                data["Personen"] = self.get_value("Personen") 
                data["Km"] = self.get_value("Km") 
                data["Kostenst"] = self.get_value("Kostenst") 
                data["Vorgang"] = self.get_value("Vorgang") 
                data["Ausstattung"] = self.get_value("Ausstattung") 
                data["Von"] = self.get_value("Von") 
                data["Nach"] = self.get_value("Nach") 
        data["Zustand"] = AfpTourist_getZustandList()[0]
        data["Art"] = self.get_value("Art")
        if data["Art"] is None:  data["Art"] = AfpTourist_getArtList()[0]
        if not "Von" in data: data["Von"] = "von"
        if not "Nach" in data: data["Nach"] = "nach"
        data["Datum"] = self.globals.today()
        print "AfpTourist.set_new data:", data
        print "AfpTourist.set_new keep:", keep
        self.clear_selections(keep)
        self.set_data_values(data,"FAHRTEN")
        if keep_flag:
            if keep_flag[2] or keep_flag[3]:
                self.spread_mainvalue()
        if KundenNr:
            self.create_selection("ADRESSE", False)
    ## financial transaction will be initated if the appropriate modul is installed
    # @param initial - flag for initial call of transaction (interal payment may be added)
    def execute_financial_transaction(self, initial):
        if self.finance:
            self.finance.add_financial_transactions(self)
            if initial: self.finance.add_internal_payment(self)
            self.finance.store()
    ## financial transaction will be canceled if the appropriate modul is installed
    def cancel_financial_transaction(self):
        if self.finance:
            original = AfpTourist(self.globals, self.mainvalue)
            self.finance.add_financial_transactions(original, True)
    ## a separate invoice is created and filled with the appropriate values
    def add_invoice(self):
        print "AfpTourist.add_invoice"
        invoice = AfpSQLTableSelection(self.get_mysql(), "RECHNG", self.debug, "RechNr")
        KNr = self.get_value("KundenNr")
        data = {"Datum": self.globals.today(), "KundenNr": KNr, "Name": self.get_name(True), "Fahrt": self.get_value("FahrtNr")}
        data["Debitor"] = Afp_getIndividualAccount(self.get_mysql(), KNr)
        betrag = self.get_value("Preis")
        data["Zahlbetrag"] = betrag
        betrag2 = self.extract_taxfree_portion()
        if betrag2:
            betrag -= betrag2
            data["Betrag2"] = betrag
            data["Konto2"] = Afp_getSpecialAccount(self.get_mysql(), "EMFA")
        data["RechBetrag"] = betrag
        data["Kontierung"] = Afp_getSpecialAccount(self.get_mysql(), "EMF")
        data["Zustand"] = "offen"
        data["Wofuer"] = "Mietfahrt Nr " + self.get_string_value("FahrtNr") + " am " + self.get_string_value("Abfahrt") + " nach " + self.get_string_value("Zielort")
        if self.get_value("ZahlDat"):
            data["Zahlung"] = self.get_value("Zahlung")
            data["ZahlDat"] = self.get_value("ZahlDat")
            if data["Zahlung"] >= betrag: data["Zustand"] = "bezahlt"
        invoice.new_data()
        invoice.set_data_values(data)
        self.selections["RECHNG"] = invoice
    ## routine to hold separate invoice syncron to the actuel charter values
    def syncronise_invoice(self):
        print "AfpTourist.syncronise_invoice"
        betrag = self.get_value("Preis")
        data = {}
        data["Zahlbetrag"] = betrag
        betrag2 = self.extract_taxfree_portion()
        if betrag2:
            betrag -= betrag2
            data["Betrag2"] = betrag
        data["RechBetrag"] = betrag
        if self.get_value("ZahlDat"):
            data["Zahlung"] = self.get_value("Zahlung")
            data["ZahlDat"] = self.get_value("ZahlDat")
        #print "AfpTourist.syncronise_invoice data:", data
        self.set_data_values(data, "RECHNG")
    ## one line to hold all relevant values of charter, to be displayed 
    def line(self):
        zeile =  self.get_string_value("SortNr").rjust(8) + "  "  + self.get_string_value("Datum") + " " +  self.get_string_value("Zustand") + " " + self.get_string_value("Art") + " " + self.get_string_value("Zielort")  
        zeile += " " + self.get_string_value("Preis").rjust(10) + " " +self.get_string_value("Zahlung").rjust(10) 
        return zeile
    ## internal routine to set the appropriate agency name
    def set_agent_name(self):
        #name = self.get_name(False,"Kontakt") + " " + self.get_string_value("KontaktNr")
        name = self.get_name(False,"Agent")
        self.set_value("AgentName",name)
    ## set all necessary values to keep track of the payments
    # @param payment - amount that has been payed
    # @param datum - date when last payment has been made
    def set_payment_values(self, payment, datum):
        AfpSelectionList.set_payment_values(self, payment, datum)
        if self.get_value("RechNr"):
            self.set_value("Zahlung.RECHNG", payment)
            self.set_value("ZahlDat.RECHNG", datum)
    ## return specific identification string to be used in dialogs \n
    # - overwritten from AfpSelectionList
    def get_identification_string(self):
        return "Mietfahrt am "  +  self.get_string_value("Abfahrt") + " nach " + self.get_string_value("Zielort")
        
## baseclass for tour handling         
class AfpTour(AfpSelectionList):
    ## initialize AfpTour class
    # @param globals - global values including the mysql connection - this input is mandatory
    # @param FahrtNr - if given and sb == None, data will be retrieved this database entry
    # @param sb - if given data will  be retrieved from the actuel AfpSuperbase data
    # @param debug - flag for debug information
    # @param complete - flag if data from all tables should be retrieved durin initialisation \n
    # \n
    # either AnmeldNr or sb (superbase) has to be given for initialisation,otherwise a new, clean object is created
    def  __init__(self, globals, FahrtNr = None, sb = None, debug = None, complete = False):
        AfpSelectionList.__init__(self, globals, "Tour", debug)
        if debug: self.debug = debug
        else: self.debug = globals.is_debug()
        self.new = False
        self.mainindex = "FahrtNr"
        self.mainvalue = ""
        self.spezial_bez = []
        if sb:
            self.mainvalue = sb.get_string_value("FahrtNr.REISEN")
            Selection = sb.gen_selection("REISEN", "FahrtNr", debug)
            self.selections["REISEN"] = Selection
        else:
            if FahrtNr:
                self.mainvalue = Afp_toString(FahrtNr)
            else:
                self.new = True
        self.mainselection = "REISEN"
        self.set_main_selects_entry()
        if not self.mainselection in self.selections:
            self.create_selection(self.mainselection)   
        #  self.selects[name of selection]  [tablename,, select criteria, optional: unique fieldname]
        self.selects["ANMELD"] = [ "ANMELD","FahrtNr = FahrtNr.REISEN"] 
        self.selects["PREISE"] = [ "PREISE","Kennung = PreisNr.ANMELD"] 
        self.selects["ANMELDER"] = [ "ANMELDER","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ANMELDEX"] = [ "ANMELDEX","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ARCHIV"] = [ "ARCHIV","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["AUSGABE"] = [ "AUSGABE","Typ = Zustand.ANMELD"] 
        #self.selects["RECHNG"] = [ "RECHNG","RechNr = RechNr.ANMELD","RechNr"] 
        self.selects["ERTRAG"] = [ "ERTRAG","FahrtNr = FahrtNr.REISEN"] 
        self.selects["EINSATZ"] = [ "EINSATZ","ReiseNr = FahrtNr.REISEN"] 
        self.selects["TNAME"] = [ "TNAME","TourNr = Route.REISEN"] 
        if complete: self.create_selections()
        if self.debug: print "AfpTour Konstruktor, FahrtNr:", self.mainvalue
    ## destuctor
    def __del__(self):    
        if self.debug: print "AfpTour Destruktor"
        #AfpSelectionList.__del__(self) 
    ## clear current SelectionList to behave as a newly created List 
    # @param KundenNr - KundenNr of newly seelected adress, == None if adress is kept
    # @param keep_flag -  flags which data should be kept while creation this copy
    # - [0] == True: address should be kept (should coincident with KundenNr == None)
    # - [1] == True: contact should be kept 
    # - [2] == True: Fahrtinfo should be kept 
    # - [3] == True: Fahrtextra should be kept 
    # - [4] == True: the rest of the data should be kept 
    def set_new(self, KundenNr, keep_flag = None):
        self.new = True
        data = {}
        keep = []
        if KundenNr:
            data["KundenNr"] = KundenNr
        else:
            data["KundenNr"] = self.get_value("KundenNr")
            keep.append("ADRESSE")
        if keep_flag:
            if keep_flag[1]: # contact kept
                data["Kontakt"] = self.get_value("Kontakt")
                data["Name"] = self.get_value("Name")
                keep.append("Kontakt")
            if keep_flag[2] and "FAHRTI" in self.selections: # Fahrtinfo kept
                keep.append("FAHRTI")
                self.selections["FAHRTI"].new = True
            if keep_flag[3] and "FAHRTEX" in self.selections: # Fahrtextra kept
                keep.append("FAHRTEX")
                self.selections["FAHRTEX"].new = True
                data["Extra"] = self.get_value("Extra") 
                data["Preis"] = self.get_value("Preis") 
                data["PersPreis"] = self.get_value("PersPreis") 
            elif keep_flag[4] and not "FAHRTEX" in self.selections: # Fahrtextra kept
                data["Preis"] = self.get_value("Preis") 
                data["PersPreis"] = self.get_value("PersPreis") 
            if keep_flag[4]: # data kept
                data["Abfahrt"] = self.get_value("Abfahrt") 
                data["Fahrtende"] = self.get_value("Fahrtende") 
                data["Abfahrtsort"] = self.get_value("Abfahrtsort") 
                data["Zielort"] = self.get_value("Zielort") 
                data["Personen"] = self.get_value("Personen") 
                data["Km"] = self.get_value("Km") 
                data["Kostenst"] = self.get_value("Kostenst") 
                data["Vorgang"] = self.get_value("Vorgang") 
                data["Ausstattung"] = self.get_value("Ausstattung") 
                data["Von"] = self.get_value("Von") 
                data["Nach"] = self.get_value("Nach") 
        data["Zustand"] = AfpTourist_getZustandList()[0]
        data["Art"] = self.get_value("Art")
        if data["Art"] is None:  data["Art"] = AfpTourist_getArtList()[0]
        if not "Von" in data: data["Von"] = "von"
        if not "Nach" in data: data["Nach"] = "nach"
        data["Datum"] = self.globals.today()
        print "AfpTourist.set_new data:", data
        print "AfpTourist.set_new keep:", keep
        self.clear_selections(keep)
        self.set_data_values(data,"FAHRTEN")
        if keep_flag:
            if keep_flag[2] or keep_flag[3]:
                self.spread_mainvalue()
        if KundenNr:
            self.create_selection("ADRESSE", False)
    ## one line to hold all relevant values of charter, to be displayed 
    def line(self):
        zeile =  self.get_string_value("SortNr").rjust(8) + "  "  + self.get_string_value("Datum") + " " +  self.get_string_value("Zustand") + " " + self.get_string_value("Art") + " " + self.get_string_value("Zielort")  
        zeile += " " + self.get_string_value("Preis").rjust(10) + " " +self.get_string_value("Zahlung").rjust(10) 
        return zeile
    ## internal routine to set the appropriate agency name
    def set_agent_name(self):
        #name = self.get_name(False,"Kontakt") + " " + self.get_string_value("KontaktNr")
        name = self.get_name(False,"Agent")
        self.set_value("AgentName",name)
    ## return specific identification string to be used in dialogs \n
    # - overwritten from AfpSelectionList
    def get_identification_string(self):
        return "Mietfahrt am "  +  self.get_string_value("Abfahrt") + " nach " + self.get_string_value("Zielort")


