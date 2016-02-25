#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpTourist.AfpToDialog
# AfpTosDialog module provides the dialogs and appropriate loader routines needed for touristihandling
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

import wx
import wx.grid

import AfpBase
from AfpBase import *
from AfpBase.AfpDatabase import AfpSuperbase
from AfpBase.AfpDatabase.AfpSuperbase import AfpSuperbase
from AfpBase.AfpBaseRoutines import *
from AfpBase.AfpBaseDialog import *
from AfpBase.AfpBaseDialogCommon import *
from AfpBase.AfpBaseAdDialog import AfpLoad_AdAusw, AfpLoad_DiAdEin_fromKNr
from AfpBase.AfpBaseFiDialog import AfpLoad_DiFiZahl

import AfpTourist
from AfpTourist import AfpToRoutines
from AfpTourist.AfpToRoutines import *

## select a 'fahrtinfo'  or select a new enty is desired \n
# return index in AfpSQLTableSelection or 'None' in case nothing is selected
# @param fahrtinfo_selection - AfpSQLTableSelection holding the fahrtinfo data
# @param allow_new - add line to allow the selection that a new entry is desired
def AfpToInfo_selectEntry(fahrtinfo_selection, allow_new = False):
    index = None
    rows = fahrtinfo_selection.get_values()
    liste = []
    if allow_new: liste.append(" --- Neue Fahrtinformation eingeben --- ")
    for row in rows:
        zeile = AfpToInfo_genLine(row[5], row[2], row[3], row[1])
        liste.append(zeile)
    value,ok = AfpReq_Selection("Bitte Fahrtinformation auswählen!".decode("UTF-8"),"",liste,"Fahrtinformation")
    if ok:
        index = liste.index(value)
        if allow_new: index -= 1
    return index

## create a copy of the actuel tour may be made completely or partly
# @param data - tour data to be copied
def AfpTour_copy(data):
    print "AfpTour_copy not implemented!"
    text1 = "Soll eine Kopie der aktuellen Reise erstellt werden?"
    text2 = "Wenn Ja, bitte auswählen was übernommen werden soll.".decode("UTF-8")
    liste = ["Adresse","Kontakt","Fahrtinfo","Fahrtextra","Fahrtdaten"]
    keep_flags = AfpReq_MultiLine(text1, text2, "Check", liste, "Reise kopieren?", 350)
    new_address = True
    if keep_flags: new_address = not keep_flags[0]
    KNr = None
    if new_address:
        name = data.get_value("Name.Adresse")
        text = "Bitte Auftraggeber für neue Reise auswählen:"
        KNr = AfpLoad_AdAusw(data.get_globals(),"ADRESSE","NamSort",name, None, text)
    if keep_flags or KNr:
        data.set_new(KNr, keep_flags)
        return data
    else:
        return None

## dialog for selection of tour data \n
# selects an entry from the reisen table
class AfpDialog_ToAusw(AfpDialog_Auswahl):
    ## initialise dialog
    def __init__(self):
        AfpDialog_Auswahl.__init__(self,None, -1, "", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.typ = "Reiseauswahl"
        self.datei = "REISEN"
        self.modul = "Tourist"
    ## get the definition of the selection grid content \n
    # overwritten for "Tourist" use
    def get_grid_felder(self): 
        Felder = [["Abfahrt.REISEN",15], 
                            ["Fahrtende.REISEN", 15], 
                            ["Zielort.REISEN",50], 
                            ["Kennung.REISEN",15], 
                            ["Anmeldungen.REISEN",5], 
                            ["FahrtNr.REISEN",None]] # Ident column
        return Felder
    ## invoke the dialog for a new entry \n
    # overwritten for "Tourist" use
    def invoke_neu_dialog(self, globals, eingabe, filter):
        superbase = AfpSuperbase.AfpSuperbase(globals, debug)
        superbase.open_datei("REISEN")
        superbase.CurrentIndexName("Zielort")
        superbase.select_key(eingabe)
        return AfpLoad_DiToEin_fromSb(globals, superbase, eingabe)      
 
## loader routine for charter selection dialog 
# @param globals - global variables including database connection
# @param index - column which should give the order
# @param value -  if given,initial value to be searched
# @param where - if given, filter for search in table
# @param ask - flag if it should be asked for a string before filling dialog
def AfpLoad_ToAusw(globals, index, value = "", where = None, ask = False):
    result = None
    Ok = True
    #print "AfpLoad_ToAusw input:", index, value, where, ask
    if ask:
        sort_list = AfpTourist_getOrderlistOfTable(globals.get_mysql(), index)        
        #print "AfpLoad_ToAusw sort_list:", sort_list
        value, index, Ok = Afp_autoEingabe(value, index, sort_list, "Reisen")
        print "AfpLoad_ToAusw index:", index, value, Ok
    if Ok:
        DiAusw = AfpDialog_ToAusw()
        #print Index, value, where
        text = "Bitte Reise auswählen:".decode("UTF-8")        
        #print "AfpLoad_ToAusw dialog:", index, value, where
        DiAusw.initialize(globals, index, value, where, text)
        DiAusw.ShowModal()
        result = DiAusw.get_result()
        #print result
        DiAusw.Destroy()
    elif Ok is None:
        # flag for direct selection
        result = Afp_selectGetValue(globals.get_mysql(), "REISEN", "FahrtNr", index, value)
        #print result
    return result      

## allows the display and manipulation of a tour 
class AfpDialog_TourEin(AfpDialog):
    ## initialise dialog
    def __init__(self, *args, **kw):   
        self.change_data = False
        AfpDialog.__init__(self,None, -1, "")
        self.lock_data = True
        self.active = None
        self.SetSize((592,260))
        self.SetTitle("Eigene Reise")
        self.Bind(wx.EVT_ACTIVATE, self.On_Activate)
    
    def InitWx(self):
        panel = wx.Panel(self, -1)
        self.label_T_Zielort = wx.StaticText(panel, -1, label="&Zielort:", pos=(16,14), size=(50,18), name="T_Zielort")
        self.text_Zielort_Reisen = wx.TextCtrl(panel, -1, value="", pos=(76,12), size=(200,22), style=0, name="Zielort_Reisen")
        self.textmap["Zielort_Reisen"] = "Zielort.REISEN"
        self.text_Zielort_Reisen.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_T_Von = wx.StaticText(panel, -1, label="&von", pos=(36,44), size=(28,20), name="T_Von")
        self.text_Abfahrt = wx.TextCtrl(panel, -1, value="", pos=(76,42), size=(80,22), style=0, name="Abfahrt")
        self.textmap["Abfahrt"] = "Abfahrt.REISEN"
        self.text_Abfahrt.Bind(wx.EVT_KILL_FOCUS, self.On_Check_Datum)
        self.label_T_Bis_Reisen = wx.StaticText(panel, -1, label="&bis", pos=(162,44), size=(28,20), name="T_Bis_Reisen")
        self.text_Fahrtende = wx.TextCtrl(panel, -1, value="", pos=(196,42), size=(80,22), style=0, name="Fahrtende")
        self.textmap["Fahrtende"] = "Fahrtende.REISEN"
        self.text_Fahrtende.Bind(wx.EVT_KILL_FOCUS, self.On_Check_Datum)
        self.button_Verst = wx.Button(panel, -1, label="&Veranstalter", pos=(180,220), size=(90,30), name="Verst")
        self.Bind(wx.EVT_BUTTON, self.On_Reisen_Verst, self.button_Verst)
        self.label_T_Kenn = wx.StaticText(panel, -1, label="&FahrtNr:", pos=(280,14), size=(60,18), name="T_Kenn")
        self.text_Kenn = wx.TextCtrl(panel, -1, value="", pos=(350,12), size=(80,22), style=0, name="Kenn")
        self.textmap["Kenn"] = "Kennung.REISEN"
        self.text_Kenn.Bind(wx.EVT_KILL_FOCUS, self.On_Reisen_setKst)
        self.label_T_Kst = wx.StaticText(panel, -1, label="&Konto:", pos=(280,42), size=(60,18), name="T_Kst")
        self.text_Kst = wx.TextCtrl(panel, -1, value="", pos=(350,40), size=(80,22), style=0, name="Kst")
        self.textmap["Kst"] = "Kostenst.REISEN"
        self.text_Kst.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_Anmeldungen = wx.StaticText(panel, -1, label="", pos=(458,12), size=(24,18), name="Anmeldungen")
        self.labelmap["Anmeldungen"] = "Anmeldungen.REISEN"
        self.label_TTeil = wx.StaticText(panel, -1, label="Teilnehmer", pos=(484,12), size=(78,18), name="TTeil")
        self.label_T_Personen = wx.StaticText(panel, -1, label="&max.:", pos=(460,42), size=(42,18), name="T_Personen")
        self.text_Personen = wx.TextCtrl(panel, -1, value="", pos=(510,40), size=(44,22), style=0, name="Personen")
        self.textmap["Personen"] = "Personen.REISEN"
        self.text_Personen.Bind(wx.EVT_KILL_FOCUS, self.On_Reisen_MaxPers)
        self.label_TBem = wx.StaticText(panel, -1, label="&Zusatz:", pos=(10,74), size=(56,18), name="TBem")
        self.text_Bem = wx.TextCtrl(panel, -1, value="", pos=(74,72), size=(480,40), style=wx.TE_MULTILINE|wx.TE_LINEWRAP, name="Bem")
        self.textmap["Bem"] = "Bem.REISEN"
        self.text_Bem.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_T_Route = wx.StaticText(panel, -1, label="Rou&te:", pos=(16,124), size=(50,18), name="T_Route")
        self.choice_Route = wx.Choice(panel, -1,  pos=(78,120), size=(198,30),  choices="",  name="CRoute")      
        self.choicemap["CRoute"] = "Route.REISEN"
 
        self.list_Attrib = wx.ListBox(panel, -1, pos=(78,154), size=(198,50), name="Attrib")
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Reisen_Attrib, self.list_Attrib)
        self.label_AgentName = wx.StaticText(panel, -1, label="", pos=(78,120), size=(198,30), name="AgentName")
        self.labelmap["AgentName"] = "AgentName.REISEN"
        self.list_Preise = wx.ListBox(panel, -1, pos=(298,124), size=(258,82), name="Preise")
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Reisen_Preise, self.list_Preise)
        self.check_Kopie = wx.CheckBox(panel, -1, label="Kopie", pos=(10,226), size=(62,14), name="Kopie")
        self.button_Neu = wx.Button(panel, -1, label="&Neu", pos=(80,220), size=(90,30), name="Neu")
        self.Bind(wx.EVT_BUTTON, self.On_Reisen_Neu, self.button_Neu)
        self.button_IntText = wx.Button(panel, -1, label="Te&xt", pos=(300,220), size=(80,30), name="IntText")
        self.Bind(wx.EVT_BUTTON, self.On_Reisen_Text, self.button_IntText)
       
        self.setWx(panel, [390, 220, 80, 30], [480, 220, 80, 30]) # set Edit and Ok widgets

    ## Event Handlers 
    def On_Check_Datum(self,event):
        print "Event handler `On_Check_Datum' not implemented!"
        event.Skip()

    def On_Reisen_Verst(self,event):
        print "Event handler `On_Reisen_Verst' not implemented!"
        event.Skip()

    def On_Reisen_setKst(self,event):
        print "Event handler `On_Reisen_setKst' not implemented!"
        event.Skip()

    def On_Reisen_MaxPers(self,event):
        print "Event handler `On_Reisen_MaxPers' not implemented!"
        event.Skip()

    def On_Reisen_Attrib(self,event):
        print "Event handler `On_Reisen_Attrib' not implemented!"
        event.Skip()

    def On_Reisen_Preise(self,event):
        print "Event handler `On_Reisen_Preise' not implemented!"
        event.Skip()

    def On_Reisen_Neu(self,event):
        print "Event handler `On_Reisen_Neu' not implemented!"
        event.Skip()

    def On_Reisen_Text(self,event):
        print "Event handler `On_Reisen_Text' not implemented!"
        event.Skip()
        
    ## event handler when window is activated
    # @param event - event which initiated this action   
    def On_Activate(self,event):
        print "Event handler `On_Activate' not implemented"
        if self.active is None:
            if self.debug: print "Event handler `On_Activate'"
            self.active = True
  
    ## execution in case the OK button ist hit - to be overwritten in derived class
    def execute_Ok(self):
        self.store_database()
        
# end of class AfpDialog_DiChEin

## loader routine for dialog TourEin
def AfpLoad_TourEin(data):
    DiTourEin = AfpDialog_TourEin(None)
    DiTourEin.attach_data(data)
    DiTourEin.ShowModal()
    Ok = DiTourEin.get_Ok()
    DiTourEin.Destroy()
    return Ok
    
## loader routine for dialog TourEin according to the given superbase object \n
# @param globals - global variables holding database connection
# @param sb - AfpSuperbase object, where data can be taken from
def AfpLoad_TourEin_fromSb(globals, sb):
    Tour = AfpTour(globals, None, sb, sb.debug, False)
    return AfpLoad_TourEin(Tour)
## loader routine for dialog DiChEin according to the given charter identification number \n
# @param globals - global variables holding database connection
# @param fahrtnr -  identification number of charter to be filled into dialog
def AfpLoad_TourEin_fromFNr(globals, fahrtnr):
    Tour = AfpTour(globals, fahrtnr)
    return AfpLoad_TourEin(Tour)
 

 
