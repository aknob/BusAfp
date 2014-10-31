#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseAdDialog
# AfpBaseAdDialog module provides the dialogs and appropriate loader routines needed for adress handling
# it holds the calsses
# - AfpDialog_AdAusw
# - AfpDialog_AdAttAusw
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
from AfpBase import AfpBaseRoutines, AfpBaseDialog, AfpBaseAdRoutines
from AfpBase.AfpBaseRoutines import *
from AfpBase.AfpBaseDialog import *
from AfpBase.AfpBaseAdRoutines import *

## select adress attribut or enter new \n
# return row or 'None' in case nothing is selected
# @param Adresse - AfpSelectionList holding adress data
def AfpSel_AdgetMrkRow(Adresse):
   sel = Adresse.get_selection("ADRESATT")
   liste, rows = Afp_getListe_fromTableSelection( sel, "KundenNr = 0", "Attribut", "Attribut")
   if not liste[0]: liste[0] = "\"Neues Adressenmerkmal\""
   name = Adresse.get_name()
   row, ok = AfpReq_Selection("Bitte Adressmerkmal für", name +" auswählen.", liste, "Merkmalauswahl", rows)
   index = sel.get_feldindices("Attribut,Tag,Aktion,AttText")
   if not row[index[0]] and ok:
      attribut, ok = AfpReq_Text("Bitte Bezeichnung für neues Adressenmerkmal eingeben.","Dieses Merkmal wird " + name + " zugeordnet.")
      if ok: row[index[0]] = attribut
   else:
      attribut = row[index[0]]
      print "AfpSel_AdgetMrkRow:",attribut, attribut.encode("UTF-8"),attribut.encode('iso8859_15')
      #attribut = attribut.encode('iso8859_15')
      #attribut = attribut.decode("UTF-8")
      print attribut
   if row[index[2]] and ok:
      Tag =  row[index[1]] 
      pyBefehl = "Tag, ok = AfpAdDi_" + row[index[2]] + "(Tag)"
      exec pyBefehl
      if ok:  row[index[1]]  = Tag
   elif ok:
      AttText = row[index[3]]
      AttText, ok = AfpReq_Text("Bitte einen zusätzlichen Text für das Adressenmerkmal '".decode("UTF-8") + attribut + "'" ,"von " + name + " eingeben.",AttText)
      #AttText, ok = AfpReq_Text("Bitte einen zusätzlichen Text für das Adressenmerkmal " ,attribut.decode('iso8859_15') +" von " + name + " eingeben.",AttText)
      if AttText and ok: row[index[3]] = AttText
   if ok: return row
   else: return None
   
def AfpAdDi_Anmeld_RbAtt(Tag):
   Ok = False
   print "AfpAdDi_Anmeld_RbAtt:",Tag, Ok
   return Tag, Ok

## dialog for selection of adress data \n
# selects an entry from the adress table
class AfpDialog_AdAusw(AfpDialog_DiAusw):
   def __init__(self):
      AfpDialog_DiAusw.__init__(self,None, -1, "")
      self.typ = "Adressenauswahl"
      self.datei = "ADRESSE"
   ## get the definition of the selection grid content \n
   # overwritten for "Adressen" use ! \n
   # Each line defines a column for the "Auswahl" dialog. \n
   # Felder = [[Field .Table .Alias,Width], ... , [Field1.Table1,None]]     
   def get_grid_felder(self):  
   #                   Field  Table    Alias  Width     
      Felder = [["Name.Adresse.Name",30], 
                     ["Vorname.Adresse.Name", 20], 
                     ["Strasse.Adresse",30], 
                     ["Ort.Adresse",20], 
                     ["KundenNr.Adresse",None]] # Ident column)  
      return Felder
   ## invoke the dialog for a new entry
   def invoke_neu_dialog(self, globals, search, where):
      if search is None: search = "a"
      debug = True
      Adresse = AfpAdresse(globals, None, None, debug, False)
      Ok = AfpLoad_DiAdEin(Adresse, search)
      return Ok
## dialog for adress selection from attribut \n 
# selects an entry of the adress table by choosinng from the adresatt table   
class AfpDialog_AdAttAusw(AfpDialog_DiAusw):
   def __init__(self):
      AfpDialog_DiAusw.__init__(self,None, -1, "")
      self.typ = "Adressenauswahl"
      self.datei = "ADRESATT"
      # remove 'Neu'-button from panel
      self.button_Neu.Destroy()
   ## get the definition of the selection grid content \n
   # overwritten for "Adressen-attribut" use
   def get_grid_felder(self):  
      Felder = [["Name.AdresAtt.Name",30], 
                     ["Vorname.Adresse.Name", 20], 
                     ["Strasse.Adresse",30], 
                     ["Ort.Adresse",20], 
                     ["KundenNr.AdresAtt = KundenNr.Adresse",None]] 
      return Felder

## loader routine for adress selection dialog
def AfpLoad_AdAusw(globals, Datei, Index, value = "", where = None, attribut = None):
   if Datei == "ADRESATT":
      DiAusw = AfpDialog_AdAttAusw()
   else:
      DiAusw = AfpDialog_AdAusw()
   #print Datei, Index, value, where
   if attribut:
      if len(attribut) > 4 and attribut[:5] == "Bitte":
         text = attribut
      else:
         text = "Bitte " + attribut.decode("UTF-8") + "-Adresse auswählen:".decode("UTF-8")
   else:
      text = "Bitte Adresse auswählen:"
   DiAusw.initialize(globals, Index, value, where, text)
   DiAusw.ShowModal()
   result = DiAusw.get_result()
   #print result
   DiAusw.Destroy()
   return result
## loader routine to select adress data from attribut table
def AfpLoad_AdAttAusw(globals, attribut, value = ""):     
      Datei = "ADRESATT"
      Index = "Name"
      where = "Attribut.ADRESATT = \"" + attribut.decode("UTF-8") + "\" and KundenNr.ADRESATT > 0"
      if not value: value = "a"
      result = AfpLoad_AdAusw(globals, Datei, Index, value, where, attribut)
      return result

## Class AfpDialog_DiAdEin display dialog to show and manipulate Adressen-data and handles interactions \n
# this class is not yet devired from AfpDialog, this has to be done
class AfpDialog_DiAdEin(AfpDialog):
   def __init__(self, *args, **kw):
      self.change_data = False
      self.choicevalues = {}
      AfpDialog.__init__(self,None, -1, "")
      self.lock_data = True
      self.SetSize((452,447))
      self.SetTitle("Adresse")
      
   ## initialize wx widgets of dialog  \n
   # 
   def InitWx(self):
      panel = wx.Panel(self, -1)
      self.label_T_Vorname_Adresse = wx.StaticText(panel, -1, label="&Vorname:", pos=(14,28), size=(62,18), name="T_Vorname_Adresse")
      self.text_Vorname_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,26), size=(260,56), style=wx.TE_MULTILINE|wx.TE_LINEWRAP, name="Vorname_Adresse")
      self.text_Vorname_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Vorname_Adresse"] = "Vorname.ADRESSE"
      self.label_T_Name_Adresse = wx.StaticText(panel, -1, label="&Name:", pos=(32,90), size=(44,18), name="T_Name_Adresse")
      self.text_Name_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,88), size=(260,56), style=wx.TE_MULTILINE|wx.TE_LINEWRAP, name="Name_Adresse")
      self.text_Name_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Name_Adresse"] = "Name.ADRESSE"
      self.label_T_Strasse_Adresse = wx.StaticText(panel, -1, label="Stra&sse:", pos=(28,152), size=(48,18), name="T_Strasse_Adresse")
      self.text_Strasse_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,150), size=(260,24), style=0, name="Strasse_Adresse")
      self.text_Strasse_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Strasse_Adresse"] = "Strasse.ADRESSE"
      self.label_T_Plz_Adresse = wx.StaticText(panel, -1, label="&Plz/", pos=(20,182), size=(32,18), name="T_Plz_Adresse")
      self.text_Plz_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,180), size=(52,24), style=0, name="Plz_Adresse")
      self.text_Plz_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Plz_Adresse"] = "Plz.ADRESSE"
      self.label_T_Ort_Adresse = wx.StaticText(panel, -1, label="O&rt:", pos=(52,182), size=(24,18), name="T_Ort_Adresse")
      self.text_Ort_Adresse = wx.TextCtrl(panel, -1, value="", pos=(132,180), size=(260,24), style=0, name="Ort_Adresse")
      self.text_Ort_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Ort_Adresse"] = "Ort.ADRESSE"
      self.label_T_Telefon_Adresse = wx.StaticText(panel, -1, label="&Telefon:", pos=(22,212), size=(54,18), name="T_Telefon_Adresse")
      self.text_Telefon_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,210), size=(260,22), style=0, name="Telefon_Adresse")
      self.text_Telefon_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Telefon_Adresse"] = "Telefon.ADRESSE"
      self.text_Tel2 = wx.TextCtrl(panel, -1, value="", pos=(80,232), size=(260,22), style=0, name="Tel2")
      self.text_Tel2.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Tel2"] = "Tel2.ADRESSE"
      self.label_TFax = wx.StaticText(panel, -1, label="&Fax:", pos=(22,256), size=(54,18), name="TFax")
      self.text_Fax = wx.TextCtrl(panel, -1, value="", pos=(80,254), size=(260,22), style=0, name="Fax")
      self.text_Fax.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Fax"] = "Fax.ADRESSE"
      self.label_TMail = wx.StaticText(panel, -1, label="&E-Mail:", pos=(22,278), size=(54,18), name="TMail")
      self.text_Mail = wx.TextCtrl(panel, -1, value="", pos=(80,276), size=(260,22), style=0, name="Mail")
      self.text_Mail.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["Mail"] = "Mail.ADRESSE"
      self.label_T_StNr = wx.StaticText(panel, -1, label="Ste&uerNr:", pos=(10,308), size=(66,18), name="T_StNr")
      self.text_StNr = wx.TextCtrl(panel, -1, value="", pos=(80,306), size=(260,22), style=0, name="StNr")
      self.text_StNr.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.textmap["StNr"] = "SteuerNr.ADRESSE"
      self.label_T_Geb_Adresse = wx.StaticText(panel, -1, label="&Geb:", pos=(22,338), size=(54,18), name="T_Geb_Adresse")
      self.text_Geb_Adresse = wx.TextCtrl(panel, -1, value="", pos=(80,336), size=(78,22), style=0, name="Geb_Adresse")
      self.text_Geb_Adresse.Bind(wx.EVT_KILL_FOCUS, self.On_Adresse_Geb)
      self.vtextmap["Geb_Adresse"] = "Geburtstag.ADRESSE"

      self.button_Merk = wx.Button(panel, -1, label="Mer&kmale", pos=(78,370), size=(80,36), name="Merk")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_Merk, self.button_Merk)
      #self.button_Suchen = wx.Button(panel, -1, label="&Suchen", pos=(170,370), size=(80,36), name="Suchen")
      #self.Bind(wx.EVT_BUTTON, self.On_Adresse_Auswahl, self.button_Suchen)
      #self.button_Abbruch = wx.Button(panel, -1, label="&Abbruch", pos=(264,370), size=(80,36), name="Abbruch")
      #self.Bind(wx.EVT_BUTTON, self.On_Adresse_Abbruch, self.button_Abbruch)
      self.button_Ok = wx.Button(panel, -1, label="&OK", pos=(356,370), size=(80,36), name="Ok")
      self.Bind(wx.EVT_BUTTON, self.On_Adresse_Ok, self.button_Ok)
      
      self.label_Anrede = wx.StaticText(panel, -1, label="Anre&de:", pos=(8,6), size=(62,18), name="Anrede")
      self.choice_Anrede = wx.Choice(panel, -1,  pos=(80,5), size=(60,20),  choices=["Du", "Sie"],  name="CAnrede")
      self.choicemap["CAnrede"] = "Anrede.ADRESSE"
      self.choice_anrede_sel = None
      self.Bind(wx.EVT_CHOICE, self.On_CAnrede, self.choice_Anrede)      
      self.label_Geschlecht = wx.StaticText(panel, -1, label="&Geschlecht:", pos=(200,6), size=(80,18), name="Geschlecht")      
      self.choice_Geschlecht = wx.Choice(panel, -1,  pos=(290,5), size=(50,20),  choices=["W","N","M"],  name="CGeschlecht")
      self.choicemap["CGeschlecht"] = "Geschlecht.ADRESSE"
      self.choice_geschlecht_sel =None
      self.Bind(wx.EVT_CHOICE, self.On_CGeschlecht, self.choice_Geschlecht)
      self.choice_Status = wx.Choice(panel, -1,  pos=(280,338), size=(154,20),  choices=["Passiv", "Aktiv", "Neutral", "Markiert", "Inaktiv"],  name="CStatus")
      self.choicemap["CStatus"] = "Kennung.ADRESSE"
      self.choice_status_sel =None
      self.Bind(wx.EVT_CHOICE, self.On_CStatus, self.choice_Status)
      #self.choice_Edit = wx.Choice(panel, -1, pos=(356,26), size=(80,36), choices=["Lesen", "Ändern"],  name="CEdit")
      self.choice_Edit = wx.Choice(panel, -1, pos=(264,370), size=(80,36), choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"],  name="CEdit")
      self.choice_Edit.SetSelection(0)
      self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)

   ## attach to database and populate widgets
   def attach_data(self, Adresse, name = None):
      self.new = Adresse.is_new()     
      if name: 
         self.text_Name_Adresse.SetValue(name)
         self.changed_text.append(self.text_Name_Adresse.GetName())
      AfpDialog.attach_data(self, Adresse, self.new)
   def store_database(self):
      self.Ok = False
      data = {}
      for entry in self.changed_text:
         name, wert = self.Get_TextValue(entry)
         data[name] = wert
      for entry in self.choicevalues:
         name = entry.split(".")[0]
         data[name] = self.choicevalues[entry]
      if self.new and len(data) > 1:
         self.data.set_data_values(data)
         self.Ok = True
      elif data or self.change_data:
         if data: self.data.set_data_values(data)
         self.Ok = True
      if self.Ok:
         self.data.store()
         self.new = False               
      self.changed_text = []
   
   def Pop_choice(self):
     for entry in self.choicemap:
         Choice= self.FindWindowByName(entry)
         if entry == "CStatus":         
            stat = self.data.get_value(self.choicemap[entry])
            cset = AfpAdresse_StatusMap()[stat]
            Choice.SetSelection(cset) 
         else:
            value = self.data.get_string_value(self.choicemap[entry])
            Choice.SetStringSelection(value)

   def On_CAnrede(self,event = None):
      self.choicevalues["Anrede.ADRESSE"] = self.choice_Anrede.GetStringSelection()   
      if event: event.Skip()  
   def On_CGeschlecht(self,event = None):
      self.choicevalues["Geschlecht.ADRESSE"] = self.choice_Geschlecht.GetStringSelection()   
      if event: event.Skip()  
   def On_CStatus(self,event= None ):
      self.choicevalues["Kennung.ADRESSE"] = AfpAdresse_StatusReMap(self.choice_Status.GetCurrentSelection())
      if event: event.Skip()  
   def On_CEdit(self,event):
      select = self.choice_Edit.GetCurrentSelection()
      editable = False
      if select == 1: editable = True
      self.Set_Editable(editable)
      if select == 2: self.On_Adresse_Abbruch(event)
   def On_KillFocus(self,event):
      object = event.GetEventObject()
      name= object.GetName()
      if not name in self.changed_text: self.changed_text.append(name)
   def On_Adresse_Geb(self,event):
      if self.debug: print "Event handler `On_Adresse_Geb'"
      gtag = self.text_Geb_Adresse.GetValue()
      gtag =  Afp_ChDatum(gtag)
      self.text_Geb_Adresse.SetValue(gtag)
      self.On_KillFocus(event)
      event.Skip()
   def On_Adresse_Merk(self,event):
      if self.debug: print "Event handler `On_Adresse_Merk'"
      #if len(self.changed_text): self.store_database()
      changed = AfpLoad_DiAdEin_SubMrk(self.data)
      if changed:      
         self.choice_Edit.SetSelection(1)
         self.Set_Editable(True)
         self.change_data = True
      event.Skip()
   def On_Adresse_Auswahl(self,event):
      print "Event handler `On_Adresse_Auswahl' not implemented!"
      self.status = "select"
      event.Skip()
   def On_Adresse_Abbruch(self,event):
      if self.debug: print "Event handler `On_Adresse_Abbruch'"
      self.Ok = False
      event.Skip()
      self.Destroy()
   def On_Adresse_Ok(self,event):
      if self.choice_Edit.GetSelection() == 1:
         self.store_database()
         if self.debug: print "Event handler `On_Adresse_Ok' save, neu:", self.new,"Ok:",self.Ok 
      else: 
         if self.debug: print "Event handler `On_Adresse_Ok' quit!"
      event.Skip()
      self.Destroy()
  
## loader routines for dialog DiAdEin 
# @param Adresse - AfpAdresse holding data
# @param name - name to be set in dialog
def AfpLoad_DiAdEin(Adresse, name = None):
   DiAdEin = AfpDialog_DiAdEin(None)
   DiAdEin.attach_data(Adresse, name)
   DiAdEin.ShowModal()
   Ok = DiAdEin.get_Ok()
   DiAdEin.Destroy()
   return Ok   
## loader routines for dialog DiAdEin with AfpSuperbase input
# @param globals - global variables including database connection
# @param sb - AfpSuperbase object to extract actuel adressdata from
# @param name - name to be set in dialog
def AfpLoad_DiAdEin_fromSb(globals, sb, name = None):
   Adresse = AfpAdresse(globals, None, sb, sb.debug)
   ken = Adresse.get_value("Kennung.ADRESSE")
   print "AfpLoad_DiAdEin_fromSb", ken, type(ken)
   return AfpLoad_DiAdEin(Adresse, name)
## loader routines for dialog DiAdEin with ident number (KundenNr) input
# @param globals - global variables including database connection
# @param KNr - address ident number (KundenNr)
def AfpLoad_DiAdEin_fromKNr(globals, KNr):
   Adresse = AfpAdresse(globals, KNr, None, globals.debug)
   ken = Adresse.get_value("Kennung.ADRESSE")
   print "AfpLoad_DiAdEin_fromKNr",  ken, type(ken)
   return AfpLoad_DiAdEin(Adresse)
   
class AfpDialog_DiAdEin_SubMrk(wx.Dialog):
   def __init__(self, *args, **kw):
      super(AfpDialog_DiAdEin_SubMrk, self).__init__(*args, **kw) 
      self.data = None
      self.debug = False
      self.textmap = {}
      self.changed_text = []
      self.changelist = {}
      self.changedlists = False
      self.readonlycolor = self.GetBackgroundColour()
      self.editcolor = (255,255,255)
      
      self.InitWx()
      #self.SetSize((358,192))
      self.SetSize((358,225))
      self.SetTitle("Adressenmerkmale")

   def InitWx(self):
      panel = wx.Panel(self, -1)
   #FOUND: DialogListBox "Ad_Attribute", conversion not implemented due to lack of syntax analysis!
      self.list_attribut = wx.ListBox(panel, -1, pos=(8,2) , size=(170, 80), name="Attribut")
      self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_DClick_Attribut, self.list_attribut)
      self.changelist["ADRESATT"] = []
      self.button_Ad_Attribut = wx.Button(panel, -1, label="Mer&kmal", pos=(8,86), size=(100,32), name="Ad_Attribut")
      self.Bind(wx.EVT_BUTTON, self.On_Ad_Merkmal, self.button_Ad_Attribut)      
      self.list_verbindung = wx.ListBox(panel, -1, pos=(180,2) , size=(170, 80), name="Verbindung")
      self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_DClick_Verbindung, self.list_verbindung)
      self.changelist["Verbindung"] = []
      self.button_Ad_Attr_Verbind = wx.Button(panel, -1, label="&Verbindung", pos=(250,86), size=(100,32), name="Ad_Attr_Verbind")
      self.Bind(wx.EVT_BUTTON, self.On_Ad_Verbindung, self.button_Ad_Attr_Verbind)
      self.text_Ad_Attr_Bem = wx.TextCtrl(panel, -1, value="", pos=(8,126), size=(342,26), style=0, name="Ad_Attr_Bem")
      self.textmap["Ad_Attr_Bem"] = "Bem.ADRESSE"
      self.text_Ad_Attr_Bem.Bind(wx.EVT_KILL_FOCUS, self.On_KillFocus)
      self.button_Ad_Attr_Bemerk = wx.Button(panel, -1, label="&Bemerkung", pos=(8,158), size=(100,32), name="Ad_Attr_Bemerk")
      self.Bind(wx.EVT_BUTTON, self.On_Ad_Bem, self.button_Ad_Attr_Bemerk)
   #FOUND: DialogListBox "Ad_Attr_Verb", conversion not implemented due to lack of syntax analysis!
      self.choice_Edit = wx.Choice(panel, -1, pos=(129,158), size=(100,32), choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
      self.choice_Edit.SetSelection(0)
      self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
      self.button_Ok = wx.Button(panel, -1, label="&Ok", pos=(250,158), size=(100,32), name="Ok")
      self.Bind(wx.EVT_BUTTON, self.On_AdAttr_Ok, self.button_Ok)

   # attach to data and populate widgets
   def attach_data(self, Adresse):
      self.data = Adresse
      self.debug = self.data.debug
      self.Populate()
      self.Set_Editable(False)

   # Population routines for dialog and widgets
   def Populate(self):
      self.Pop_text()
      self.Pop_lists()
   def Pop_text(self):
      #print self.textmap
      for entry in self.textmap:
         TextBox = self.FindWindowByName(entry)
         value = self.data.get_string_value(self.textmap[entry])
         TextBox.SetValue(value.decode('iso8859_15'))
   def Pop_lists(self):
      self.Pop_list_attribut()
      self.Pop_list_verbindung()
   def Pop_list_attribut(self):
      rows = self.data.get_value_rows("ADRESATT", "Attribut,AttText")
      liste = []
      for row in rows:
         liste.append(row[0] + " " + row[1])
      self.list_attribut.Clear()
      self.list_attribut.InsertItems(liste, 0)
   def Pop_list_verbindung(self):
      rows = self.data.get_value_rows("Bez", "Vorname,Name")
      liste = []
      for row in rows:
         liste.append(row[0] + " " + row[1])
      #print liste
      self.list_verbindung.Clear()
      self.list_verbindung.InsertItems(liste, 0)

   def Set_Editable(self, ed_flag):
      for entry in self.textmap:
         TextBox = self.FindWindowByName(entry)
         TextBox.SetEditable(ed_flag)
         if ed_flag: TextBox.SetBackgroundColour(self.editcolor)
         else: TextBox.SetBackgroundColour(self.readonlycolor)
      if ed_flag: 
         self.list_attribut.SetBackgroundColour(self.editcolor)
         self.list_verbindung.SetBackgroundColour(self.editcolor)
      else:  
         self.list_attribut.SetBackgroundColour(self.readonlycolor)         
         self.list_verbindung.SetBackgroundColour(self.readonlycolor)  
      self.button_Ad_Attribut.Enable(ed_flag)
      self.button_Ad_Attr_Verbind.Enable(ed_flag)
      self.button_Ad_Attr_Bemerk.Enable(ed_flag)
      self.use_changedlists = ed_flag
   def has_changed(self):
      if self.use_changedlists:
         return (self.changed_text or self.changelist)
      else:
         return False

   # Event Handlers 
   def On_KillFocus(self,event):
      object = event.GetEventObject()
      name = object.GetName()
      if not name in self.changed_text: self.changed_text.append(name)
   def On_DClick_Attribut(self,event):
      if self.debug: print "Event handler `On_DClick_Attribut'"
      index = self.list_attribut.GetSelections()[0]
      if self.is_editable() and index >= 0:
         selection = self.data.get_selection("ADRESATT")
         attribut = selection.get_values("Attribut", index)
         Ok = AfpReq_Question("Soll das Merkmal '" + attribut + "'", "für diese Adresse gelöscht werden?".decode("UTF-8"), "Löschen?".decode("UTF-8"))
         if Ok:
            mani = [index, None]
            selection.manipulate_data([mani])
            self.changelist["ADRESATT"].append(mani)
            self.Pop_list_attribut()
      event.Skip()  
   def On_DClick_Verbindung(self,event):
      if self.debug: print "Event handler `On_DClick_Verbindung'"
      index = self.list_verbindung.GetSelections()[0]
      if self.is_editable() and index >= 0:
         selection = self.data.get_selection("Bez")
         name = selection.get_values("Vorname", index) + " " + selection.get_values("Name", index)
         Ok = AfpReq_Question("Soll die Verbindung zu '" + name + "'", "für diese Adresse gelöscht werden?".decode("UTF-8"), "Löschen?".decode("UTF-8"))
         if Ok:
            mani = [index, None]
            selection.manipulate_data([mani])
            self.changelist["Verbindung"].append(mani)
            self.Pop_list_verbindung()
      event.Skip()  
   
   def On_Ad_Merkmal(self,event):
      if self.debug: print "Event handler `On_Ad_Merkmal'!"
      row = AfpSel_AdgetMrkRow(self.data)
      #print row
      if row:
         mani = [-1, row]
         self.data.get_selection("ADRESATT").manipulate_data([mani])
         self.changelist["ADRESATT"].append(mani)
         self.Pop_list_attribut()
      event.Skip()

   def On_Ad_Verbindung(self,event):
      if self.debug: print "Event handler `On_Ad_Verbindung'"
      name = self.data.get_value("Name")
      text = "Bitte Adresse auswählen die mit der aktuellen in verbunden werden soll."
      auswahl = AfpLoad_DiAusw(self.data.get_mysql(), "ADRESSE", "NamSort", text, name[0])
      if not auswahl is None:
         KNr = int(auswahl)
         rows = self.data.get_mysql().select("*","KundenNr = " + Afp_toString(KNr), "ADRESSE") 
         mani = [-1, rows[0]]       
         self.data.get_selection("Bez").manipulate_data([mani])
         self.changelist["Verbindung"].append(mani)
         self.Pop_list_verbindung()
         # print KNr
      event.Skip()

   def On_Ad_Bem(self,event):
      print "Event handler `On_Ad_Bem' not implemented!"
      event.Skip()

   def On_CEdit(self,event):
      editable = (self.choice_Edit.GetCurrentSelection() == 1) 
      if not editable: self.changed = False
      self.list_attribut.DeselectAll()
      self.Set_Editable(editable)
      event.Skip()
      if self.choice_Edit.GetCurrentSelection() == 2:
         self.On_cancel()
   def On_cancel(self):
      if self.has_changed():
         self.data.delete_selection("ADRESATT")
         self.data.delete_selection("Bez")
      self.Destroy()
         
   def On_AdAttr_Ok(self,event):
      if self.debug: print "Event handler `On_AdAttr_Ok'"
      event.Skip()      
      if not self.choice_Edit.GetCurrentSelection() == 1:
         self.On_cancel()
      else:
         self.Destroy()          
 
# loader routine for dialog DiAdMrk
def AfpLoad_DiAdEin_SubMrk(Adresse):
   DiAdMrk = AfpDialog_DiAdEin_SubMrk(None)
   DiAdMrk.attach_data(Adresse)
   DiAdMrk.ShowModal()
   changed = DiAdMrk.has_changed()
   DiAdMrk.Destroy()
   return changed
