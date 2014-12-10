#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpAdresse.AfpAdScreen
# AfpAdScreen module provides the graphic screen to access all data of the Afp-'Adressen' modul 
# it holds the class
# - AfpAdScreen
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


import wx
import wx.grid

import AfpBase
from AfpBase import *
from AfpBase.AfpUtilities import *
from AfpBase.AfpUtilities.AfpStringUtilities import AfpSelectEnrich_dbname
from AfpBase.AfpUtilities.AfpBaseUtilities import Afp_existsFile
from AfpBase.AfpDatabase import *
from AfpBase.AfpDatabase.AfpSQL import AfpSQL
from AfpBase.AfpDatabase.AfpSuperbase import AfpSuperbase
#from AfpBase.AfpBaseRoutines import AfpPy_Import, Afp_archivName, Afp_startFile
from AfpBase.AfpBaseDialog import AfpReq_Information, AfpScreen
from AfpBase.AfpBaseAdRoutines import AfpAdresse_StatusMap
from AfpBase.AfpBaseAdDialog import AfpLoad_DiAdEin_fromSb, AfpLoad_AdAusw

## Class_Adresse shows Window Adresse and handles interactions
class AfpAdScreen(AfpScreen):
   ## initialize AfpAdScreen, graphic objects are created here
   # @param debug - flag for debug info
   def __init__(self, debug = None):
      AfpScreen.__init__(self,None, -1, "")
      self.typ = "Adresse"
      self.sb_master = "ADRESSE"
      self.sb_filter = ""
      self.archiv_rows = 10
      self.archiv_min_rows = 10
      self.archiv_colnames = [["Datum","Art","Ablage","Fach","Bem."],["ReiseNr","Datum","Zielort","Anmeldung","Preis"],["Zustand","Datum","Zielort","FahrtNr","Preis"],["RechNr","Datum","Text","Preis","Zahlung"],["RechNr","Datum","Text","Preis","Zahlung"],["Merkmal","Text","-","-","-"],["Name","Vorname","Strasse","Ort","Telefon"]]
      self.archiv_colname = self.archiv_colnames[0]
      self.archiv_id = []
      # self properties
      self.SetTitle("BusAfp Adresse")
      self.SetSize((800, 600))
      self.SetBackgroundColour(wx.Colour(192, 192, 192))
      self.SetForegroundColour(wx.Colour(20, 19, 18))
      self.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))

      panel = self.panel
      
      # BUTTON
      self.button_Auswahl = wx.Button(panel, -1, label="Aus&wahl", pos=(692,50), size=(77,50), name="BAuswahl")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_AuswErw, self.button_Auswahl)
      self.button_Bearbeiten = wx.Button(panel, -1, label="&Bearbeiten", pos=(692,110), size=(77,50), name="Bearbeiten")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_AendF, self.button_Bearbeiten)
      self.button_Voll = wx.Button(panel, -1, label="&Volltext", pos=(692,170), size=(77,50), name="BVoll")
      self.Bind(wx.EVT_BUTTON, self.On_Ad_Volltext, self.button_Voll)
       
      self.button_CommandButton31 = wx.Button(panel, -1, label="&Dokument", pos=(692,256), size=(77,50), name="BDokument")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_Doku, self.button_CommandButton31)
      self.button_Doppelt = wx.Button(panel, -1, label="Do&ppelte", pos=(692,338), size=(77,50), name="Doppelt")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_Doppelt, self.button_Doppelt)
      self.button_Listen = wx.Button(panel, -1, label="&Listen", pos=(692,405), size=(77,50), name="Listen")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_Listen, self.button_Listen)
      self.button_Ende = wx.Button(panel, -1, label="Be&enden", pos=(692,470), size=(77,50), name="Ende")
      self.Bind(wx.EVT_BUTTON, self.On_Ende, self.button_Ende)

      #self.button_BAdresse = wx.Button(panel, -1, label="A&dresse:", pos=(34,55), size=(115,20), name="BAdresse")
      #self.Bind(wx.EVT_BUTTON, self.On_Adresse_AendF, self.button_BAdresse)
        
      # COMBOBOX
      self.combo_Filter_Merk = wx.ComboBox(panel, -1, value="", pos=(529,16), size=(150,20), choices=[], style=wx.CB_DROPDOWN, name="Filter_Merk")
      self.Bind(wx.EVT_COMBOBOX, self.On_Filter_Merk, self.combo_Filter_Merk)
        
      self.combo_Archiv = wx.ComboBox(panel, -1, value="Dokumente", pos=(23,236), size=(186,20), choices=["Dokumente","Anmeldungen","Mietfahrten","Rechnungs-Ausgang","Rechnungs-Eingang", "Merkmale","Beziehungen"], style=wx.CB_DROPDOWN, name="Archivtyp")
      #self.combo_Archiv = wx.ComboBox(panel, -1, value="Rechnungs-Ausgang", pos=(23,236), size=(186,20), choices=["Dokumente","Anmeldungen","Mietfahrten","Rechnungs-Ausgang","Rechnungs-Eingang"], style=wx.CB_DROPDOWN, name="Archiv")
      self.Bind(wx.EVT_COMBOBOX, self.On_Filter_Archiv, self.combo_Archiv)
        
      # LABEL
      self.label_Adresse = wx.StaticText(panel, -1, label="Adresse:", pos=(36,55), size=(115,16), name="LAdresse")
      self.label_Tel = wx.StaticText(panel, -1, label="Telefon:", pos=(36,154), size=(46,16), name="LTel")
      self.label_Fax = wx.StaticText(panel, -1, label="Fax:", pos=(36,188), size=(27,16), name="LFax")
      self.label_Mail = wx.StaticText(panel, -1, label="E-Mail:", pos=(36,205), size=(42,16), name="LMail")
        
      # TEXTBOX
      self.text_Vorname = wx.TextCtrl(panel, -1, "", pos=(35,78), size=(217,18), style=wx.TE_READONLY, name="Vorname")
      self.textmap["Vorname"] = "Vorname.ADRESSE"
      self.text_Name = wx.TextCtrl(panel, -1,value="", pos=(35,95), size=(217,18), style=wx.TE_READONLY, name="Name")
      self.textmap["Name"] = "Name.ADRESSE"
        
      self.text_Strasse = wx.TextCtrl(panel, -1,value="", pos=(35,112), size=(271,18), style=wx.TE_READONLY, name="Strasse")
      self.textmap["Strasse"] = "Strasse.ADRESSE"
        
      self.text_Plz = wx.TextCtrl(panel, -1,value="", pos=(35,129), size=(53,18), style=wx.TE_READONLY, name="Plz")
      self.textmap["Plz"] = "Plz.ADRESSE"
      self.text_Ort = wx.TextCtrl(panel, -1,value="", pos=(91,129), size=(215,18), style=wx.TE_READONLY, name="Ort")
      self.textmap["Ort"] = "Ort.ADRESSE"
        
      self.text_Telefon = wx.TextCtrl(panel, -1,value="", pos=(89,154), size=(215,18), style=wx.TE_READONLY, name="Telefon")
      self.textmap["Telefon"] = "Telefon.ADRESSE"
      self.text_Tel2 = wx.TextCtrl(panel, -1,value="", pos=(89,171), size=(215,18), style=wx.TE_READONLY, name="Tel2")
      self.textmap["Tel2"] = "Tel2.ADRESSE"
      self.text_Fax = wx.TextCtrl(panel, -1,value="", pos=(89,188), size=(215,18), style=wx.TE_READONLY, name="Fax")
      self.textmap["Fax"] = "Fax.ADRESSE"
      self.text_Mail = wx.TextCtrl(panel, -1,value="", pos=(89,205), size=(215,18), style=0, name="Mail")
      self.textmap["Mail"] = "Mail.ADRESSE"
        
      self.text_Bem = wx.TextCtrl(panel, -1,value="", pos=(379,137), size=(297,18), style=wx.TE_READONLY, name="Bem")
      self.textmap["Bem"] = "Bem.ADRESSE"
      self.text_BemExt = wx.TextCtrl(panel, -1,value="", pos=(462,52), size=(214,84), style=0, name="BemExt")
      self.extmap["BemExt"] = "BemExt.ADRESSE"
        
      self.text_Geschlecht = wx.TextCtrl(panel, -1,value="", pos=(166,57), size=(24,18), style=wx.TE_READONLY, name="Geschlecht")
      self.textmap["Geschlecht"] = "Geschlecht.ADRESSE"
      self.text_Anrede = wx.TextCtrl(panel, -1,value="", pos=(203,57), size=(27,18), style=wx.TE_READONLY, name="Anrede")
      self.textmap["Anrede"] = "Anrede.ADRESSE"
        
      self.text_MerkT_Archiv = wx.TextCtrl(panel, -1,value="", pos=(689,18), size=(80,18), style=0, name="MerkT_Archiv")

      # OPTIONBUTTON
      self.choice_Status = wx.Choice(panel, -1, pos=(377,52), size=(77,18), choices=["Passiv", "Aktiv", "Neutral", "Markiert", "Inaktiv"],  name="RStatus")
      self.choice_Status.SetSelection(0)
      #self.choice_Status.Enable(False)
      self.Bind(wx.EVT_CHOICE, self.On_CStatus, self.choice_Status)
      self.choicemap = AfpAdresse_StatusMap()
        
      # GRID
      self.grid_archiv = wx.grid.Grid(panel, -1, pos=(23,256) , size=(653, 264), name="Archiv")
      self.grid_archiv.CreateGrid(10, 5)
      self.grid_archiv.SetRowLabelSize(3)
      self.grid_archiv.SetColLabelSize(18)
      self.grid_archiv.EnableEditing(0)
      self.grid_archiv.EnableDragColSize(0)
      self.grid_archiv.EnableDragRowSize(0)
      self.grid_archiv.EnableDragGridSize(0)
      self.grid_archiv.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)
      self.grid_archiv.SetColLabelValue(0, self.archiv_colname[0])
      self.grid_archiv.SetColSize(0, 130)
      self.grid_archiv.SetColLabelValue(1, self.archiv_colname[1])
      self.grid_archiv.SetColSize(1, 130)
      self.grid_archiv.SetColLabelValue(2, self.archiv_colname[2])
      self.grid_archiv.SetColSize(2, 130)
      self.grid_archiv.SetColLabelValue(3, self.archiv_colname[3])
      self.grid_archiv.SetColSize(3, 130)
      self.grid_archiv.SetColLabelValue(4, self.archiv_colname[4])
      self.grid_archiv.SetColSize(4, 130)
      for row in range(0,self.archiv_rows):
         for col in range(0,5):
            self.grid_archiv.SetReadOnly(row, col)
      self.gridmap.append("Archiv")
      self.grid_minrows["Archiv"] = self.grid_archiv.GetNumberRows()

      # MENU Bindings
      #self.Bind(wx.EVT_MENU, self.On_MAdresse, self.MAdresse)
      #self.Bind(wx.EVT_MENU, self.On_MTouristik, self.MTouristik)
      
   ## Eventhandler BUTTON - select other address, either direkt or via attribut
   def On_Adresse_AuswErw(self,event):
      if self.debug: print "Event handler `On_Adresse_AuswErw'!"
      self.sb.set_debug()
      index = self.sb.identify_index().get_name()
      where = AfpSelectEnrich_dbname(self.sb.identify_index().get_where(), self.sb_master)
      values = self.sb.identify_index().get_indexwert()
      #values = self.sb.get_string_value(index)
      #print "Ind:",index, "VAL:",values,"Where:", where
      #vsplit = values.split()
      if self.sb_master == "ADRESATT": 
         value = values[1]
         attrib = values[0]
      else: 
         value = values[0]
         attrib = None
      #auswahl = AfpLoad_DiAusw(self.mysql, self.sb_master, index, None, value, where)
      auswahl = AfpLoad_AdAusw(self.globals, self.sb_master, index, value, where, attrib)
      if not auswahl is None:
         KNr = int(auswahl)
         if self.sb_filter: self.sb.select_where(self.sb_filter, "KundenNr", self.sb_master)
         self.sb.select_key(KNr, "KundenNr", self.sb_master)
         if self.sb_filter: self.sb.select_where("", "KundenNr", self.sb_master)
         self.sb.set_index(index, self.sb_master, "KundenNr")   
         if self.sb_master == "ADRESATT":
            self.sb.select_key(KNr,"KundenNr","ADRESSE")
         self.Populate()
      self.sb.unset_debug()
      event.Skip()
   ## Eventhandler BUTTON - resolve duplicate addresses - not implemented yet!
   def On_Adresse_Doppelt(self,event):
      print "Event handler `On_Adresse_Doppelt' not implemented!"
      event.Skip()
   ## Eventhandler BUTTON - show different lists, not implemented yet!
   def On_Adresse_Listen(self,event):
      print "Event handler `On_Adresse_Listen' not implemented!"
      event.Skip()
   ## Eventhandler BUTTON - change address
   def On_Adresse_AendF(self,event):
      if self.debug: print "AfpAdScreen Event handler `On_Adresse_AendF'"
      AfpLoad_DiAdEin_fromSb(self.globals, self.sb)
      event.Skip()
   ## Eventhandler BUTTON - invoke full text search over addresses an all attached data - not yet implemented
   def On_Ad_Volltext(self,event):
      print "Event handler `On_Ad_Volltext' not implemented!"
      event.Skip()
   ## Eventhandler BUTTON - invoke dokument generation - not yet implemented
   def On_Adresse_Doku(self,event):
      print "Event handler `On_Adresse_Doku' not implemented!"
      event.Skip()
        
   ## Eventhandler COMBOBOX - allow filter due to attributes
   def On_Filter_Merk(self,event): 
      value = self.combo_Filter_Merk.GetValue()
      if self.debug: print "AfpAdScreen Event handler `On_Filter_Merk'", self.sb_master, value      
      where = ""
      changed = (value != "" and  self.sb_master == "ADRESSE") or (value == "" and  self.sb_master == "ADRESATT")
      vorname =  self.sb.get_value("Vorname.ADRESSE")
      name = self.sb.get_value("Name")
      KNr = self.sb.get_value("KundenNr")
      if value == "":   
         if self.sb_master == "ADRESATT":
            self.sb.select_where("")
         self.sb_master = "ADRESSE"
         Index = "NamSort"
         s_key = name + " " + vorname
      else:
         if self.sb_master =="ADRESSE": 
            self.sb.CurrentIndexName("KundenNr")
         self.sb_master = "ADRESATT"
         Index = "AttName"
         where = "Attribut = \"" +  value + "\" and KundenNr > 0"
         s_key =  value + " " + name 
      if changed:
         self.sb.CurrentIndexName(Index, self.sb_master)  
      if where != "" and self.sb_filter != where: 
         self.sb.select_where(where)
      self.sb_filter = where
      if changed:
         #print "On_Filter_Merk", self.sb_master, s_key, value
         #self.sb.set_debug()
         self.sb.select_key(s_key)
         while KNr != self.sb.get_value("KundenNr") and name ==  self.sb.get_value("Name") and vorname ==  self.sb.get_value("Vorname.ADRESSE") and self.sb.neof():
           self.sb.select_next()
      self.CurrentData()
      event.Skip()
   ## Eventhandler COMBOBOX - fill grid 'Archiv' due to the new setting
   def On_Filter_Archiv(self,event):
      self.Pop_grid("Archiv")        
      if self.debug: print "AfpAdScreen Event handler `On_Filter_Archiv'"
      event.Skip()
   ## Eventhandler RADIOBOX - only implemented to reset selection due to databas entry
   def On_CStatus(self, event):
      self.Pop_choice_status()
      print "Event handler `On_CStatus' only implemented to reset selection!"
      event.Skip()
        
   ## Eventhandler MENU - address menu - not yet implemented! \n
   # Probably not needed!
   def On_MAdresse(self, event):
      print "Event handler `On_MAdresse' not implemented!"
      event.Skip()

   ## Eventhandler MENU - address menu - not yet implemented!
   # Probably not needed!
   def On_MTouristik(self, event):
      print "Event handler `On_MTouristik' not implemented!"
      event.Skip()
      
   ## set right status-choice for this address
   def Pop_choice_status(self):
      stat = self.sb.get_value("Kennung.ADRESSE")
      choice = self.choicemap[stat]
      self.choice_Status.SetSelection(choice)
      if self.debug: print "AfpAdScreen Population routine`Pop_choice_status'", choice
   ## populate attribut filter with entries from database table
   def Pop_Filter_Merk(self):
      if self.debug:  print "AfpAdScreen Population routine`Pop_Filter_Merk'"      
      rows = self.mysql.select_strings("Attribut","KundenNr = 0","ADRESATT")
      values = []
      values.append("")
      for value in rows:
         values.append(value[0])
      values.sort()
      self.combo_Filter_Merk.AppendItems(values)
      
   # routines to be overwritten in explicit class
   ## set current record to be displayed 
   # (overwritten from AfpScreen) 
   def set_current_record(self):
      KNr = self.sb.get_value("KundenNr")
      if self.sb_master == "ADRESATT":
         KNr = self.sb.get_value("KundenNr")
         self.sb.select_key(KNr,"KundenNr","ADRESSE")
      #print "set_current_record",self.sb_master, KNr
      self.Pop_choice_status()
      return  
   ## set initial record to be shown, when screen opens the first time
   #overwritten from AfpScreen) 
   # @param origin - string where to find initial data
   def set_initial_record(self, origin = None):
      KNr = 0
      if origin == "Charter":
         KNr = self.sb.get_value("KundenNr.FAHRTEN")
         # FNr = self.globals.get_value("FahrtNr", origin)
      if KNr == 0:
         self.sb.CurrentIndexName("NamSort","ADRESSE")
         #self.sb.set_debug()
         self.sb.select_key("Knoblauch Andreas") # for tests
         #self.sb.select_key("Egeling S") # for tests
         #self.sb.select_last() # for tests
      else:
         self.sb.select_key(KNr,"KundenNr","ADRESSE")
         self.sb.set_index("NamSort","ADRESSE","KundenNr")
         self.sb.CurrentIndexName("NamSort","ADRESSE")
      self.Pop_Filter_Merk()
      return
   ## get identifier of graphical objects, 
   # where the keydown event should not be catched
   # (overwritten from AfpScreen)
   def get_no_keydown(self):
      return ["Bem","BemExt","MerkT_Archiv","Archiv"]
   ## get names of database tables to be opened for this screen
   # (overwritten from AfpScreen)
   def get_dateinamen(self):
      return  ["ADRESATT", "ADRESSE", "ANFRAGE", "ARCHIV"]
   ## get grid rows to populate grids \n
   # (overwritten from AfpScreen) 
   # @param name - name of grid to be populated
   def get_grid_rows(self, name):
      rows = []
      if self.debug: print "AfpAdScreen.get_grid_rows Population routine",name
      if name == "Archiv":
         typ= self.combo_Archiv.GetValue()
         KundenNr =  self.sb.get_value("KundenNr") 
         id_col = 5      
         select = ( "KundenNr = %d")% KundenNr
         if typ == "Dokumente":
            self.archiv_colname = self.archiv_colnames[0]
            rows = self.mysql.select_strings("Datum,Art,Typ,Gruppe,Bem,Extern",select,"ARCHIV")
         elif typ == "Anmeldungen":
            self.archiv_colname = self.archiv_colnames[1]
            select += " and AnmeldNr > 0"
            rows = self.mysql.select_strings("Datum,Art,Typ,Gruppe,Bem,AnmeldNr",select,"ARCHIV")
         elif typ == "Mietfahrten":
            self.archiv_colname = self.archiv_colnames[2]
            select += " and MietNr > 0"
            rows = self.mysql.select_strings("Datum,Art,Typ,Gruppe,Bem,MietNr",select,"ARCHIV")
         elif typ == "Rechnungs-Ausgang":
            self.archiv_colname = self.archiv_colnames[3]
            select += " and RechNr > 0"
            rows = self.mysql.select_strings("Datum,Art,Typ,Gruppe,Bem,RechNr",select,"ARCHIV")
         elif typ == "Rechnungs-Eingang":
            self.archiv_colname = self.archiv_colnames[4]
            select += " and VerbNr > 0"
            rows = self.mysql.select_strings("Datum,Art,Typ,Gruppe,Bem,VerbNr",select,"ARCHIV") 
         elif typ == "Merkmale":
            self.archiv_colname = self.archiv_colnames[5]
            rows = self.mysql.select_strings("Attribut,AttText,Attribut",select,"ADRESATT") 
         elif typ == "Beziehungen":
            self.archiv_colname = self.archiv_colnames[6]
            rows = []
            stack = [int(KundenNr)]
            KNr = int(self.sb.get_value("Bez.ADRESSE")) 
            while not KNr in stack and KNr != 0:
               stack.append(KNr)
               select = ( "KundenNr = %d")% KNr
               row = self.mysql.select_strings("Name,Vorname,Strasse,Ort,Telefon,Bez,KundenNr",select ,"ADRESSE") 
               rows.append(row[0])
               KNr = int(row[0][5])
         for col in range(0,5):
            self.grid_archiv.SetColLabelValue(col, self.archiv_colname[col])
      return rows
