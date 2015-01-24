#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseDialog
# AfpBaseDialog module provides wrapper for the base Dialog-Requesters delivered by wx, 
#                         common used dialogs as well as the dialog base classes for all dialogs and all screens.
# it holds the calsses
# - AfpDialog_TextEditor - common text editor dialog
# - AfpDialog_DiReport - common output dialog
# - AfpDialog_DiAusw - common selection dialog for unlimited choices
# - AfpDialog - dialog base class
# - AfpScreen - screen base class
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

import AfpUtilities.AfpBaseUtilities
from AfpUtilities.AfpBaseUtilities import Afp_existsFile, Afp_copyFile, Afp_isTime, Afp_isDate, Afp_isNumeric
import AfpUtilities.AfpStringUtilities
from AfpUtilities.AfpStringUtilities import Afp_pathname, Afp_addRootpath, Afp_toString, Afp_toInternDateString, Afp_fromString, Afp_ChDatum
import AfpGlobal
from AfpGlobal import AfpGlobal

import AfpDatabase.AfpSQL
from AfpDatabase.AfpSQL import AfpSQL, AfpSQLTableSelection
import AfpDatabase.AfpSuperbase
from AfpDatabase.AfpSuperbase import AfpSuperbase

import AfpBaseRoutines
from AfpBaseRoutines import Afp_importPyModul, Afp_importAfpModul, Afp_getModulName, Afp_ModulNames, Afp_archivName, Afp_startFile, Afp_printSelectionListDataInfo
import AfpAusgabe
from AfpAusgabe import AfpAusgabe

# Common dialog routines to be used in different modules

## common routine to invoke text editing \n
#  depending on input the text is edited directly or loaded from an external file
# @param input_text - text to be edited or relativ path to file
# @param globals - global variable to hold path-delimiter and path to archiv
def Afp_editExternText(input_text, globals=None):
    if globals:
        delimiter = globals.get_value("path-delimiter")
        file= Afp_archivName(input_text, delimiter)
        if file:
            file = globals.get_value("archivdir") + file
            if Afp_existsFile(file): 
                with open(file,"r") as inputfile:
                    input_text = inputfile.read().decode('iso8859_15')
    return AfpReq_EditText(input_text,"Texteingabe")
   
# Simple dialogs often used (requester in superbase)
#
## Information display (only OK to close window)
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param header - header to be displayed on top ribbon of dialog
def AfpReq_Info(text1, text2, header = ""):
    if not header: header = "Info"
    dialog = wx.MessageDialog(None, text1 + '\n' + text2, header, wx.OK)
    dialog.ShowModal()
## Question, decision needed (return Ok == True/False)
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param header - header to be displayed on top ribbon of dialog
# @param use_Yes - flag to user Yes/No instead of Ok/Cancel
def AfpReq_Question(text1, text2, header = "", use_Yes = True):
    Ok = False
    if not header: header = "Frage"
    if use_Yes:
        dialog = wx.MessageDialog(None, text1 + '\n' + text2, header, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    else:
        dialog = wx.MessageDialog(None, text1 + '\n' + text2, header, wx.ICON_QUESTION)
    ret = dialog.ShowModal()
    if ret == wx.ID_OK or ret == wx.ID_YES: Ok = True
    return Ok
## Small Text or password input needed (return text, Ok == True/False)
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param text - text to be modified, if supplied
# @param header - header to be displayed on top ribbon of dialog
# @param hidden - flag to hide input (* is displayed instead of typed input)
def AfpReq_Text(text1, text2, text = "", header = "", hidden = False):
    Ok = False
    dialog = None
    if not header: 
        if hidden: header = "Passworteingabe"
        else: header = "Texteingabe"
    if hidden: dialog =  wx.PasswordEntryDialog(None, text1 + '\n' + text2, header, text, style=wx.OK|wx.CANCEL)
    else: dialog =  wx.TextEntryDialog(None, text1 + '\n' + text2, header, text, style=wx.OK|wx.CANCEL)
    ret = dialog.ShowModal()
    text = dialog.GetValue()
    dialog.Destroy()
    if hidden: text = text.encode('base64')
    if ret == wx.ID_OK: Ok = True
    return text, Ok
## date input needed, text is checked to have valuable date format (return date-text, Ok == True/False)
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param text - text to be modified, if supplied
# @param header - header to be displayed on top ribbon of dialog
# @param only_past - if a decision about the year has to be made, the date is assumed to lie in the past
def AfpReq_Date(text1, text2, text = "", header = "", only_past = False):
    Ok = False
    if not header: header = "Datumseingabe"
    loop = True
    while loop:
        text, Ok = AfpReq_Text(text1, text2, text, header)
        loop = False
        if Ok:
            datum = Afp_ChDatum(text, only_past)
            if not datum == text:
                text = datum
                loop = True
    return text, Ok
## text input needed, text is checked to have valuable format (return value, format, Ok == True/False) \n
# date input has to have readeble format, output will be set to intern date format for selection. \n
# the returned format array will be filled as follows:
# - [0] - format name: string, int, float, date, time
# - [1] - parameter fo format: string, float - length
# - [2] - parameter 2 for format: float - number of decimals
# - a leading "!" will be removed and a "special" in format[0] will prepend the name
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param text - text to be modified, if supplied
# @param header - header to be displayed on top ribbon of dialog
def AfpReq_Eingabe(text1, text2, text = "", header = ""):
    Ok = False
    value = text
    frm_name = ""
    frm_len = None
    frm_deci = None
    if not header: header = "Eingabe"
    text, Ok = AfpReq_Text(text1, text2, text, header)
    if Ok:
        if text[0] == "!":
            text = text[1:]
            frm_name = "!"
        value = Afp_fromString(text)
        if Afp_isTime(value):
            frm_name += "time"
        elif Afp_isDate(value):
            frm_name += "date"
        elif Afp_isNumeric(value):
            if type(value) == float:
                deci = value - int(value)
                # look for dates only partly written (at least one separator)
                if value < 32  and value >= 1 and deci >= 0.01 and deci <= 0.12:
                    text = Afp_ChDatum(text)
                    value = Afp_fromString(text)
                    frm_name += "date"
                else:
                    frm_name += "float"
                    split = Afp_split(text,[".",","])
                    frm_len = len(text)
                    frm_deci = len(split[-1])
            else:
                frm_name += "int"
        else:
            frm_name += "string"
            #frm_len = len(text)
    format = frm_name
    if frm_len: 
        format += "(" + str(frm_len)
        if frm_deci: 
            format += "," + str(frm_deci)
        format +=")"
    return value, format, Ok   
## Edit multilineText (return text, Ok == True/False)
# @param oldtext - text to be modified, if supplied
# @param header - header to be displayed on top ribbon of dialog
# @param direct - flag that dialog is directliy set to 'modify' instead of 'read'
# @param size - size of dialog window (may differ for different purposes)
def AfpReq_EditText(oldtext = "", header = "TextEditor", direct = False, size = (500, 300)):
    dialog =  AfpDialog_TextEditor(None)
    dialog.attach_text(header, oldtext, size)
    if direct: dialog.set_direct_editing()
    dialog.ShowModal()
    newtext = None
    if dialog.get_Ok():
        newtext = dialog.get_text()
    dialog.Destroy()
    print "AfpReq_EditText:", newtext
    if newtext: 
        return newtext, True
    else: 
        return oldtext, False
## modify multiple entries of the same typ
# - return a list of selections/entries made, if Ok is hit
# - return an empty list, if Cancel is hit
# - return None, if Delete is hit
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param typ - typ of dialog entries, "Text" and "Check" are possible
# @param liste - list with data for dialog entries; 
# in case "Text" - [label, text], in case "Check" - checked text
# @param header - header to be displayed on top ribbon of dialog
# @param width - width of dialog
# @param no_delete - flag if 'delete' button should be hidden
def AfpReq_MultiLine(text1, text2, typ, liste, header = "Multi Editing", width = 250, no_delete = True):
    Ok = False
    values = None
    dialog = AfpDialog_MultiLines(None)
    dialog.attach_data(text1 + '\n' + text2 , header, [typ], liste, width, no_delete)
    ret = dialog.ShowModal()
    result = dialog.get_result()
    return result
## Selection from a list, optional identifiers for the list entries may be given
# (return selected list/identifier entry, Ok == True(False)
# @param text1, text2 - two lines of text to be displayed (used for historical reasons)
# @param liste - list where selection has to be made from
# @param header - header to be displayed on top ribbon of dialog
# @param identify - optional identifier, if listentries are not unique
def AfpReq_Selection(text1, text2, liste, header = "Auswahl", identify = None):
    Ok = False
    value = None
    dialog = wx.SingleChoiceDialog(None, text1 + '\n' + text2 , header, liste)
    ret = dialog.ShowModal()
    ind = dialog.GetSelection()
    if ind >= 0:
        if identify and len(identify) > ind: value = identify[ind]
        elif len(liste) > ind: value = liste[ind]
    if ret == wx.ID_OK : Ok = True
    return value, Ok
## Dialog for 'open' or save filename selection
# @param dir - directory where dialog points to
# @param header - header to be displayed on top ribbon of dialog
# @param wild - wildcard to select entries from directory
# @param open - flag is 'open' dialog is used instead of 'save to' dialog
def AfpReq_FileName(dir = "", header = "", wild = "", open = False):
    Ok = False
    fname = None
    if open:
        if not header: header = "Datei öffnen".decode("UTF-8")
        style = wx.FD_OPEN
    else:
        if not header:  "Datei speichern als"
        style = wx.FD_SAVE
    dialog = wx.FileDialog(None , message=header, defaultDir=dir, wildcard=wild, style=style)
    ret = dialog.ShowModal()
    fname = dialog.GetPath()
    if ret == wx.ID_OK : Ok = True
    return fname, Ok
## Display printer dialog
# - not used
def AfpReq_Printer(frame):
    Ok = False
    pdata = wx.PrintData()
    pdata.SetPaperId(wx.PAPER_A4)
    pdata.SetOrientation(wx.PORTRAIT) # wx.LANDSCAPE, wx.PORTRAIT
    data = wx.PrintDialogData()
    data.SetPrintData(pdata)
    data.EnableSelection(False)
    #data.EnableSelection(True)
    data.EnablePrintToFile(False)
    #data.EnablePrintToFile(True)
    data.EnablePageNumbers(False)
    #data.EnablePageNumbers(True)
    data.SetMinPage(1)
    data.SetMaxPage(5)
    data.SetAllPages(True)
    dialog = wx.PrintDialog(frame, data)
    odata = dialog.GetPrintData()
    if dialog.ShowModal() == wx.ID_OK:
        Ok = True    
    dialog.Destroy()
    return odata, Ok
## Displays Info dialog of product
# @param globals - global variables to hold information data \n
# used values are - name, version, description, copyright, website, license, developer
def AfpReq_Information(globals):
    pversion = globals.get_value("python-version").split("(")[0]
    myversion = globals.mysql.version.split("-")[0]
    wxversion = wx.version().split("(")[0]
    version = "python: " + pversion + '\n' + " wx: " + wxversion + '\n' + " mysql: " + myversion + '\n\n'
    imagefile = Afp_addRootpath(globals.get_value("start-path"), globals.get_value("picture"))
    info = wx.AboutDialogInfo()
    info.SetIcon(wx.Icon(imagefile, wx.BITMAP_TYPE_PNG))
    info.SetName(globals.get_string_value("name"))
    info.SetVersion(globals.get_string_value("version"))
    info.SetDescription(version + globals.get_string_value("description"))
    info.SetCopyright(globals.get_string_value("copyright"))
    info.SetWebSite(globals.get_string_value("website"))
    info.SetLicence(globals.get_string_value("license")) 
    info.AddDeveloper(globals.get_string_value("developer") + '\n' + globals.get_modul_infos())
    docwriter = globals.get_string_value("docwriter")
    if docwriter: info.AddDocWriter(docwriter)
    artist = globals.get_string_value("artist")
    if artist: info.AddDocWriter(artist)
    translator = globals.get_string_value("translator")
    if translator: info.AddDocWriter(translator)
    wx.AboutBox(info)   
 
##  handles automatic and manual sort cirterium selection for data search
#  @param value - initial value for search
#  @param index - initial sort criterium
#  @param sort_list - dictionatry of possible sort criteria, with automatic selection format in the values
#  @param name - name of purpose of this selection
def Afp_autoEingabe(value, index, sort_list, name):
    name = name.decode("UTF-8")
    value, format, Ok = AfpReq_Eingabe("Bitte Auswahlkriteium für die ".decode("UTF-8") + name + "auswahl eingeben.","", value, name +"auswahl")
    print "Afp_autoEingabe:", Ok, value, format, sort_list
    if Ok:
        #print sort_list
        if format[0] == "!":
            liste = sort_list.keys()
            res,Ok = AfpReq_Selection("Bitte Sortierkriterium für die ".decode("UTF-8") + name + "auswahl auswählen.".decode("UTF-8"),"",liste,"Sortierung")
            #print Ok, res
            if Ok:
                index = res
        else:
            for entry in sort_list:
                if sort_list[entry] and sort_list[entry] == format:
                    index = entry
        print "index:", index, value
        if sort_list[index] is None:
            Ok = None
    return value, index, Ok
   
## Baseclass Texteditor Requester 
class AfpDialog_TextEditor(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_TextEditor, self).__init__(*args, **kw) 
        self.Ok = False
        self.readonlycolor = self.GetBackgroundColour()
        self.editcolor = (255,255,255)
        self.text_text = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
        self.choice_Edit = wx.Choice(self, -1, choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
        self.choice_Edit.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
        self.button_Ok = wx.Button(self, -1, label="&Ok", name="Ok")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
        self.lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer.Add(self.choice_Edit,1,wx.EXPAND)
        self.lower_sizer.Add(self.button_Ok,1,wx.EXPAND)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.text_text,1,wx.EXPAND)
        self.sizer.Add(self.lower_sizer,0,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.On_CEdit()
    ## attach header, text and size to dialog
    # @param header - text to be displayed in the window top ribbon
    # @param text - text to be displayed and manipulated
    # @param size - size of dialog
    def attach_text(self, header, text, size):
        self.SetSize(size)
        self.SetTitle(header)
        self.text_text.SetValue(text)
    ## set the dialog edit modus
    def set_direct_editing(self):
        self.choice_Edit.SetSelection(1)
        self.text_text.SetBackgroundColour(self.editcolor) 
    ## return Ok flag, to be called in calling routine
    def get_Ok(self):
        return self.Ok
    ## return actuel text, to be called in calling routine
    def get_text(self):
        ret_text = self.text_text.GetValue()
        print "AfpDialog_TextEditor:", ret_text
        #return self.text_text.GetValue()
        return ret_text
    ## Eventhandler CHOICE - handle event of the 'edit','read' od 'quit' choice
    # @param event - event which initiated this action
    def On_CEdit(self,event = None):
        editable =  self.choice_Edit.GetCurrentSelection() == 1
        self.text_text.SetEditable(editable)
        if editable: self.text_text.SetBackgroundColour(self.editcolor)
        else: self.text_text.SetBackgroundColour(self.readonlycolor)    
        if self.choice_Edit.GetCurrentSelection() == 2: self.Destroy()
        if event: event.Skip()
    ## Eventhandler BUTTON - Ok button pushed
    # @param event - event which initiated this action
    def On_Button_Ok(self,event):
        if self.choice_Edit.GetSelection() == 1:
            self.Ok = True
        event.Skip()
        self.Destroy()

## Baseclass Multiline Requester 
class AfpDialog_MultiLines(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_MultiLines, self).__init__(*args, **kw) 
        self.Ok = False
        self.typ = None
        self.result = []
        self.label = []
        self.texts = []
        self.check = []
        self.sizers = []
        self.statictext = wx.StaticText(self, -1, label="", name="Text")
 
        self.button_Cancel = wx.Button(self, -1, label="&Abbruch", name="Abbruch")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Cancel, self.button_Cancel)   
        self.button_Delete = wx.Button(self, -1, label="&Löschen".decode("UTF-8"), name="Delete")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Delete, self.button_Delete)
        self.button_Ok = wx.Button(self, -1, label="&Ok", name="Ok")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
        self.lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Cancel,2,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Delete,2,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Ok,2,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
    ## attach data to dialog
    # @param text - text to be displayed above action part
    # @param header - header to be display in the dialogts top ribbon
    # @param types [typ] - typ of data to be provided, typ of input needed,  at least one entry in array is needed. 
    # If not enough types are provides, the last will be used for the rest
    # @param datas - input data depending on typ -
    # "Text" typ: [label, text], "Check" typ: text of checkbox - default is set to 'CHECKED'
    # @param width - width of dialog (default = 250)
    # @param no_delete - flag if 'delete' button should be hidden
    def attach_data(self, text, header, types, datas, width = 250, no_delete = True):
        self.statictext.SetLabel(text)
        self.SetTitle(header)
        self.types = types
        self.lines = len(datas)
        if no_delete: self.button_Delete.Hide()
        if len(self.types) < self.lines: 
            while len(self.types) < self.lines:
                self.types.append(self.types[-1])
        height = 70
        for i in range(self.lines):
            data = datas[i]
            if self.types[i] == "Text":
                self.label.append(wx.StaticText(self, -1, label=data[0], name=data[0]))
                self.texts.append(wx.TextCtrl(self, -1, value=data[1], name=data[1]))
                self.sizers.append(wx.BoxSizer(wx.HORIZONTAL))
                self.sizers[-1].AddStretchSpacer(1)
                self.sizers[-1].Add(self.label[-1],9,wx.EXPAND)
                self.sizers[-1].Add(self.texts[-1],9,wx.EXPAND) 
                self.sizers[-1].AddStretchSpacer(1)
                height += 30
            elif self.types[i] == "Check":
                self.check.append(wx.CheckBox(self, -1, label=data, name=data))
                self.check[-1].SetValue(True)
                height += 20
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.statictext, 2, wx.EXPAND)
        for i in range(self.lines):
            if self.types[i] == "Text":
                self.sizer.Add(self.sizers[i], 1, wx.EXPAND)
            elif self.types[i] == "Check":
                self.sizer.Add(self.check[i], 1, wx.EXPAND)
        self.sizer.AddStretchSpacer(1)
        self.sizer.Add(self.lower_sizer, 2, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.SetSize((width, height))
    ## extract output values from graphic elements \n
    # first textboxes are sampled, second checkboxes,
    # the user is in charge to distribute it to the right lines
    def set_values(self):
        values = [None]*self.lines
        ind_t = 0
        ind_c = 0
        for i in range(self.lines):
            data = None
            if self.types[i] == "Text":
                if ind_t < len(self.texts): values[i] = self.texts[ind_t].GetValue()
                ind_t += 1
            elif self.types[i] == "Check":
                if ind_c < len(self.check): values[i] = self.check[ind_c].GetValue()
                ind_c += 1
        self.result = values
    ## return results, to be called from calling routine
    # - returns a list of entries, if Ok is hit
    # - returns an empty list, if Cancel is hit
    # - returns None, if Delete is hit
    def get_result(self):
        return self.result 
    ## Eventhandler BUTTON - Cancel button pushed
    # @param event - event which initiated this action
    def On_Button_Cancel(self,event ):
        event.Skip()
        self.Destroy()
    ## Eventhandler BUTTON - Delete button pushed
    # @param event - event which initiated this action
    def On_Button_Delete(self,event ):
        self.result = None
        event.Skip()
        self.Destroy()
    ## Eventhandler BUTTON - Ok button pushed
    # @param event - event which initiated this action
    def On_Button_Ok(self,event):
        self.set_values()
        event.Skip()
        self.Destroy()

## Baseclass for all  dialogs 
class AfpDialog(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog, self).__init__(*args, **kw) 
        self.Ok = False
        self.new = False
        self.debug = False
        self.data = None
        self.lock_data = False
        self.panel = None
        self.textmap = {}
        self.vtextmap = {}
        self.labelmap = {}
        self.choicemap = {}
        self.listmap = []
        self.conditioned_display = {}
        self.changed_text = []
        self.readonlycolor = self.GetBackgroundColour()
        self.editcolor = (255,255,255)
        self.InitWx()

    ## routine to be called from initWx in devired class
    # set Edit and Ok widgets
    def setWx(self, panel, edit, ok):
        if panel is None: return
        self.choice_Edit = wx.Choice(panel, -1, pos=(edit[0], edit[1]), size=(edit[2], edit[3]), choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
        self.choice_Edit.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
        self.button_Ok = wx.Button(panel, -1, label="&Ok", pos=(ok[0], ok[1]), size=(ok[2], ok[3]), name="Ok")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
      
  ## set up dialog widgets - to be overwritten in derived class
    def InitWx(self):
        return
    ## execution in case the OK button ist hit - to be overwritten in derived class
    def execute_Ok(self):
        self.Ok = True
   
    ## attaches data to this dialog, invokes population of widgets
    # @param data - AfpSelectionList which holds data to be filled into dialog wodgets 
    # @param new - flag if new database entry has to be created 
    # @param editable - flag if dialogentries are editable when dialog pops up
    def attach_data(self, data, new = False, editable = False):
        self.data = data
        self.debug = self.data.debug
        self.new = new
        edit = new or editable
        if edit: self.choice_Edit.SetSelection(1)
        if not self.new: self.Populate()
        self.Set_Editable(edit, False)
    ## central routine which returns if dialog is meant to be editable
    def is_editable(self):
        editable = False
        if self.choice_Edit.GetCurrentSelection() == 1: editable = True
        return editable 
    ## return the Ok flag to caller
    def get_Ok(self):
        return self.Ok
    ## return the attached (an possibly modified) data to caller 
    def get_data(self):
        return self.data
    ## evaluate a simple condition ( [field1,value1] [==,!=] [field2,value2]) \n
    # will return the result of this condition (True/False)
    # @param condition - condition to be evaluated
    def evaluate_condition(self, condition):
        result = True
        sign = None
        if "==" in condition:
            sign = "=="
        elif "!=" in condition:
            sign = "!="
        if sign:
            split = condition.split(sign)
            values = []
            for sp in split:
                if "." in sp:
                    values.append(self.data.get_string_value(sp.strip()))
                else:
                    values.append(sp.strip())
            if len(values) == 2 and values[0] and values[1]:
                pyBefehl = "result = " + values[0] + " " + sign + " " + values[1]
                exec pyBefehl
                if self.debug: print "evaluate_condition:", condition, pyBefehl, result
        return result
    ## common population routine for dialog and widgets
    def Populate(self):
        self.Pop_text()
        self.Pop_label()
        self.Pop_choice()
        self.Pop_lists()
    ## population routine for textboxes \n
    # covention: textmap holds the entryname to retrieve value from self.data
    def Pop_text(self):
        for entry in self.textmap:
            TextBox = self.FindWindowByName(entry)
            value = self.data.get_string_value(self.textmap[entry])
            #print self.textmap[entry], "=", value
            TextBox.SetValue(value)
        for entry in self.vtextmap:
            TextBox = self.FindWindowByName(entry)
            value = self.data.get_string_value(self.vtextmap[entry])
            #print self.textmap[entry], "=", value
            TextBox.SetValue(value)
    ## population routine for labels \n
    # covention: labelmap holds the entryname to retrieve value from self.data
    def Pop_label(self):
        for entry in self.labelmap:
            Label= self.FindWindowByName(entry)
            display = True
            if entry in self.conditioned_display:
                display = self.evaluate_condition(self.conditioned_display[entry])
            if display:
                value = self.data.get_string_value(self.labelmap[entry])
                #print self.labelmap[entry], "=", value
                Label.SetLabel(value)
    ## population routine for choices
    # covention: choicemap holds the entryname to retrieve value from self.data
    def Pop_choice(self):
      for entry in self.choicemap:
            Choice= self.FindWindowByName(entry)
            value = self.data.get_string_value(self.choicemap[entry])
            #print "Pop_choice:", self.choicemap[entry], "=", value
            Choice.SetStringSelection(value)
    ## population routine for lists \n
    # covention: listmap holds the name to generate the routinename to be called: \n
    # Pop_'name'()
    def Pop_lists(self):
        for entry in self.listmap:
            Befehl = "self.Pop_" + entry + "()"
            #print Befehl
            exec Befehl
    ## get value from textbox (needed for formating of dates)
    # @param entry - windowname of calling widget
    def Get_TextValue(self, entry):
        TextBox = self.FindWindowByName(entry)
        wert = TextBox.GetValue()
        if entry in self.vtextmap:
            name = self.vtextmap[entry].split(".")[0]
            wert = Afp_fromString(wert)
        else:
            name = self.textmap[entry].split(".")[0]  
        return name, wert
    ## dis- or enable editing of dialog widgets
    # @param ed_flag - flag to turn editing on or off
    # @param lock_data - flag if invoking of dialog needs a lock on the database
    def Set_Editable(self, ed_flag, lock_data = None):
        if lock_data is None: lock_data = self.lock_data
        for entry in self.textmap:
            TextBox = self.FindWindowByName(entry)
            TextBox.SetEditable(ed_flag)
            if ed_flag: TextBox.SetBackgroundColour(self.editcolor)
            else: TextBox.SetBackgroundColour(self.readonlycolor)    
        for entry in self.vtextmap:
            TextBox = self.FindWindowByName(entry)
            TextBox.SetEditable(ed_flag)
            if ed_flag: TextBox.SetBackgroundColour(self.editcolor)
            else: TextBox.SetBackgroundColour(self.readonlycolor)    
        for entry in self.choicemap:
            Choice = self.FindWindowByName(entry)
            Choice.Enable(ed_flag)
        for entry in self.listmap:
            list = self.FindWindowByName(entry)
            list.Enable(ed_flag)
            if ed_flag: list.SetBackgroundColour(self.editcolor)
            else: list.SetBackgroundColour(self.readonlycolor)    
        if not ed_flag:
            self.changelist = []
        if lock_data:
            if ed_flag:
                if not self.new: self.data.lock_data()
            else: 
                if not self.new: self.data.unlock_data()

    ## common Eventhandler TEXTBOX - when leaving the textbox
    # @param event - event which initiated this action
    def On_KillFocus(self,event):
        if self.is_editable():
            object = event.GetEventObject()
            name = object.GetName()
            if not name in self.changed_text: self.changed_text.append(name)    
    ## Eventhandler CHOICE - handle event of the 'edit','read' od 'quit' choice
    # @param event - event which initiated this action
    def On_CEdit(self,event):
        editable = self.is_editable()
        if not editable: self.Populate()
        self.Set_Editable(editable)
        if self.choice_Edit.GetCurrentSelection() == 2: self.Destroy()
        event.Skip()
    ## Eventhandler BUTTON - Ok button pushed
    # @param event - event which initiated this action
    def On_Button_Ok(self,event):
        if self.choice_Edit.GetSelection() == 1:
            self.execute_Ok()
            if self.lock_data and not self.new: self.data.unlock_data() 
            if self.debug: print "Event handler `On_Button_Ok' save, neu:", self.new,"Ok:",self.Ok 
        else: 
            if self.debug: print "Event handler `On_Button_Ok' quit!"
        event.Skip()
        self.Destroy()
      
## common dialog to create output documents
class AfpDialog_DiReport(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_DiReport, self).__init__(*args, **kw) 
        self.Ok = False
        self.debug = False
        self.data = None     # data where output should be created for
        self.datas = None   # in case more then one output has to be created, datas are attached here and sucessively assigned to data
        self.datasindex = None # current index in datas of actuel assigned data
        self.globals = None
        self.prefix = ""
        self.textmap = {}
        self.labelmap = {}
        self.choicevalues = {}
        self.changelist = []
        self.reportname = []
        self.reportlist = []
        self.reportflag = []
        self.reportdel = []
        self.readonlycolor = self.GetBackgroundColour()
        self.editcolor = (255,255,255)

        self.InitWx()
        #self.SetSize((428,138))
        self.SetSize((428,200))
        self.SetTitle("Dokumentenausgabe")

    ## set up dialog widgets
    def InitWx(self):
        panel = wx.Panel(self, -1)
        self.list_Report = wx.ListBox(panel, -1, pos=(10,10), size=(310,120), name="Report")
        #self.Bind(wx.EVT_LISTBOX_SCLICK, self.On_Rep_Click, self.list_Report)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.On_Rep_DClick, self.list_Report)
        self.choice_Bearbeiten = wx.Choice(panel, -1,  pos=(325,10), size=(93,30),  choices=["Vorlage ...", "Ändern".decode("UTF-8"),"Kopie","Info", "Löschen".decode("UTF-8")], name="CBearbeiten")      
        self.choice_Bearbeiten.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.On_Rep_Bearbeiten, self.choice_Bearbeiten)
        #self.button_Info = wx.Button(panel, -1, label="&Info", pos=(340,46), size=(78,30), name="Info")
        #self.Bind(wx.EVT_BUTTON, self.On_Rep_Info, self.button_Info)
        self.check_Archiv = wx.CheckBox(panel, -1, label="Archiv:", pos=(10,141), size=(70,20), name="Archiv")
        self.label_Ablage= wx.StaticText(panel, -1, label="", pos=(80,144), size=(70,18), name="Ablage")  
        self.text_Bem= wx.TextCtrl(panel, -1, value="", pos=(150,141), size=(170,20), style=0, name="Bem")
        self.button_Abbr = wx.Button(panel, -1, label="&Abbruch", pos=(325,100), size=(93,30), name="Abbruch")
        self.Bind(wx.EVT_BUTTON, self.On_Rep_Abbr, self.button_Abbr)
        self.button_Okay = wx.Button(panel, -1, label="&Ok", pos=(325,136), size=(93,30), name="Okay")
        self.Bind(wx.EVT_BUTTON, self.On_Rep_Ok, self.button_Okay)

    ## attach to database and populate widgets
    # @param data - SelectionList holding data to be filled into output
    # @param globals - globas variables including prefix of typ
    # @param header - header to be display in the dialogts top ribbon
    # @param prefix - if given prefix of resultfile
    # @param datas - if given array of SelectionLists, which are assigned sucessively to data
    def attach_data(self, data, globals, header, prefix, datas = None):
        if header: 
            self.SetTitle(self.GetTitle() + ": " + header)
            self.label_Ablage.SetLabel(header)      
        if data is None and datas:
            self.data = datas[0]
        else:
            self.data = data 
        self.debug = self.data.debug
        self.globals = globals
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = self.globals.get_value("prefix", data.typ)
        if datas: 
            self.datas = datas
        else:
            self.check_Archiv.SetValue(True)
            self.check_Archiv.Enable(False)
            self.label_Ablage.Enable(False)
        self.Populate()
    ## common population routines for dialog and widgets
    def Populate(self):
        self.Pop_text()
        self.Pop_label()
        self.Pop_list()
    ## return ok flag to caller
    def get_Ok(self):
        return self.Ok  
    ## specific population routine for textboxes 
    def Pop_text(self):
        for entry in self.textmap:
            TextBox = self.FindWindowByName(entry)
            value = self.data.get_string_value(self.textmap[entry])
            TextBox.SetValue(value)
    ## specific population routine for lables
    def Pop_label(self):
        for entry in self.labelmap:
            Label = self.FindWindowByName(entry)
            value = self.data.get_string_value(self.labelmap[entry])
            Label.SetValue(value)
    ## specific population routine for lists
    def Pop_list(self):
        rows = self.data.get_string_rows("AUSGABE", "Bez,Datei,BerichtNr")
        self.reportname = []
        self.reportlist = []
        self.reportflag = []
        self.reportdel = []
        for row in rows:
            self.reportname.append(row[0])
            if row[1]: 
                self.reportlist.append(row[1])
                self.reportdel.append(False)
            else: 
                self.reportlist.append(row[2])
                self.reportdel.append(True)
            self.reportflag.append(True)
        rows = self.data.get_string_rows("ARCHIV", "Datum,Gruppe,Typ,Bem,Extern")
        if rows:
            for row in rows:
                self.reportname.append(row[0] + " " + row[1] + " " + row[2] + " " + row[3])
                self.reportlist.append(Afp_archivName(row[4], self.globals.get_value("path-delimiter")))
                self.reportflag.append(False)
                self.reportdel.append(False)
        self.list_Report.Clear()
        self.list_Report.InsertItems(self.reportname, 0)
        return None
    ## common Eventhandler TEXTBOX - when leaving the textbox
    # @param event - event which initiated this action
    def On_KillFocus(self,event):
        object = event.GetEventObject()
        name = object.GetName()
        if not name in self.changelist: self.changelist.append(name)
    ## initiate generation of names of template- and resultfiles
    def generate_names(self):
        fname = self.get_template_name()
        fresult = self.get_result_name()
        return fname, fresult
    ## initiate document generation
    def generate_Ausgabe(self):
        empty = Afp_addRootpath(self.globals.get_value("templatedir"), "empty.odt")
        fname, fresult = self.generate_names()
        print "generate_Ausgabe:", fname, fresult
        if fresult:
            out = AfpAusgabe(self.debug, self.data)
            out.inflate(fname)
            out.write_resultfile(fresult, empty)
        else:
            fresult = fname
        if fresult:
            self.execute_Ausgabe(fresult)
            self.add_to_archiv()
    ## generate template filename due to list selection
    def get_template_name(self):
        template = None
        index = self.get_list_Report_index()
        if index >= 0:
            template = self.reportlist[index]
            if not "." in template and len(template) < 7:
                template = "BusAfp_template_" + template + ".fodt"
                template = Afp_addRootpath(self.globals.get_value("templatedir"), template)
            else:
                if template[:6] == "Archiv":
                    template = template[7:]
                template = Afp_addRootpath(self.globals.get_value("archivdir"), template)
            #print "get_template_name:", template      
        return template
    ## generate result filename due to list selection
    def get_result_name(self):
        fresult = None  
        index = self.get_list_Report_index()
        archiv = self.check_Archiv.IsChecked() 
        if index >= 0 and self.reportflag[index]:
            if archiv:
                max = 0
                for entry in self.reportlist:
                    if "." in entry:
                        split = entry.split(".")
                        nb = int(split[0][-2:]) 
                        if nb > max: max = nb
                max += 1
                if self.datasindex: max += self.datasindex
                if max < 10:  null = "0"
                else:  null = ""
                fresult = self.prefix + self.data.get_string_value() + "_" + null + str(max) + ".odt"
                self.archivname = fresult
                fresult = Afp_addRootpath(self.globals.get_value("archivdir"), fresult)
            else:
                if self.datasindex:
                    fresult = Afp_addRootpath(self.globals.get_value("tempdir"), "BusAfp_textausgabe" + str(self.datasindex) + ".fodt")
                else:
                    fresult = Afp_addRootpath(self.globals.get_value("tempdir"), "BusAfp_textausgabe.fodt")
        #print "get_result_name:", fresult   
        return  fresult
    ## return selected list index
    def get_list_Report_index(self):
        sel = self.list_Report.GetSelections()
        if sel: index = sel[0]
        #else: index = 0
        else: index = -.1
        return index
    ## start editing of generated document in extern editor
    # qparam fresult - result filename
    def execute_Ausgabe(self, fresult):
        Afp_startFile(fresult, self.globals, self.debug)
    ## gernerate entry in archieve
    def add_to_archiv(self):
        if not self.archivname: return
        new_data = {}
        new_data["Gruppe"] = self.label_Ablage.GetLabel()
        new_data["Bem"] = self.text_Bem.GetValue()
        new_data["Extern"] = self.archivname
        self.data.add_to_Archiv(new_data)
   
    # Event Handlers 
    ## Eventhandler left mouse click in list selection
    # @param event - event which initiated this action
    def On_Rep_Click(self,event):
        print "Event handler `On_Rep_Click' not implemented!"
        template, result = self.generate_names()
        #print self.reportlist, self.reportflag
        print template, result
        event.Skip()
    ## Eventhandler left mouse doubleclick in list selection
    # @param event - event which initiated this action
    def On_Rep_DClick(self,event):
        print "Event handler `On_Rep_DClick' not implemented!"
        template, result = self.generate_names()
        #print self.reportlist, self.reportflag
        print template, result
        event.Skip()
    ## Eventhandler BUTTON - Edit button pushed
    # @param event - event which initiated this action
    def On_Rep_Bearbeiten(self,event):
        if self.debug: print "Event handler `On_Rep_Bearbeiten'"      
        template = self.get_template_name()
        list_Report_index = self.list_Report.GetSelection()
        if list_Report_index < 0: list_Report_index = 0
        if template and template[-5:] == ".fodt":
            noWait = False
            filename = ""
            choice = self.choice_Bearbeiten.GetStringSelection()
            if choice == "Ändern".decode("UTF-8"):
                filename = template
            elif choice == "Kopie":
                filename = Afp_addRootpath(self.globals.get_value("tempdir"), "BusAfp_template.fodt")
                Afp_copyFile(template, filename)
            elif choice == "Info":
                filename = Afp_addRootpath(self.globals.get_value("tempdir") , "DataInfo.txt")
                Afp_printSelectionListDataInfo(self.data, filename) 
                noWait = True
            elif choice == "Löschen".decode("UTF-8"):
                rname = self.list_Report.GetStringSelection()
                if self.reportdel[list_Report_index]:
                    ok = AfpReq_Question("Vorlage '" + rname + "' wirklich löschen?".decode("UTF-8") ,"", "Vorlage löschen".decode("UTF-8"))
                    if ok:
                        self.data.delete_row("AUSGABE",list_Report_index)
                        self.data.get_selection("AUSGABE").store()
                        self.Pop_list()
            if filename:
                Afp_startFile( filename, self.globals, self.debug, noWait) 
                if choice == "Kopie":
                    rows = self.data.get_value_rows("AUSGABE","Art,Typ,Bez",list_Report_index)
                    name = rows[0][2]
                    ok = True
                    neu = ""
                    while ok and name in self.reportname:
                        name, ok = AfpReq_Text("Bitte " + neu + "Namen eingeben unter dem die neue Vorlage","für '".decode("UTF-8") + rows[0][0] + " " + rows[0][1] + "' abgelegt werden soll!",rows[0][2], "Vorlagenbezeichnung")
                        neu = "NEUEN "
                    if ok:
                        data = {"Art": rows[0][0], "Typ": rows[0][1], "Bez": name, "Datei": ""}
                        ausgabe = AfpSQLTableSelection(self.data.get_mysql(), "AUSGABE", self.debug, "BerichtNr", self.data.get_selection("AUSGABE").get_feldnamen())
                        ausgabe.new_data()
                        ausgabe.set_data_values(data)
                        ausgabe.store()
                        BNr = ausgabe.get_string_value("BerichtNr")
                        destination = self.globals.get_value("templatedir") + "BusAfp_template_" + BNr + ".fodt"
                        Afp_copyFile(filename, destination)
                        ind = list_Report_index + 1
                        self.reportname.insert(ind, name)
                        self.reportlist.insert(ind, BNr)
                        self.reportflag.insert(ind, True)
                        self.reportdel.insert(ind, True)
                        self.list_Report.Clear()
                        self.list_Report.InsertItems(self.reportname, 0)
        self.choice_Bearbeiten.SetSelection(0)
        event.Skip()  
    ## Eventhandler BUTTON - Cancel button pushed
    # @param event - event which initiated this action
    def On_Rep_Abbr(self,event):
        if self.debug: print "Event handler `On_Rep_Abbr'"
        self.Destroy()
        event.Skip()
    ## Eventhandler BUTTON - Ok button pushed
    # @param event - event which initiated this action
    def On_Rep_Ok(self,event):
        if self.debug: print "Event handler `On_Rep_Ok'"
        self.archivname = None
        if self.datas:
            for data in self.datas:
                self.datasindex = self.datas.index(data)
                self.data = data
                self.generate_Ausgabe()
        else:
            self.generate_Ausgabe()
        if self.archivname:
            select = self.data.get_selection("ARCHIV")
            if select: select.store()
        self.Destroy()
        event.Skip()

## loader routine for dialog DiReport
# for multiple output use 'datalist' as input for a list of 'AfpSelectionList's
def AfpLoad_DiReport(selectionlist, globals, header = "", prefix = "", datalist = None):
    DiReport = AfpDialog_DiReport(None)
    DiReport.attach_data(selectionlist, globals, header, prefix, datalist)
    DiReport.ShowModal()
    DiReport.Destroy()

   
## Dialog for the commen unrestricted selection of data from a database table \n
# the following routines must be supplied in the derived class: \n
#  "self.get_grid_felder()"      for selection grid population \n
#  "self.invoke_neu_dialog()" to generate a new database entry
class AfpDialog_DiAusw(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_DiAusw, self).__init__(*args, **kw) 
        # values from call
        self.mysql = None
        self.globals = None
        self.debug = False
        self.datei = None
        self.index = None
        self.select = None
        self.where = None  
        self.search = None  
        # inital values      
        self.rows = 7
        self.grid_breite = 500
        # for internal use
        self.used_modul = None
        self.cols = None
        self.feldlist = ""
        self.dateien = ""
        self.textmap = []
        self.sortname = ""
        self.valuecol = -1 
        self.link = None  
        self.ident = [None]
        self.offset = 0
        # for the result
        self.result_index = -1
        self.result = None

        self.InitWx()
        self.SetSize((560,315))
        self.SetTitle("--Variable-Text--")
   
    ## set up dialog widgets      
    def InitWx(self):
        self.panel = wx.Panel(self, -1)
        panel = self.panel
        self.label_Auswahl = wx.StaticText(panel, -1, label="-- Bitte Datensatz auswählen --", pos=(4,6), size=(508,20), name="Auswahl")
        self.button_First = wx.Button(panel, -1, label="|<", pos=(520,44), size=(30,28), name="First")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_First, self.button_First)
        self.button_PPage = wx.Button(panel, -1, label="&<<", pos=(520,72), size=(30,28), name="PPage")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_PPage, self.button_PPage)
        self.button_Minus = wx.Button(panel, -1, label="&<", pos=(520,100), size=(30,28), name="Minus")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Prev, self.button_Minus)
        self.button_Plus = wx.Button(panel, -1, label="&>", pos=(520,128), size=(30,28), name="Plus")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Next, self.button_Plus)
        self.button_NPage = wx.Button(panel, -1, label="&>>", pos=(520,156), size=(30,28), name="NPage")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_NPage, self.button_NPage)
        self.button_Last = wx.Button(panel, -1, label=">|", pos=(520,184), size=(30,28), name="Last")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Last, self.button_Last)
        self.button_Suchen = wx.Button(panel, -1, label="&Suchen", pos=(8,230), size=(80,40), name="Suchen")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Suchen, self.button_Suchen)
        self.button_Neu = wx.Button(panel, -1, label="&Neu", pos=(108,230), size=(80,40), name="Neu")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Neu, self.button_Neu)
        self.button_Abbruch = wx.Button(panel, -1, label="&Abbruch", pos=(338,230), size=(100,40), name="Abbruch")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Abbruch, self.button_Abbruch)
        self.button_Okay = wx.Button(panel, -1, label="&OK", pos=(450,230), size=(100,40), name="Okay")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Ok, self.button_Okay)
    ## initialisation of  the dialog \n
    # set up grid, attach data
    # @param globals - global variables including database connection
    # @param index - name of column for sorting values
    # @param value - actuel index value for this selection
    # @param where - filter for this selection
    # @param text - text to be displayed above selection list
    def initialize(self, globals, Index, value, where, text):
        value = Afp_toInternDateString(value)
        self.globals = globals
        self.mysql = globals.get_mysql()
        self.debug = self.mysql.get_debug()
        #self.datei = Datei.upper()
        self.dateien = self.datei
        self.index = Index
        self.search = value
        # initialize grid
        if self.globals.os_is_windows():
            self.rows = int(1.5 * self.rows)
        felder = self.get_grid_felder()
        breite = self.grid_breite
        self.feldlist = ""
        if "=" in felder[-1][0]:
            self.link = felder[-1][0]
            lsplit =  self.link.split()
            felder[-1][0] = lsplit[-1]
        lgh = len(felder)
        ColLabelValue = []
        ColSize = []
        skip = False
        width = 0
        name = ""
        indexcol = -1
        selectname = ""
        for i in range(0,lgh):
            feld = felder[i][0]    
            if self.index + "." in feld: indexcol = len(ColLabelValue)
            if self.feldlist == "": komma = ""
            else : komma = ","
            self.feldlist += komma + feld 
            if not felder[i][1] is None:
                new_width =  felder[i][1]*(breite-10)/100
                if skip:  width += new_width
                fsplit = feld.split(".") 
                if i == 0:  selectname = fsplit[0] + "." + fsplit[1]
                if len(fsplit) > 2:
                    new_name = fsplit[2]
                    if new_name: skip = True
                    else: skip = False
                else:
                    new_name = ""
                    skip = False
                if name and not name == new_name: # delayed write
                    if self.sortname == "":
                        self.sortname = name
                        self.valuecol = len(ColLabelValue)
                    ColLabelValue.append(name)
                    ColSize.append(width)
                name = new_name
                if not skip: # direct write
                    ColLabelValue.append(fsplit[0])
                    ColSize.append(new_width)
                if not fsplit[1].upper() in self.dateien:
                    self.dateien += " " + fsplit[1].upper()
        if indexcol > -1:
            selectname =  self.index + "." + self.datei
            self.sortname = ""
            self.valuecol = indexcol
        if not self.sortname: 
            self.sortname =   selectname
            self.SetTitle("Auswahl " +  self.datei.capitalize() + " Sortierung: " + selectname.split(".")[0])
        else:
            self.SetTitle("Auswahl " +  self.datei.capitalize() + " Sortierung: " + self.sortname)
        if text: self.label_Auswahl.SetLabel(text)
        if not value == "":
            self.select = selectname  + " >= \"" + value + "\""
        self.where = where
        self.cols = len(ColLabelValue) 
        panel = self.panel
        self.grid_auswahl = wx.grid.Grid(panel, -1, pos=(8,25) , size=(breite, 198), name="Auswahl")
        self.grid_auswahl.CreateGrid(self.rows, self.cols)
        self.grid_auswahl.SetRowLabelSize(0)
        self.grid_auswahl.SetColLabelSize(18)
        self.grid_auswahl.EnableEditing(0)
        #self.grid_auswahl.EnableDragColSize(0)
        self.grid_auswahl.EnableDragRowSize(0)
        self.grid_auswahl.EnableDragGridSize(0)
        self.grid_auswahl.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)   
        for col in range(0,self.cols):  
            self.grid_auswahl.SetColLabelValue(col,ColLabelValue[col])
            self.grid_auswahl.SetColSize(col,ColSize[col])
        for row in range(0,self.rows):
            for col in range(0,self.cols):
                self.grid_auswahl.SetReadOnly(row, col)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_LEFT_CLICK, self.On_LClick, self.grid_auswahl)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_LEFT_DCLICK, self.On_DClick, self.grid_auswahl)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_RIGHT_CLICK, self.On_RClick, self.grid_auswahl)
        self.Pop_grid()
        if self.ident == [None]: # grid not filled, go for last entries
            self.On_Ausw_Last()
    ## populate selection grid
    def Pop_grid(self):
        limit = str(self.offset) + ","+ str(self.rows)
        rows = self.mysql.select(self.feldlist,self.select,self.dateien, self.sortname, limit, self.where, self.link)
        lgh = len(rows)
        self.ident = []
        #print "AfpDialog_DiAusw.Pop_grid lgh:", lgh
        for row in range(0, self.rows):
            for col in range(0,self.cols):
                if row < lgh:
                    self.grid_auswahl.SetCellValue(row, col,  Afp_toString(rows[row][col]))
                else:
                    self.grid_auswahl.SetCellValue(row, col,  "")
            if row < lgh:
                self.ident.append(rows[row][self.cols])
    ## return if grid-rows are filled completely
    def grid_is_complete(self):
        return len(self.ident) >= self.rows
    ## step backwards on database table 
    # @param step - step length
    # @param last - flag in new selection is necessary
    def set_step_back(self, step, last = False):
        #print "AfpDialog_DiAusw.set_step_back In:", step, last
        if self.offset >= step and not last:
            self.offset -= step
            return
        if last:
            limit = "0,1"
            ssplit = self.select.split()
            rows = self.mysql.select(self.feldlist, self.select, self.dateien, self.sortname + " DESC", limit, self.where, self.link)
            value = Afp_toInternDateString(rows[0][self.valuecol])
            self.select = ssplit[0] + " " + ssplit[1] + " \"" + value + "\""
            self.ident[0] = rows[0][-1]
        limit = "0,"+ str(self.rows + 1)
        ssplit = self.select.split()
        select = ssplit[0] + " < " + ssplit[2]
        rows = self.mysql.select(self.feldlist, select,self.dateien, self.sortname + " DESC", limit, self.where, self.link)
        if len(rows):
            value = Afp_toInternDateString(rows[-1][self.valuecol])
        else:
            value = ""
        select = ssplit[0] + " " + ssplit[1] + " \"" + value + "\""
        offset = -1
        anz = 2*self.rows
        while offset < 0:
            limit = "0,"+ str(anz)
            rows = self.mysql.select(self.feldlist, select,self.dateien, self.sortname, limit, self.where, self.link)
            lgh = len(rows)
            for i in range(0,len(rows)):
                #if Afp_compareSql(rows[i][-1], self.ident[0],True): offset = i 
                if rows[i][-1] == self.ident[0]: offset = i
            if lgh == anz:
                anz += anz
            elif offset < 0:
                print "Warning: AfpDialog_DiAusw.set_step_back: identic entry not found ",anz
                offset = 0
        self.select = select
        if offset < step:
            self.offset = 0
        else:
            self.offset = offset - step
        #print "AfpDialog_DiAusw.set_step_back Out:", offset, step, self.offset
    ## return result
    def get_result(self):
        return self.result
 
    # Event Handlers 
    ## event handler for the Left Mouse Click 
    def On_LClick(self, event): 
        if self.debug: print "Event handler `On_LClick'"
        self.result_index = event.GetRow()
        event.Skip()   
    ## event handler for the Left Mouse Double Click
    def On_DClick(self, event): 
        if self.debug: print "Event handler `On_DClick'"
        self.result_index = event.GetRow()
        self.result = self.ident[self.result_index]
        event.Skip()
        self.Destroy()
    ## event handler for the Right Mouse Click
    def On_RClick(self, event): 
        print "Event handler `On_RClick' not implemented"
        event.Skip()
    ## event handler for the Select First button        
    def On_Ausw_First(self,event):
        if self.debug: print "Event handler `On_Ausw_First'"
        ssplit = self.select.split()
        self.select = ssplit[0] + " " + ssplit[1] + " \"\""
        self.offset = 0
        self.Pop_grid()
        event.Skip()
    ## event handler for the Select Previous Page button
    def On_Ausw_PPage(self,event):
        if self.debug: print "Event handler `On_Ausw_PPage'"
        self.set_step_back(self.rows - 1)
        self.Pop_grid()
        event.Skip()
    ## event handler for the Select Previous Entry button
    def On_Ausw_Prev(self,event):
        if self.debug: print "Event handler `On_Ausw_Prev'"
        self.set_step_back(1)
        self.Pop_grid()
        event.Skip()
    ## event handler for the Select Next Entry button
    def On_Ausw_Next(self,event):
        if self.debug: print "Event handler `On_Ausw_Next'"
        if self.grid_is_complete():
            self.offset += 1
            self.Pop_grid()
        event.Skip()
    ## event handler for the Select Next Page button
    def On_Ausw_NPage(self,event):
        if self.debug: print "Event handler `On_Ausw_NPage'"
        if self.grid_is_complete():
            self.offset += self.rows - 1
            self.Pop_grid()
        event.Skip()
    ## event handler for th Select Last button
    def On_Ausw_Last(self,event = None):
        if self.debug: print "Event handler `On_Ausw_Last'"
        self.set_step_back(self.rows - 1, True)
        self.Pop_grid()
        if event: event.Skip()
    ## event handler for the Search button
    def On_Ausw_Suchen(self,event):
        if self.debug: print "Event handler `On_Ausw_Suchen'"
        value = self.search
        text, Ok = AfpReq_Text("Suche in Datei " + self.datei.capitalize() + ".", "Bitte Suchbegriff eingeben:", value, "Texteingabe Suche")
        if Ok:
            select = self.select.split()
            self.search = text
            self.select = select[0] + " " + select[1] + " \"" + text + "\""
            self.offset = 0
            #print "Ok", text         
            self.Pop_grid()
        event.Skip()
    ## event handler fpr the New button   
    def On_Ausw_Neu(self,event):
        if self.debug: print "Event handler `On_Ausw_Neu'"
        Ok = self.invoke_neu_dialog(self.globals, self.search, self.where)
        if Ok: self.Pop_grid()
        event.Skip() 
    ## event handler for the Cancel button    
    def On_Ausw_Abbruch(self,event):
        if self.debug: print "Event handler `On_Ausw_Abbruch'"
        event.Skip()
        self.Destroy()
    ## event handler for the OK button
    def On_Ausw_Ok(self,event):
        if self.debug: print "Event handler `On_Ausw_Ok'"
        if self.result_index > -1:
            self.result = self.ident[self.result_index]
        event.Skip()
        self.Destroy()
      
    # routines to be overwritten for custimisation
    # -------------------------------------------------------------------
   
    ## selection grid definition \n
    # must be overwritten in devired dialog \n
    #
    # All columns with a 'width' entry will be shown, the witdh entry is the percetage of the available witdh used by this column. \n
    # The column with a 'None' entry is used for identification and the appropriate value will be returned in case of selection. \n
    # The first string defines the 'field' and the 'table' where the data is extracted from, the optional additional third part indicates
    #   that a concatinated column will be used for all lines having the same value ('alias'). \n
    # Selection works either on the 'field.table' entry of the first line or in the 'index' supplied from outside if it can be found in this list. \n
    # Sorting works on the first 'alias' entry if available or is handled simular to the selection. \n
    #
    # If different tables are involved the 'Ident column' string must hold the connection forumlar. \n
    # The first 'field.table' string will then be returned in the case of selection.\n
    #
    # Felder = [[Field .Table .Alias,Width], ... , [Field1.Table1,None]]  
    #
    # example and comments see in "AfpAdDialog.AfpDialog_AdAusw"
    def get_grid_felder(self):
        # get the definition of the grid content (to be overwritten)
        return []
    ## invoke dialog for a new entry \n
    # may be overwritten in devired dialog
    def invoke_neu_dialog(self, globals, search, where):
        # invoke the dialog for a new entry (to be overwritten)
        AfpReq_Info("Funktion 'Neu' nicht eingebaut!","Meist ist der Grund dazu Doppeleingaben zu vermeiden.","Funktion 'Neu'")
        return False

## base class for Screens
class AfpScreen(wx.Frame):
    ## constructor
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.typ = None
        self.debug = False
        self.globals = None
        self.mysql = None
        self.setting = None
        self.sb = None
        self.sb_filter = ""
        self.menu_items = {}
        self.textmap = {}
        self.choicemap = {}
        self.extmap = {}
        self.listmap =[]
        self.list_id = {}
        self.gridmap = []
        self.grid_id = {}
        self.grid_minrows = {}
        self.filtermap = {}
        self.indexmap = {}
        self.no_keydown = []     
        self.buttoncolor = (230,230,230)
        self.actuelbuttoncolor = (255,255,255)
        self.panel = wx.Panel(self, -1, style = wx.WANTS_CHARS) 
        
    ## connect to database and populate widgets
    # @param globals - global variables, including database connection
    # @param sb - AfpSuperbase database object , if supplied, otherwise it is created
    # @param origin - string from where to get data for initial record, 
    # to allow syncronised display of screens (only works if 'sb' is given)
    def init_database(self, globals, sb, origin):
        self.create_menubar()
        self.create_modul_buttons()
        self.globals = globals
        # set header
        self.SetTitle(self.GetTitle() + " " + globals.get_host_header())
        # shortcuts for convienence
        self.mysql = self.globals.get_mysql()
        self.debug = self.globals.is_debug()
        #self.debug = True
        self.globals.set_value(None, None, self.typ)
        self.load_additional_globals()
        # add 'Einsatz' moduls if desired
        if hasattr(self,'einsatz'):
            self.einsatz = Afp_importAfpModul("Einsatz", globals)
        else:
            self.einsatz = None
        print "AfpScreen.init_database Einsatz:", self.einsatz
        # Keyboard Binding
        self.no_keydown = self.get_no_keydown()
        self.panel.Bind(wx.EVT_KEY_DOWN, self.On_KeyDown)
        self.panel.SetFocus()
        children = self.panel.GetChildren()
        for child in children:
            if not child.GetName() in self.no_keydown:
                child.Bind(wx.EVT_KEY_DOWN, self.On_KeyDown)
        # generate Superbase
        setting = self.globals.get_setting(self.typ)
        if not self.debug and not setting is None: 
            if setting.exists_key("debug"):
                self.debug = setting.get("debug")
        if sb:
            self.sb = sb
        else:
            self.sb = AfpSuperbase(self.globals, self.debug)
        dateien = self.get_dateinamen()
        for datei in dateien:
            self.sb.open_datei(datei)
        self.set_initial_record(origin)
        self.set_current_record()
        self.Populate()
    
    ## create menubar and add common items \n
    # menubar implementation has only be done to this point, specific Afp-modul menues are not yet implemented
    def create_menubar(self):
        self.menubar = wx.MenuBar()
        tmp_menu = wx.Menu()
        modules = Afp_ModulNames()
        for mod in modules:
            new_id = wx.NewId()
            self.menu_items[new_id] = wx.MenuItem(tmp_menu, new_id, mod, "", wx.ITEM_CHECK)
            tmp_menu.AppendItem(self.menu_items[new_id])
        new_id = wx.NewId()
        self.menu_items[new_id] = wx.MenuItem(tmp_menu, new_id, "Beenden", "")
        tmp_menu.AppendItem(self.menu_items[new_id])
        self.menubar.Append(tmp_menu, "Bildschirm")
        tmp_menu = wx.Menu() 
        mmenu =  wx.MenuItem(tmp_menu, wx.NewId(), "Info", "")
        self.Bind(wx.EVT_MENU, self.On_ScreenInfo, mmenu)
        tmp_menu.AppendItem(mmenu)
        self.menubar.Append(tmp_menu, "?")
        self.SetMenuBar(self.menubar)
        for id in self.menu_items:
            self.Bind(wx.EVT_MENU, self.On_Screenitem, self.menu_items[id])
            if self.menu_items[id].GetText() == self.typ: self.menu_items[id].Check(True)
   
    ## create buttons to switch modules 
    def create_modul_buttons(self):
        modules = Afp_ModulNames()
        panel = self.panel
        cnt = 0
        self.button_modules = {}
        for mod in modules:
            self.button_modules[mod] = wx.Button(panel, -1, label=mod, pos=(35 + cnt*80,10), size=(75,30), name="B"+ mod)
            self.Bind(wx.EVT_BUTTON, self.On_ScreenButton, self.button_modules[mod])
            cnt += 1
            if mod == self.typ:
                self.button_modules[mod] .SetBackgroundColour(self.actuelbuttoncolor)
            else:
                self.button_modules[mod] .SetBackgroundColour(self.buttoncolor)

    ## resize grid rows
    # @param name - name of grid
    # @param grid - the grid object
    # @param new_lgh - new number of rows to be populated
    def grid_resize(self, name, grid, new_lgh):
        if new_lgh < self.grid_minrows[name]:
            new_lgh =  self.grid_minrows[name]
        old_lgh = grid.GetNumberRows()
        if new_lgh > old_lgh:
            grid.AppendRows(new_lgh - old_lgh)
        elif  new_lgh < old_lgh:
            for i in range(new_lgh, old_lgh):
                grid.DeleteRows(1)
      
    ## Eventhandler Menu - show info dialog box
    def On_ScreenInfo(self,event):
        if self.debug: print "AfpScreen Event handler `On_ScreenInfo'!"
        AfpReq_Information(self.globals)
      
    ## Eventhandler Menu - switch between screen
    def On_Screenitem(self,event):
        if self.debug: print "AfpScreen Event handler `On_Screenitem'!"
        id = event.GetId()
        item = self.menu_items[id]
        text = item.GetText() 
        #print id, text
        if text == self.typ:
            item.Check(True)
        elif text == "Beenden":
            self.On_Ende(event)
        else:
            # Afp_writeTarget(self.globals, text, self.typ)
            Afp_loadScreen(self.globals, text, self.sb, self.typ)
            self.Close()
        #event.Skip() #invokes eventhandler twice on windows

    ## Enventhandler BUTTON - switch modules
    def On_ScreenButton(self,event):
        if self.debug: print "AfpScreen Event handler `On_ScreenButton'!"
        object = event.GetEventObject()
        name = object.GetName()
        text = name[1:]
        if not text == self.typ:
            Afp_loadScreen(self.globals, text, self.sb, self.typ)
            self.Close()
        #event.Skip() #invokes eventhandler twice on windows
      
 ## Eventhandler BUTTON - quit
    def On_Ende(self,event):
        if self.debug: print "AfpScreen Event handler `On_Ende'!"
        self.Close()
        event.Skip()

    ## Eventhandler Keyboard - handle key-down events
    def On_KeyDown(self, event):
        keycode = event.GetKeyCode()
        if self.debug: print "AfpScreen Event handler `On_KeyDown'", keycode
        #print "AfpScreen Event handler `On_KeyDown'", keycode
        next = 0
        if keycode == wx.WXK_LEFT: next = -1
        if keycode == wx.WXK_RIGHT: next = 1
        if next: self.CurrentData(next)
        event.Skip()
     
    ## Population routines for form and widgets
    def Populate(self):
        self.Pop_text()
        self.Pop_ext()
        self.Pop_grid()
        self.Pop_list()
    ## populate text widgets
    def Pop_text(self):
        for entry in self.textmap:
            TextBox = self.FindWindowByName(entry)
            value = self.sb.get_string_value(self.textmap[entry])
            TextBox.SetValue(value)
    ## populate external file textboxes
    def Pop_ext(self):
        delimiter = self.globals.get_value("path-delimiter")
        for entry in self.extmap:
            filename = ""
            TextBox = self.FindWindowByName(entry) 
            text = self.sb.get_string_value(self.extmap[entry])
            file= Afp_archivName(text, delimiter)
            if file:
                filename = self.globals.get_value("archivdir") + file
                if not Afp_existsFile(filename): 
                    #if self.debug: 
                    print "WARNING in AfpScreen: External file", filename, "does not exists!"
                    filename = ""
            if filename:
                #print "AfpScreen LoadFile", self.extmap[entry], filename
                TextBox.LoadFile(filename)
            else:
                TextBox.Clear()
                #print "AfpScreen SetValue", self.extmap[entry], text
                if text: TextBox.SetValue(text)
        # print "Population routine`Pop_text'!"
    ## populate lists
    def Pop_list(self):
        for entry in self.listmap:
            rows = self.get_list_rows(entry)
            list = self.FindWindowByName(entry)
            if None in rows:
                ind = rows.index(None)
                self.list_id[entry] = rows[ind+1:]
                rows = rows[:ind]
            list.Clear()
            list.InsertItems(rows, 0)
    ## populate grids
    # @param name - if given ,name of grid to be populated 
    def Pop_grid(self, name = None):
        for typ in self.gridmap:
            if not name or typ == name:
                rows = self.get_grid_rows(typ)
                grid = self.FindWindowByName(typ)
                self.grid_resize(typ, grid, len(rows))
                self.grid_id[typ] = []
                row_lgh = len(rows)
                max_col_lgh = grid.GetNumberCols()
                if rows: act_col_lgh = len(rows[0]) - 1
                for row in range(0,row_lgh):
                    for col in range(0,max_col_lgh):
                        if col >= act_col_lgh:
                            grid.SetCellValue(row, col, "")
                        else:
                            grid.SetCellValue(row, col, rows[row][col])
                    self.grid_id[typ].append(rows[row][act_col_lgh])
                if row_lgh < self.grid_minrows[typ]:
                    for row in range(row_lgh, self.grid_minrows[typ]):
                        for col in range(0,max_col_lgh):
                            grid.SetCellValue(row, col,"")
   
    ## reload current data to screen
    def Reload(self):
        self.sb.select_current()
        self.Populate()
         
    ## set current screen data
    # @param plus - indicator to step forwards, backwards or stay
    def CurrentData(self, plus = 0):
        if self.debug: print "AfpScreen.CurrentData", plus
        #self.sb.set_debug()
        if plus == 1:
            self.sb.select_next()
        elif plus == -1:
            self.sb.select_previous()
        self.set_current_record()
        #self.sb.unset_debug()
        self.Populate()

    # routines to be overwritten in explicit class
    ## load additional global data for this Afp-modul
    # default - empty, to be overwritten if needed
    def load_additional_globals(self): # only needed if globals for additonal moduls have to be loaded
        return
    ## set current record to be displayed 
    # default - empty, to be overwritten if changes have to be diffused to other the main database table
    def set_current_record(self): 
        return   
    ## set initial record to be shown, when screen opens the first time
    # default - empty, should be overwritten to assure consistant data on frist screen
    # @param origin - string where to find initial data
    def set_initial_record(self, origin = None):
        return
    ## get identifier of graphical objects, 
    # where the keydown event should not be catched
    # default - empty, to be overwritten if needed
    def get_no_keydown(self):
        return []
    ## get names of database tables to be opened for the screen
    # default - empty, has to be overwritten
    def get_dateinamen(self):
        return []
    ## get rows to populate lists \n
    # default - empty, to be overwritten if grids are to be displayed on screen \n
    # possible selection criterias have to be separated by a "None" value
    # @param typ - name of list to be populated 
    def get_list_rows(self, typ):
        return [] 
    ## get grid rows to populate grids \n
    # default - empty, to be overwritten if grids are to be displayed on screen
    # @param typ - name of grid to be populated
    # - REMARK: last column will not be shown, but stored for identifiction
    def get_grid_rows(self, typ):
        return []
# End of class AfpScreen

## loader roution for Screens
# @param globals - global variables, holding mysql access
# @param modulname - name of modul this screen belongs to, the appropriate modulfile will be imported
# @param sb - AfpSuperbase object which holds the current settings on the mysql tables
# @param origin - value which identifies mysql tableentry to be displayed
# the parameter 'sb' and 'origin' may only be used aternatively
def Afp_loadScreen(globals, modulname, sb = None, origin = None):
    Modul = None
    moduls = Afp_ModulNames()
    if modulname in moduls:
        screen = "Afp" + modulname[:2] + "Screen" 
        modname = "Afp" + modulname + "." + screen 
        #print "Afp_loadScreen:", modname
        pyModul =  Afp_importPyModul(modname, globals)
        #print "Afp_loadScreen:", pyModul
        pyBefehl = "Modul = pyModul." + screen + "()"
        #print "Afp_loadScreen:", pyBefehl
        exec pyBefehl
    if Modul:
        Modul.init_database(globals, sb, origin)
        Modul.Show()
        return Modul
    else:
        return None

# Main   
if __name__ == "__main__":
    text, ok = AfpReq_EditText("Hallo","Wie geht's?")
    #name, ok = AfpReq_FileName()
    #data, ok = AfpReq_Printer()
    print ok, text
    #print ok, name
    #print data
