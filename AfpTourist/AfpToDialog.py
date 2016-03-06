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
from AfpBase.AfpBaseAdRoutines import AfpAdresse
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
class AfpDialog_TourEdit(AfpDialog):
    ## initialise dialog
    def __init__(self, *args, **kw):   
        self.change_data = False
        AfpDialog.__init__(self,None, -1, "")
        self.lock_data = True
        self.agent = None
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
        self.vtextmap["Abfahrt"] = "Abfahrt.REISEN"
        self.text_Abfahrt.Bind(wx.EVT_KILL_FOCUS, self.On_Check_Datum)
        self.label_T_Bis_Reisen = wx.StaticText(panel, -1, label="&bis", pos=(162,44), size=(28,20), name="T_Bis_Reisen")
        self.text_Fahrtende = wx.TextCtrl(panel, -1, value="", pos=(196,42), size=(80,22), style=0, name="Fahrtende")
        self.vtextmap["Fahrtende"] = "Fahrtende.REISEN"
        self.text_Fahrtende.Bind(wx.EVT_KILL_FOCUS, self.On_Check_Datum)
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
 
        self.list_Preise = wx.ListBox(panel, -1, pos=(298,120), size=(258,86), name="Preise")
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Reisen_Preise, self.list_Preise)
        self.listmap.append("Preise")
        #self.list_Attrib = wx.ListBox(panel, -1, pos=(78,154), size=(198,50), name="Attrib")
        #self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Reisen_Attrib, self.list_Attrib)
        self.label_T_Art = wx.StaticText(panel, -1, label="Art:", pos=(16,130), size=(50,18), name="T_Art")
        self.choice_Art = wx.Choice(panel, -1,  pos=(78,120), size=(198,30),  choices=AfpTourist_possibleTourKinds(),  name="CArt")      
        self.choicemap["CArt"] = "Art.REISEN"
        self.Bind(wx.EVT_CHOICE, self.On_CArt, self.choice_Art)  
        self.label_T_Route = wx.StaticText(panel, -1, label="Rou&te:", pos=(16,160), size=(50,18), name="T_Route")
        self.choice_Route = wx.Choice(panel, -1,  pos=(78,150), size=(198,30),  choices="",  name="CRoute")      
        self.choicemap["CRoute"] = "Name.TNAME"
        self.label_T_Agent = wx.StaticText(panel, -1, label="Agent:", pos=(16,190), size=(50,18), name="T_Agent")
        self.label_AgentName = wx.StaticText(panel, -1, label="", pos=(78,190), size=(198,30), name="AgentName")
        self.labelmap["AgentName"] = "AgentName.REISEN"
        self.check_Kopie = wx.CheckBox(panel, -1, label="Kopie", pos=(10,226), size=(62,20), name="Kopie")
        self.button_Neu = wx.Button(panel, -1, label="&Neu", pos=(80,220), size=(90,30), name="Neu")
        self.Bind(wx.EVT_BUTTON, self.On_Reisen_Neu, self.button_Neu)
        self.button_Agent = wx.Button(panel, -1, label="&Agent", pos=(180,220), size=(90,30), name="Verst")
        self.Bind(wx.EVT_BUTTON, self.On_Agent, self.button_Agent)
        self.button_IntText = wx.Button(panel, -1, label="Te&xt", pos=(300,220), size=(80,30), name="IntText")
        self.Bind(wx.EVT_BUTTON, self.On_Reisen_Text, self.button_IntText)

        self.setWx(panel, [390, 220, 80, 30], [480, 220, 80, 30]) # set Edit and Ok widgets

 ## read values from dialog and invoke writing into data         
    def store_data(self):
        self.Ok = False
        data = {}
        #print self.changed_text
        for entry in self.changed_text:
            name, wert = self.Get_TextValue(entry)
            data[name] = wert
        if not self.agent is None:
            data = self.add_agent_data(data)
        #print "store_data data:",,self.change_data, data
        if data or self.change_data:
            if self.new: data = self.complete_data(data)
            self.data.set_data_values(data, "REISEN")
            self.data.store()
            self.Ok = True
        self.changed_text = []   
        self.change_data = False  
        
    ## add additonal agent data, if agent has been changed
    # @param data - data where additional data is added
    def add_agent_data(self, data):
        if self.agent:
            data["AgentNr"] = self.agent
            Adresse = AfpAdresse(self.globals, self.agent)
            data["AgentName"] = Adresse.get_name(True)
            data["Kreditor"] = Adresse.get_account("Kreditor")
        elif self.data.get_value("AgentNr"):
            data["AgentNr"] = None
            data["AgentName"] = None
            data["Kreditor"] = None
        return data
        
    ## dis-/enable wigdets according to kind of tour
    def set_kind(self):
        kind = self.choice_Art.GetStringSelection()
        ed_flag = self.is_editable()
        if kind == "Fremd":
            #self.label_T_Agent.Enable(ed_flag)
            self.label_AgentName.Enable(ed_flag)
            self.button_Agent.Enable(ed_flag)
            #self.label_T_Route.Enable(False)
            self.choice_Route.Enable(False)
        else: # kind == "Eigen"
            #self.label_T_Agent.Enable(False)
            self.label_AgentName.Enable(False)
            self.button_Agent.Enable(False)
            #self.label_T_Route.Enable(ed_flag)
            self.choice_Route.Enable(ed_flag)
            
    ## execution in case the OK button ist hit - overwritten from AfpDialog
    def execute_Ok(self):
        self.store_data()

    ## populate the 'Preise' list, \n
    # this routine is called from the AfpDialog.Populate
    def Pop_Preise(self):
        rows = self.data.get_value_rows("PREISE", "Preis,Plaetze,Anmeldungen,Bezeichnung,Kennung")
        liste = ["--- Neuen Preis hinzufügen ---".decode("UTF-8")]
        #print "Pop_Preise:", rows
        for row in rows:
            liste.append(Afp_toString(row[0]).rjust(10) + Afp_toString(row[1]).rjust(4) + Afp_toString(row[2]).rjust(3) + "  " + Afp_toString(row[3]))
        self.list_Preise.Clear()
        self.list_Preise.InsertItems(liste, 0)

    ## Event Handlers 
    def On_Check_Datum(self,event):
        if self.debug: print "Event handler `On_Check_Datum'" 
        object = event.GetEventObject()
        datum = object.GetValue()
        date = Afp_ChDatum(datum)
        object.SetValue(date)
        event.Skip()

    def On_Agent(self,event):
        print "Event handler `On_Agent' not implemented!"
        name = self.data.get_value("AgentName")
        if not name: name = "a"
        text = "Bitte Veranstalter von Reise auswählen:"
        #self.data.globals.mysql.set_debug()
        KNr = AfpLoad_AdAusw(self.data.get_globals(),"ADRESATT","AttName",name, "Attribut = \"Reiseveranstalter\"", text)
        #self.data.globals.mysql.unset_debug()
        print "AfpDialog_TourEdit.On_Agent:", KNr
        if KNr:
            self.label_AgentName.SetLabel(AfpAdresse(self.data.get_globals(),KNr).get_name())
            self.agent = KNr
        else:
            self.agent = False
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
        if self.debug: print "Event handler `On_Reisen_Preise'"
        data = self.data
        index = self.list_Preise.GetSelections()[0] - 1
        if index < 0: index = None
        data = AfpLoad_TourPrices(data, index)
        if data: 
            self.data = data
            self.change_data = True
        event.Skip()

    def On_Reisen_Neu(self,event):
        print "Event handler `On_Reisen_Neu' not implemented!"
        event.Skip()

    def On_Reisen_Text(self,event):
        print "Event handler `On_Reisen_Text' not implemented!"
        event.Skip()

    def On_CArt(self,event):
        if self.debug: print "Event handler `On_CArt'"
        self.set_kind()
        event.Skip()
        
    ## event handler when window is activated
    # @param event - event which initiated this action   
    def On_Activate(self,event):
        #print "Event handler `On_Activate' not implemented"
        if self.active is None:
            if self.debug: print "Event handler `On_Activate'"
            self.active = True
            routes = AfpTourist_getRouteNames(self.data.globals.get_mysql())
            #print "AfpDialog_TourEdit.On_Activate:", routes
            for route in routes[0]:
                self.choice_Route.Append(Afp_toString(route))
            self.Pop_choice()
            self.set_kind()
                    
# end of class AfpDialog_DiChEin

## loader routine for dialog TourEin
def AfpLoad_TourEdit(data):
    DiTourEin = AfpDialog_TourEdit(None)
    new = data.is_new()
    DiTourEin.attach_data(data, new)
    DiTourEin.ShowModal()
    Ok = DiTourEin.get_Ok()
    DiTourEin.Destroy()
    return Ok
    
## loader routine for dialog TourEin according to the given superbase object \n
# @param globals - global variables holding database connection
# @param sb - AfpSuperbase object, where data can be taken from
def AfpLoad_TourEdit_fromSb(globals, sb):
    Tour = AfpTour(globals, None, sb, sb.debug, False)
    if sb.eof(): Tour.set_new(True)
    return AfpLoad_TourEdit(Tour)
## loader routine for dialog DiChEin according to the given charter identification number \n
# @param globals - global variables holding database connection
# @param fahrtnr -  identification number of charter to be filled into dialog
def AfpLoad_TourEdit_fromFNr(globals, fahrtnr):
    Tour = AfpTour(globals, fahrtnr)
    return AfpLoad_TourEdit(Tour)
 
 
class AfpDialog_TourPrices(AfpDialog):
    def __init__(self, *args, **kw):
        AfpDialog.__init__(self,None, -1, "")
        self.SetSize((484,143))
        self.SetTitle("Preis ändern".decode("UTF-8"))

    def InitWx(self):
        panel = wx.Panel(self, -1)
        self.label_T_Fuer = wx.StaticText(panel, -1, label="für".decode("UTF-8"), pos=(20,10), size=(24,18), name="T_Fuer")
        self.label_Zielort = wx.StaticText(panel, -1, pos=(50,10), size=(160,20), name="Zielort")
        self.labelmap["Zielort"] = "Zielort.Reisen"
        self.label_Anmeld = wx.StaticText(panel, -1, pos=(220,10), size=(20,20), name="Anmeld")
        self.label_T_Anmeld = wx.StaticText(panel, -1, label="Anmeldungen", pos=(250,10), size=(120,20), name="T_Anmeld")
        self.label_T_Bez = wx.StaticText(panel, -1, label="&Bezeichnung:", pos=(20,42), size=(90,18), name="T_Bez")
        self.text_Bez = wx.TextCtrl(panel, -1, value="", pos=(120,40), size=(250,22), style=0, name="Bez")
        self.textmap["Bez"] = "Bezeichnung.Preise"
        self.text_Bez.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_T_Preis = wx.StaticText(panel, -1, label="&Preis:", pos=(70,72), size=(40,18), name="T_Preis")
        self.text_Preis = wx.TextCtrl(panel, -1, value="", pos=(120,70), size=(100,22), style=0, name="Preis")        
        self.textmap["Preis"] = "Preis.Preise"
        self.text_Preis.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
        self.label_T_Plaetze = wx.StaticText(panel, -1, label="Pl&ätze:".decode("UTF-8"), pos=(240,72), size=(50,18), name="T_Plaetze")
        self.text_Plaetze = wx.TextCtrl(panel, -1, value="", pos=(300,70), size=(70,22), style=0, name="Plaetze")
        self.textmap["Plaetze"] = "Plaetze.Preise"
        self.text_Plaetze.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)

        self.choice_Typ = wx.Choice(panel, -1,  pos=(40,100), size=(180,25),  choices=["Grund","Aufschlag"],  name="CTyp")      
        self.choicemap["CTyp"] = "Typ.Preise"
        #self.Bind(wx.EVT_CHOICE, self.On_CTyp, self.choice_Typ)  
        self.check_NoPrv = wx.CheckBox(panel, -1, label="ohne Pro&vision", pos=(248,104), size=(122,18), name="NoPrv")
        self.button_Loeschen = wx.Button(panel, -1, label="&Löschen".decode("UTF-8"), pos=(400,48), size=(75,36), name="Löoechen")
        self.Bind(wx.EVT_BUTTON, self.On_Preise_loeschen, self.button_Loeschen)
 
        self.setWx(panel, [400, 6, 75, 36], [400, 90, 75, 36]) # set Edit and Ok widgets

    ## attach data to dialog and invoke population of the graphic elements
    # @param data - AfpTour object to hold the data to be displayed
    # @param index - if given, index of row of price to be displayed in data.selections["Preise"]
    def attach_data(self, data, index):
        self.data = data
        self.debug = self.data.debug
        self.index = index
        self.new = (index is None)
        self.Populate()
        self.Set_Editable(self.new, True)
        if self.new:
            self.choice_Edit.SetSelection(1)

   ## read values from dialog and invoke writing into data         
    def store_data(self):
        self.Ok = False
        data = {}
        for entry in self.changed_text:
            name, wert = self.Get_TextValue(entry)
            data[name] = wert
        for entry in self.choicevalues:
            data[entry] = self.choicevalues[entry]
        if data:
            if self.new: data = self.complete_data(data)
            self.data.set_data_values(data, "PREISE", self.index)
            self.Ok = True
        self.changed_text = []   
        self.choicevalues = {}  

    ## Population routine for the dialog overwritten from parent \n
    # due to special choice settings
    def Populate(self):
        super(AfpDialog_TourPrices, self).Populate()
        if self.index is None:
            self.index = self.data.get_value_length("PREISE") 
            #print "AfpDialog_TourPrices: no index given - NEW index created:", self.index
        if self.index < self.data.get_value_length("PREISE"):
            row = self.data.get_value_rows("PREISE","Bezeichnung,Preis,Typ,Plaetze,Anmeldungen,NoPrv", self.index)[0]
            print "AfpDialog_TourPrices index:", self.index
            print row
            self.text_Bez.SetValue(Afp_toString(row[0]))
            self.text_Preis.SetValue(Afp_toString(row[1]))
            if row[2] == "Aufschlag":
                self.choice_Typ.SetSelection(1)
            else:
                self.choice_Typ.SetSelection(0)
            self.text_Plaetze.SetValue(Afp_toString(row[3]))
            self.label_Anmeld.SetLabel(Afp_toString(row[4]))
            if row[5]:
                self.check_NoPrv.SetValue(True)
            else:
                self.check_NoPrv.SetValue(False)     
                
    ## activate or deactivate changeable widgets \n
    # this method also calls the parent method
    # @param ed_flag - flag if widgets have to be activated (True) or deactivated (False)
    # @param initial - flag if data has to be locked, used in parent method 
    def Set_Editable(self, ed_flag, initial = False):
        super(AfpDialog_TourPrices, self).Set_Editable(ed_flag, initial)
        if ed_flag: 
            self.choice_Typ.Enable(True)
            self.check_NoPrv.Enable(True)
            self.button_Loeschen.Enable(True)
        else:  
            self.choice_Typ.Enable(False)
            self.check_NoPrv.Enable(False)
            self.button_Loeschen.Enable(False)
            #self.Populate()

    # Event Handlers 
    def On_Preise_loeschen(self,event):
        print "Event handler `On_Preise_loeschen' not implemented!"
        event.Skip()

## loader routine for dialog TourPrices
# @param data - Tour data where prices are attached
# @param index - index of price in tour-data
def AfpLoad_TourPrices(data, index):
    TourPrices = AfpDialog_TourPrices(None)
    TourPrices.attach_data(data, index)
    TourPrices.ShowModal()
    Ok = TourPrices.get_Ok()
    data = TourPrices.get_data()
    TourPrices.Destroy()
    if Ok: return data
    else: return None


 
