#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseFiDialog
# AfpBaseFiDialog module provides the dialogs and appropriate loader routines needed for finance handling, \n
# payment userinteraction is performed here. \n
#
#   History: \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        14 Feb. 2014 - inital code generated - Andreas.Knoblauch@afptech.de

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

import wx
import wx.grid

import AfpDatabase
from AfpDatabase import AfpSuperbase
import AfpBaseRoutines
from AfpBaseRoutines import *
import AfpBaseDialog
from AfpBaseDialog import *
import AfpBaseFiRoutines
from AfpBaseFiRoutines import *

## display and manipulation of payments
class AfpDialog_DiFiZahl(AfpDialog):
    ## initialise dialog
    def __init__(self, *args, **kw):
        AfpDialog.__init__(self,None, -1, "")
        self.do_store = True
        self.SetSize((570,400))
        self.SetTitle("Zahlung")

    ## initialise graphic elements
    def InitWx(self):
        panel = wx.Panel(self, -1)
    #FOUND: DialogFrame "Von_Zahlung", conversion not implemented due to lack of syntax analysis!
        self.label_Vorname = wx.StaticText(panel, -1, label="Vorname.Adresse", pos=(26,32), size=(200,20), name="Vorname")
        self.labelmap["Vorname"] = "Vorname.ADRESSE"
        self.label_Name = wx.StaticText(panel, -1, label="Name.Adresse", pos=(26,54), size=(200,20), name="Name")
        self.labelmap["Name"] = "Name.ADRESSE"
        self.label_Strasse = wx.StaticText(panel, -1, label="Strasse.Adresse", pos=(26,76), size=(200,20), name="Strasse")
        self.labelmap["Strasse"] = "Strasse.ADRESSE"
        self.label_Plz = wx.StaticText(panel, -1, label="Plz.Adresse", pos=(26,98), size=(48,20), name="Plz")
        self.labelmap["Plz"] = "Plz.ADRESSE"
        self.label_Ort = wx.StaticText(panel, -1, label="Ort.Adresse", pos=(70,98), size=(200,20), name="Ort")
        self.labelmap["Ort"] = "Ort.ADRESSE"
        self.label_T_Bet_Zahlung = wx.StaticText(panel, -1, label="zu zahlen:", pos=(330,10), size=(110,20), name="T_Bet_Zahlung")
        self.label_Gesamt = wx.StaticText(panel, -1, label="Betrag_Zahlung$", pos=(460,10), size=(84,20), name="Gesamt")
        self.label_T_Anz_Zahlung = wx.StaticText(panel, -1, label="bereits bezahlt:", pos=(310,32), size=(130,20), name="T_Anz_Zahlung")
        self.label_Anzahlung = wx.StaticText(panel, -1, label="Anz_Zahlung$", pos=(460,32), size=(84,20), name="Anzahlung")
        self.label_TGut = wx.StaticText(panel, -1, label="Gutschrift:", pos=(310,54), size=(130,16), name="TGut")
        self.label_Gut = wx.StaticText(panel, -1, label="", pos=(460,54), size=(84,18), name="Gut")
        self.label_T_Zahl_Zahlung = wx.StaticText(panel, -1, label="&Betrag:", pos=(460,82), size=(84,20), name="T_Zahl_Zahlung")
        self.text_Zahlung = wx.TextCtrl(panel, -1, value="", pos=(460,102), size=(84,24), style=0, name="Zahlung")
        self.text_Zahlung.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_T_Aus_Zahlung = wx.StaticText(panel, -1, label="Aus&zug:", pos=(330,82), size=(110,20), name="T_Aus_Zahlung")
        self.text_Auszug = wx.TextCtrl(panel, -1, value="", pos=(330,102), size=(110,24), style=0, name="Auszug")
        self.text_Auszug.Bind(wx.EVT_KILL_FOCUS, self.On_Zahlung_Auszug)
    #FOUND: DialogFrame "Ausw_Zahlung", conversion not implemented due to lack of syntax analysis!
        self.button_Verbind = wx.Button(panel, -1, label="&Verbindl.", pos=(20,160), size=(92,34), name="Verbind")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Verb, self.button_Verbind)
        self.button_Verbind.Enable(False)
        self.label_TRueck = wx.StaticText(panel, -1, label="Rueck:", pos=(120,168), size=(40,16), name="TRueck")
        self.button_Anmeld_Zahlung = wx.Button(panel, -1, label="&Anmeldung", pos=(20,160), size=(92,34), name="Anmeld_Zahlung")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Anmeld, self.button_Anmeld_Zahlung)
        self.button_Anmeld_Zahlung.Enable(False)
        self.button_Storno_Anmeld = wx.Button(panel, -1, label="&Stornierung", pos=(120,160), size=(92,34), name="Storno_Anmeld")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Storno, self.button_Storno_Anmeld)
        self.button_Storno_Anmeld.Enable(False)
        self.button_Miet_Zahlung = wx.Button(panel, -1, label="&Mietfahrt", pos=(220,160), size=(92,34), name="Miet_Zahlung")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Miet, self.button_Miet_Zahlung)
        self.button_Rech_Zahlung = wx.Button(panel, -1, label="&Rechnung", pos=(320,160), size=(92,34), name="Rech_Zahlung")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Rech, self.button_Rech_Zahlung)
        #self.button_Rech_Zahlung.Enable(False)
        self.list_Zahlungen = wx.ListBox(panel, -1, pos=(22,200), size=(530,100), name="Zahlungen")
        self.listmap.append("Zahlungen")
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Zahlung_Reihe, self.list_Zahlungen)
        self.button_ZListe_Zahlung = wx.Button(panel, -1, label="&Liste", pos=(14,320), size=(90,44), name="ZListe_Zahlung")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Liste, self.button_ZListe_Zahlung)
        self.button_Manuell = wx.Button(panel, -1, label="Ma&nuell", pos=(120,320), size=(90,44), name="Manuell")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Manuell, self.button_Manuell)
        self.button_Info = wx.Button(panel, -1, label="&Info", pos=(226,320), size=(90,44), name="Info")
        self.Bind(wx.EVT_BUTTON, self.On_Zahlung_Info, self.button_Info)
        self.setWx(panel, [370, 320, 90, 44], [470, 320, 90, 44])

    ## populate the 'Zahlung' list, \n
    # this routine is called from the AfpDialog.Populate
    def Pop_Zahlungen(self):
        liste = self.data.get_display_list()
        gesamt = self.data.get_preis()
        anz = self.data.get_anzahlung()
        gut = self.data.get_gutschrift()
        self.label_Gesamt.SetLabel(gesamt)
        self.label_Anzahlung.SetLabel(anz)
        self.label_Gut.SetLabel(gut)
        self.list_Zahlungen.Clear()
        self.list_Zahlungen.InsertItems(liste, 0)
    ## execution routine for pushing the Ok button \n
    # distribute and enter all payments into the database
    def execute_Ok(self):
        value = Afp_fromString(self.text_Zahlung.GetValue())
        if Afp_isEps(value):
            Auszug = self.text_Auszug.GetValue()
            if self.check_auszug(Auszug):
                self.data.distribute_payment(value)
                if self.do_store: self.data.store()
                self.Ok = True
        print "AfpZahlung.execute_Ok:", value, self.Ok
    ## set flag to avoid writing into database when leaving the dialog \n
    # exectution may be performed by caller
    def do_not_store(self):
        self.do_store = False
    ## check if statement of account (Auszug) exists, if not create one
    # @param auszug - identifier of statement of account to be checked
    def check_auszug(self, auszug):
        if not auszug:
            Ok = AfpReq_Question("Barzahlung?","","Zahlung")
            if Ok:
                today = Afp_toString(self.data.get_globals().get_value("today"))
                auszug = "BAR" + today
                self.text_Auszug.SetValue(auszug)
        if auszug:
            checked = self.data.check_auszug(auszug)
            if not checked:
                datum, Ok = AfpReq_Date("Bitte Datum für Auszug '".decode("UTF-8") + auszug + "' abgeben,", "", "", "", True)
                if Ok: 
                    self.set_auszug(auszug, datum) 
                    checked = True
            return checked
        else:
            return False
    ## create an new statement of account 
    # @param auszug - identifier of statement of account to be created
    # @param datum - date when statement has become valid
    def set_auszug(self, auszug, datum):
        if auszug:
            self.data.set_auszug(auszug, datum)
    ## invoke selection of another participent of this payment
    # @param tablename - name of database taable, where selection should be made
    def select_selection(self, tablename):
        liste = []
        ident = []
        KundenNr = self.data.get_value("KundenNr")
        if tablename == "FAHRTEN":
            felder = "Abfahrt,Zielort,Preis,Zustand,FahrtNr"
            filter_feld = "Zustand"
            filter =  ["Angebot","Rechnung"]
            text = "Mietfahrt"
        elif tablename == "RECHNG":
            felder = "Datum,Zahlbetrag,Wofuer,Zustand,RechNr"
            filter_feld = "Zustand"
            #filter_feld = None
            filter = ["offen"]
            text = "Rechnung"
        rows = Afp_selectSameKundenNr(self.data.get_mysql(), tablename, KundenNr, self.debug, felder, filter_feld, filter)
        for row in rows:
            liste.append(Afp_ArraytoLine(row, " ", 4))
            ident.append(row[4])
        value,ok = AfpReq_Selection("Bitte " + text + " für Zahlung auswählen!","",liste, text + " für Zahlung", ident)
        if ok and value:
            self.data.add_selection(tablename, value)
            self.Pop_Zahlungen()

    # Event Handlers 
    ## event handler when cursor leaves the 'statement of account' (Auszug) textbox
    def On_Zahlung_Auszug(self,event):
        if self.debug: print "Event handler `On_Zahlung_Auszug'"
        print "Event handler `On_Zahlung_Auszug'"
        Auszug = self.text_Auszug.GetValue()
        self.check_auszug(Auszug)
        event.Skip()

    ##Eventhandler BUTTON - add a incoming invoice to this payment \n
    # not implemented yet
    def On_Zahlung_Verb(self,event):
        print "Event handler `On_Zahlung_Verb' not implemented!"
        event.Skip()

    ##Eventhandler BUTTON - add a touristic entry  to this payment \n
    # not implemented yet
    def On_Zahlung_Anmeld(self,event):
        print "Event handler `On_Zahlung_Anmeld' not implemented!"
        event.Skip()

    ##Eventhandler BUTTON - add a cancelled invoice to this payment \n
    # not implemented yet
    def On_Zahlung_Storno(self,event):
        print "Event handler `On_Zahlung_Storno' not implemented!"
        event.Skip()

    ##Eventhandler BUTTON - add a charter entry to this payment \n
    # not implemented yet
    def On_Zahlung_Miet(self,event):
        if self.debug: print "Event handler `On_Zahlung_Miet'"
        self.select_selection("FAHRTEN")
        event.Skip()

    ##Eventhandler BUTTON - add a outgoing invoice to this payment \n
    # not implemented yet
    def On_Zahlung_Rech(self,event):
        if self.debug: print "Event handler `On_Zahlung_Rech'"
        self.select_selection("RECHNG")
        event.Skip()

    ##Eventhandler BUTTON - add a outgoing invoice to this payment \n
    # not implemented yet
    def On_Zahlung_Reihe(self,event):
        if self.debug: print "Event handler `On_Zahlung_Reihe'"
        index = self.list_Zahlungen.GetSelections()[0] 
        if index > 0:
            self.data.remove_selection(index)
            self.Pop_Zahlungen()
        event.Skip()

    ##Eventhandler BUTTON - show list of financial payment transaction \n
    # not implemented yet
    def On_Zahlung_Liste(self,event):
        print "Event handler `On_Zahlung_Liste' not implemented!"
        event.Skip()

    ##Eventhandler BUTTON - allow manuel distribution of this payment \n
    # not implemented yet
    def On_Zahlung_Manuell(self,event):
        print "Event handler `On_Zahlung_Manuell' not implemented!"
        event.Skip()

    ##Eventhandler BUTTON - show payment info \n
    # not implemented yet
    def On_Zahlung_Info(self,event):
        print "Event handler `On_Zahlung_Info' not implemented!"
        event.Skip()

## loader routine for dialog DiFiZahl \n
# @param do_not_store - flag if writing to database should be skipped
def AfpLoad_DiFiZahl(data, do_not_store = False):
    DiZahl = AfpDialog_DiFiZahl(None)
    Zahl = AfpZahlung(data) 
    DiZahl.attach_data(Zahl, False, True)
    if do_not_store: DiZahl.do_not_store()
    DiZahl.ShowModal()
    Ok = DiZahl.get_Ok()
    data = DiZahl.get_data()
    DiZahl.Destroy()
    return Ok, data

