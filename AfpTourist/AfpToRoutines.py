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

## returns all possible entries for kind of tours
def AfpTourist_possibleTourKinds():
    #return ["Indi","Eigen","Fremd"]
    return ["Eigen","Fremd"]
## available 'Zustand' values are set here \n
# This is the definition routine for all available 'Zustand' values
def AfpTourist_getZustandList():
    return ["Reservierung","Anmeldung"]
## return 'Zustand' values where financial transaction are needed \n
# This is the definition routine for the above 'Zustand' values
def AfpTourist_getTransactionList():
    return ["Anmeldung"]
    
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
    rows = mysql.select("Name,TourNr","","TNAME","Name")
    namen = []
    idents = []
    for row in rows:
        namen.append(row[0])
        idents.append(row[1])
    return namen, idents
## read all route names from table
# @param mysql - sql object to access datatable
# @param route - identification number of route where locations should be extracted
def AfpTourist_getLocations(mysql, route):
    knr = 100*route
    select = "KennNr >= " + Afp_toString(knr) + " AND KennNr < "  + Afp_toString(knr + 100)
    rows = mysql.select("KennNr",select,"TROUTE")
    namen = []
    kennungen = []
    for row in rows:
        select = "OrtsNr = " + Afp_toString(row[0])
        orte = mysql.select("Ort,Kennung",select,"TORT")
        namen.append(orte[0][0])
        idents.append(orte[0][1])
    return namen, kennungen
    
## check if vehicle is needed for this route
# @param mysql - sql object to access datatable
# @param route - identifier of route
def AfpTourist_checkVehicle(mysql, route):
    bus = None
    if route:
        select = "TourNr = " + Afp_toString(route)
        rows = mysql.select("OhneBus",select,"TNAME")
        if rows:
            #print "AfpTourist_checkVehicle", rows
            if Afp_fromString(rows[0][0]): 
                # OhneBus == 1
                bus = False
            else:
                # OhneBus = 0
                bus = True
    return bus
        
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
            if  sb.get_value("FahrtNr.REISEN") == sb.get_value("FahrtNr.ANMELD"):
                self.mainvalue = sb.get_string_value("AnmeldNr.ANMELD")
                Selection = sb.gen_selection("ANMELD", "AnmeldNr", debug)
            else:
                self.new = True
                Selection = AfpSQLTableSelection(self.mysql, "ANMELD", self.debug, "AnmeldNr")
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
        self.selects["PREISE"] = [ "PREISE","FahrtNr = FahrtNr.ANMELD"] 
        self.selects["TORT"] = [ "TORT","OrtsNr = Ab.ANMELD"] 
        self.selects["ANMELDER"] = [ "ANMELDER","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ANMELDEX"] = [ "ANMELDEX","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["ARCHIV"] = [ "ARCHIV","AnmeldNr = AnmeldNr.ANMELD"] 
        self.selects["AUSGABE"] = [ "AUSGABE","Typ = Zustand.ANMELD"] 
        self.selects["RechNr"] = [ "ANMELD","RechNr = RechNr.ANMELD"] 
        self.selects["Agent"] = [ "ADRESSE","KundenNr = AgentNr.ANMELD"] 
        self.selects["ExtraPreis"] = [ "PREISE","FahrtNr = 0"] 
        self.selects["Preis"] = [ "PREISE","Kennung = PreisNr.ANMELD"] 
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
    # @param FahrtNr - identifier of tour == None if tour is kept
    # @param KundenNr - KundenNr of newly selected adress, == None if adress is kept
    # @param keep_flag -  flags which data should be kept while creation this copy
    # - [0] == True: agent should be kept 
    # - [1] == True: prices and Anmeldex should be kept 
    # - [2] == True: the rest of the data should be kept 
    def set_new(self, FahrtNr, KundenNr, keep_flag = None):
        self.new = True
        data = {}
        keep = []
        if keep_flag == True:
            keep_flag = [True, True, True]
        if FahrtNr:
            data["FahrtNr"] = FahrtNr
        else:
            data["FahrtNr"] = self.get_value("FahrtNr.REISEN")
            keep.append("REISEN")
            keep.append("PREISE")
        if KundenNr:
            data["KundenNr"] = KundenNr
        else:
            data["KundenNr"] = self.get_value("KundenNr")
            keep.append("ADRESSE")
        if keep_flag:
            if keep_flag[0]: # agent kept
                data["AgentNr"] = self.get_value("AgentNr")
                data["AgentName"] = self.get_value("AgentName")
                keep.append("Agent")
            if keep_flag[1] and "ANMELDEX" in self.selections: # Anmeldex kept
                keep.append("ANMELDEX")
                self.selections["ANMELDEX"].new = True
                data["Extra"] = self.get_value("Extra") 
                data["PreisNr"] = self.get_value("PreisNr") 
                data["Preis"] = self.get_value("Preis") 
                data["Transfer"] = self.get_value("Transfer") 
                data["ProvPreis"] = self.get_value("ProvPreis") 
            if keep_flag[2]: # data kept
                data["Ab"] = self.get_value("Ab") 
                data["Bem"] = self.get_value("Bem") 
                data["Info"] = self.get_value("Info") 
                data["ExText"] = self.get_value("ExText") 
                data["Zustand"] = self.get_value("Zustand") 
                data["RechNr"] = self.get_value("RechNr") 
        data["Zustand"] = AfpTourist_getTransactionList()[0]
        data["Anmeldung"] = self.globals.today()
        print "AfpTourist.set_new data:", data
        print "AfpTourist.set_new keep:", keep
        self.clear_selections(keep)
        self.set_data_values(data,"ANMELD")
        if keep_flag:
            if keep_flag[1]:
                self.spread_mainvalue()
        if FahrtNr:
            self.create_selection("REISEN", False)
            self.create_selection("PREISE", False)
        if KundenNr:
            self.create_selection("ADRESSE", False)
        if not self.get_value("Preis"):
            self.set_value("Preis", self.get_value("Preis.PREISE"))
            self.set_value("PreisNr", self.get_value("Kennung.PREISE"))
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
    # either AnmeldNr or sb (superbase) has to be given for initialisation, otherwise a new, clean object is created
    def  __init__(self, globals, FahrtNr = None, sb = None, debug = None, complete = False):
        AfpSelectionList.__init__(self, globals, "Tour", debug)
        if debug: self.debug = debug
        else: self.debug = globals.is_debug()
        self.new = False
        self.mainindex = "FahrtNr"
        self.mainvalue = ""
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
        self.selects["ANMELD"] = [ "ANMELD","FahrtNr = FahrtNr.REISEN","AnmeldNr"] 
        self.selects["PREISE"] = [ "PREISE","FahrtNr = FahrtNr.REISEN"] 
        self.selects["ERTRAG"] = [ "ERTRAG","FahrtNr = FahrtNr.REISEN"] 
        self.selects["EINSATZ"] = [ "EINSATZ","ReiseNr = FahrtNr.REISEN","EinsatzNr"] 
        self.selects["TNAME"] = [ "TNAME","TourNr = Route.REISEN","TourNr"] 
        self.selects["Agent"] = [ "ADRESSE","KundenNr = AgentNr.REISEN"] 
        if complete: self.create_selections()
        if self.debug: print "AfpTour Konstruktor, FahrtNr:", self.mainvalue
    ## destuctor
    def __del__(self):    
        if self.debug: print "AfpTour Destruktor"
    ## clear current SelectionList to behave as a newly created List 
    # @param copy -  flag if a copy should be created or flags which data should be kept during creation of a copy
    # - True: a complete copy is created
    # - [0] == True: dates should be kept 
    # - [1] == True: agent or transfer route should be kept 
    # - [2] == True: prices should be kept 
    # - [3] == True: internal text should be kept 
    # - the rest of the data is kept if copy != [flag, flag, flag]
    def set_new(self, copy = None):
        self.new = True
        data = {}
        keep = []
        if copy == True:
            keep_flag = [False, True, True, False]
        else:
            keep_flag = copy
        if keep_flag:
            if keep_flag[0]: # dates kept
                data["Abfahrt"] = self.get_value("Abfahrt") 
                data["Fahrtende"] = self.get_value("Fahrtende") 
                data["ErloesKt"] = self.get_value("ErloesKt")
            if keep_flag[1]: # agent, transfer route kept
                data["AgentNr"] = self.get_value("AgentNr")
                data["Kreditor"] = self.get_value("Kreditor")
                data["Debitor"] = self.get_value("Debitor")
                data["AgentName"] = self.get_value("AgentName")
                data["Route"] = self.get_value("Route")
                keep.append("TNAME")
            if keep_flag[2] and "PREISE" in self.selections: # prices kept
                keep.append("PREISE")
                self.selections["PREISE"].new = True
                self.selections["PREISE"].spread_value("FahrtNr", None)
                self.selections["PREISE"].spread_value("Kennung", None)
            if keep_flag[3]: # internal text kept
                data["IntText"] = self.get_value("IntText")
            data["Art"] = self.get_value("Art")
            data["Kostenst"] = self.get_value("Kostenst") 
            data["Zielort"] = self.get_value("Zielort") 
            data["Personen"] = self.get_value("Personen") 
            data["Bem"] = self.get_value("Bem")
        data["RechNr"] = 0
        data["Anmeldungen"] = 0
        print "AfpTour.set_new data:", data
        print "AfpTour.set_new keep:", keep
        self.clear_selections(keep)
        self.set_data_values(data,"REISEN")
    ## one line to hold all relevant values of this tour, to be displayed 
    def line(self):
        zeile =  self.get_string_value("Kennung").rjust(8) + "  "  + self.get_string_value("Art") + " " +  self.get_string_value("AgentName") + " " + self.get_string_value("Abfahrt") + " " + self.get_string_value("Zielort")  
        return zeile
    ## internal routine to set the appropriate agency name
    def set_agent_name(self):
        #name = self.get_name(False,"Kontakt") + " " + self.get_string_value("KontaktNr")
        name = self.get_name(False,"Agent")
        self.set_value("AgentName",name)
    ## return specific identification string to be used in dialogs \n
    # - overwritten from AfpSelectionList
    def get_identification_string(self):
        return "Reise am "  +  self.get_string_value("Abfahrt") + " nach " + self.get_string_value("Zielort")

## baseclass for departure route handling  \n
# not yet implemented completely, actually only used to retrieve route data!
class AfpToRoute(AfpSelectionList):
    ## initialize AfpToRoute class
    # @param globals - global values including the mysql connection - this input is mandatory
    # @param RouteNr - if given and sb == None, data will be retrieved this database entry
    # @param sb - if given data will  be retrieved from the actuel AfpSuperbase data
    # @param debug - flag for debug information
    # @param complete - flag if data from all tables should be retrieved durin initialisation \n
    # \n
    # either RouteNr or sb (superbase) has to be given for initialisation, otherwise a new, clean object is created
    def  __init__(self, globals, RouteNr = None, sb = None, debug = None, complete = False):
        AfpSelectionList.__init__(self, globals, "Route", debug)
        if debug: self.debug = debug
        else: self.debug = globals.is_debug()
        self.new = False
        self.mainindex = "TourNr"
        self.mainvalue = ""
        self.kennnr = None
        self.feldnamen_route = None
        self.feldnamen_orte = None
        self.spezial_orte = []
        self.free_text = " - anderen Ort auswählen - ".decode("UTF-8")
        self.new_text = " - neuen Ort eingeben - "
        self.raste_text = "Raststätten".decode("UTF-8")
        self.new_location = None
        self.new_route_index = None
        if sb:
            self.mainvalue = sb.get_string_value("TourNr.TNAME")
            Selection = sb.gen_selection("TNAME", "TourNr", debug)
            self.selections["TNAME"] = Selection
        else:
            if RouteNr:
                self.mainvalue = Afp_toString(RouteNr)
            else:
                self.new = True
        if self.mainvalue:
            self.kennnr = 1000*Afp_fromString(self.mainvalue)
        self.mainselection = "TNAME"
        self.set_main_selects_entry()
        if not self.mainselection in self.selections:
            self.create_selection(self.mainselection)   
        #  self.selects[name of selection]  [tablename,, select criteria, optional: unique fieldname]
        self.selects["Route"] = [] 
        self.selects["Orte"] = [] 
        if complete: self.create_selections()
        if self.debug: print "AfpToRoute Konstruktor, TourNr:", self.mainvalue
    ## destuctor
    def __del__(self):    
        if self.debug: print "AfpToRoute Destruktor"
        #AfpSelectionList.__del__(self) 
    ## special selection (overwritten from AfpSelectionList) \n
    # to handle the selection 'Orte'  which holds all attached location data of all departure points
    # @param selname - name of selection (in our case 'Orte' is implemented)
    # @param new - flag if a new empty list has to be created
    def spezial_selection(self, selname, new = False):
        LocSelection = None
        #print "AfpToRoute.sepzial_selection:", selname, new
        if selname == "Route":
            if new:
                 LocSelection = AfpSQLTableSelection(self.mysql, "TROUTE", self.debug) 
                 LocSelection.new_data()
            else: 
                LocSelection = AfpSQLTableSelection(self.mysql, "TROUTE", self.debug) 
                select = "KennNr >= " + Afp_toString(self.kennnr) + " AND KennNr < " + Afp_toString(self.kennnr + 1000)
                LocSelection.load_data(select)
            self.feldnamen_route = LocSelection.get_feldnamen()
        elif selname == "Orte":
            if new:
                 LocSelection = AfpSQLTableSelection(self.mysql, "TORT", self.debug) 
                 LocSelection.new_data()
            else: 
                LocSelection = AfpSQLTableSelection(self.mysql, "TORT", self.debug) 
                data = []
                kenns = self.get_selection("Route").get_values("KennNr")
                for ken in kenns:
                    ort = ken[0] - int(ken[0]/1000)*1000
                    row = self.mysql.select("*","OrtsNr = " + Afp_toString(ort), "TORT")
                    if row: 
                        #print  "AfpToRoute.sepzial_selection row:", ort, row
                        data.append(row[0])
                        self.spezial_orte.append(ort)
                    LocSelection.set_data(data)
            self.feldnamen_orte = LocSelection.get_feldnamen()
        return LocSelection
    ## special save (overwritten from AfpSelectionList) \n
    # store the special selection 'Bez'
    # @param selname - name of selection (in our case 'Route' is implemented)
    def spezial_save(self, selname):
        if selname == "Route": 
            route = self.get_selection("Route")
            if route.has_changed():
                route.store()
        elif selname == "Orte":
            if self.new_location:
                if self.new_location.get_value("OrtsNr") is None:
                    self.new_location.store()
                    if not self.new_route_index is None:
                        ortsnr = self.new_location.get_value("OrtsNr")
                        self.get_selection("Route").set_value("KennNr", self.gen_ident(ortsnr), self.new_route_index)
    ## retrieve spezial text
    # @param  typ - typ of text to be retrieved
    def get_spezial_text(self, typ = None):
        if typ is None or typ == "new":
            text = self.new_text
        elif typ == "free":
            text = self.free_text
        elif typ == "raste":
            text = self.raste_text
        else:
             text = None
        return text
    ## look if locations with given 'Kennung' are available
    # @param ken - if given only location having this 'Kennung' are selected (used for rest-point 'RA')
    def location_available(self, ken = None):
        if ken:
            available = False
            rows = self.get_selection("Orte").get_values("Kennung")
            for row in rows:
                if ken in row: available = True
            return available
        else:
            return self.get_selection("Orte").get_data_length() >= 1
    ## get all locations referred by route sorted alphabethically
    # @param typ -  see get_location_list
    # @param add - see get_location_list
    def get_sorted_location_list(self, typ = None, add = False):
        values, idents = self.get_location_list(typ, add)
        return Afp_sortSimultan(values, idents)    
    ## get all locations referred by route
    # @param typ -  the following locations are delivered:
    # - typ = None: all route locations 
    # - typ = 'routeOnlyRaste': all route rest-points
    # - typ = 'routeNoRaste': all route locations without rest-points, 
    # one common 'Raststätten' entry for the key -10, if a rest-point is available in this route
    # - typ = 'all': all locations in the database
    # - typ = 'allNoRoute': all locations in the database, which do not belong to this route
    # @param add - will add additonal text output list
    # - typ = 'routeNoRaste': text for free location selection for key -12
    # - typ = 'all...': text for new location entry for key -11
    def get_location_list(self, typ = None, add = False):
        if typ is None:
            ortsdict = self.get_all_locations()
        elif typ == "routeOnlyRaste":
            ortsdict = self.get_all_locations('RA') 
        elif typ == "routeNoRaste":
            ortsdict = self.get_all_locations('RA', True) 
            if self.location_available('RA'): 
                ortsdict[-10] = self.raste_text
            if add: 
                ortsdict[-12] = self.free_text
        elif typ == "all":
            ortsdict = self.get_possible_locations(True)
            if add: 
                ortsdict[-11] = self.new_text
        elif typ == "allNoRoute":
            ortsdict = self.get_possible_locations()
            if add: 
                ortsdict[-11] = self.new_text
                #ortsdict[0] = self.new_text
        return ortsdict.values(), ortsdict.keys()
    ## get all possible locations 
    # @param all - if given and true, all locations are extraced directly, 
    # otherwise only locations not in route are returned
    def get_possible_locations(self, all = None):
        rows = self.mysql.select("OrtsNr,Ort,Kennung", None, "TORT")
        orte = {}
        for row in rows:
            if row[1] and (all or not row[0] in self.spezial_orte):
                orte[row[0]] = Afp_toString(row[1]) + " [" + Afp_toString(row[2]) + "]"
        return orte
   ## get all locations referred by route
    # @param ken - if given only location having this 'Kennung' are selected (used for rest-point 'RA')
    # @param rev - if given the selection above is reversed (only locations without this 'Kennung' are selected)
    def get_all_locations(self, ken = None, rev = None):
        rows = self.get_selection("Orte").get_values("OrtsNr,Ort,Kennung")
        orte = {}
        #print "AfpToRoute.get_all_locations:", rows
        for row in rows:
            if ken is None or (row[2] == ken and not rev) or (rev and row[2] != ken):
                orte[row[0]] = Afp_toString(row[1]) + " [" + Afp_toString(row[2]) + "]"
        return orte
    ## get location data
    # @param ortsnr - identifier of departure point
    # @param index - if ortsnr == None and given, index in location list
    def get_location_data(self, ortsnr, index = None):
        row = None
        if ortsnr and ortsnr in self.spezial_orte:
            index = self.spezial_orte.index(ortsnr)
        if not index is None:
            row_route = self.get_selection("Route").get_values(None, index)[0]
            row_ort = self.get_selection("Orte").get_values(None, index)[0]
            row =  row_ort + row_route
        else:
            row = self.mysql.select("*","OrtsNr = " + Afp_toString(ortsnr), "TORT")[0]
        return row
    ## set location data
    # @param changed_data - dictionary holding data to be stored
    # @param ortsnr - if given, identifier of departure point
    # @param index - if ortsnr == None and given, index in location list \n
    #  if ortsnr and index is None a new row is added
    def set_location_data(self, changed_data, ortsnr = None, index = None):
        route = self.get_selection("Route")
        orte = self.get_selection("Orte")
        if ortsnr and ortsnr in self.spezial_orte:
            index = self.spezial_orte.index(ortsnr)
        elif index is None:
            add = True
            index = orte.get_data_length()
        for data in changed_data:
            if data in self.feldnamen_route:
                route.set_value(data, changed_data[data], index)
            elif data in self.feldnamen_orte:
                orte.set_value(data, changed_data[data], index)
    ## generate rout identifier ("Kennung")
    # @param ortsnr - identifier of location
    def gen_ident(self, ortsnr):
        ken = 1000*self.get_value("TourNr") + ortsnr
        return ken
    ## add a location to this route
    # @param ortsnr - identfier of location to be added
    # @param time - if given, start time in route relativ to starting point of route (float)
    # @param preis - if given, additional price for departure at that location
    def add_location_to_route(self, ortsnr, time = None, preis = None):
        if ortsnr is None:
            changed_data = {"Zeit":time, "Preis":preis, "OrtsNr": -1} 
            self.new_route_index = len(self.spezial_orte)
        else:
            changed_data = {}
            if not ortsnr in self.spezial_orte:
                row = self.mysql.select("*","OrtsNr = " + Afp_toString(ortsnr), "TORT")[0]
                changed_data = {"OrtsNr":row[0], "Ort":row[1], "Kennung":row[2]}
            else:
                changed_data = {}
            changed_data["KennNr"] = self.gen_ident(ortsnr)
            changed_data["Zeit"] = time
            changed_data["Preis"] = preis 
        self.set_location_data(changed_data, ortsnr)
        print "AfpToRoute.add_location_to_route:", ortsnr, time, preis
    ## add location without adding route entry
    # @param ort - name of location
    # @param ken - short name of location ('Kennung')
    def add_new_location(self, ort, ken):
        changed_data = {"Ort":ort, "Kennung":ken} 
        #self.new_location_data = changed_data
        if self.new_location is None:
            self.new_location = AfpSQLTableSelection(self.mysql, "TORT", self.debug, "OrtsNr", self.feldnamen_orte)
            self.new_location.new_data(False, True)
        self.new_location.set_data_values(changed_data)
        print "AfpToRoute.add_new_location:", ort, ken
    ## add the identification number to the new location data
    # @param ortsnr - identification number
    def add_new_location_nr(self, ortsnr):
        if self.new_location:
            self_new_loacation.set_value("OrtsNr", ortsnr)
        if not self.new_route_index is None:
            self.get_selection("Route").set_value("KennNr", self.gen_ident(ortsnr), self.new_route_index)
    ## add location and add it to route
    # @param ort - name of location
    # @param ken - short name of location ('Kennung')
    # @param time - if given, start time in route relativ to starting point of route (float)
    # @param preis - if given, additional price for departure at that location
    def add_new_route_location(self, ort, ken, time = None, preis = None):
        self.add_new_location(ort, ken)
        self.add_location_to_route(None, time, preis)
        print "AfpToRoute.add_new_route_location"
                

