#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpBaseDialog
# AfpBaseDialog module provides wrapper for the base Dialog-Requesters delivered by wx, 
#                         as well as the dialog base classes for all dialogs.
# it holds the calsses
# - AfpDialog_MultiLine - multi line editing dialog
# - AfpDialog_TextEditor - common text editor dialog
# - AfpDialog_DiAusw - common selection dialog for unlimited choices
# - AfpDialog - dialog base class
#
#   History: \n
#        05 Mar. 2015 - move screen base class to separate file - Andreas.Knoblauch@afptech.de \n
#        26 Feb. 2015 - move common dialogs to AfpBaseDialogCommon - Andreas.Knoblauch@afptech.de \n
#        19 Okt. 2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        30 Nov. 2012 - inital code generated - Andreas.Knoblauch@afptech.de

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

import AfpUtilities.AfpBaseUtilities
from AfpUtilities.AfpBaseUtilities import Afp_isTime, Afp_isDate, Afp_isNumeric
import AfpUtilities.AfpStringUtilities
from AfpUtilities.AfpStringUtilities import Afp_addRootpath, Afp_toString, Afp_toInternDateString, Afp_fromString, Afp_ChDatum
   
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
# @param label1 - text to be displayed on first line of the dialog
# @param label2 - text to be displayed on second line of the dialog
# @param label_low - text to be displayed below text, aboe buttons
# @param direct - flag that dialog is directliy set to 'modify' instead of 'read'
# @param size - size of dialog window (may differ for different purposes)
def AfpReq_EditText(oldtext = "", header = "TextEditor", label1 = None, label2 = None, label_low = None, direct = False, size = (500, 300)):
    dialog =  AfpDialog_TextEditor(None, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    dialog.attach_text(header, oldtext, label1, label2, label_low, size)
    if direct: dialog.set_direct_editing()
    dialog.ShowModal()
    newtext = None
    if dialog.get_Ok():
        newtext = dialog.get_text()
    dialog.Destroy()
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
    dialog = AfpDialog_MultiLines(None, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
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
    if not wild: wild = "*.*"
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
 
## Baseclass Texteditor Requester 
class AfpDialog_TextEditor(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_TextEditor, self).__init__(*args, **kw) 
        self.Ok = False
        self.readonlycolor = self.GetBackgroundColour()
        self.editcolor = (255,255,255)
        self.label_text_1 = wx.StaticText(self, 1, name="label1")        
        self.label_text_2 = wx.StaticText(self, 2, name="label2")
        self.label_lower = wx.StaticText(self, 2, name="label_lower")
        self.text_text = wx.TextCtrl(self, 3, style=wx.TE_MULTILINE)
        self.choice_Edit = wx.Choice(self, -1, choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
        self.choice_Edit.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
        self.button_Ok = wx.Button(self, -1, label="&Ok", name="Ok")
        self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
        self.lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.choice_Edit,2,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Ok,2,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.inner_sizer=wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.Add(self.label_text_1,0,wx.EXPAND)
        self.inner_sizer.Add(self.label_text_2,0,wx.EXPAND)
        self.inner_sizer.Add(self.text_text,1,wx.EXPAND)
        self.inner_sizer.Add(self.label_lower,0,wx.EXPAND)
        self.inner_sizer.Add(self.lower_sizer,0,wx.EXPAND)
        self.inner_sizer.AddSpacer(10)
        self.sizer=wx.BoxSizer(wx.HORIZONTAL)  
        self.sizer.AddSpacer(10)     
        self.sizer.Add(self.inner_sizer,1,wx.EXPAND)
        self.sizer.AddSpacer(10)    
        self.SetSizerAndFit(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.On_CEdit()
    ## attach header, text and size to dialog
    # @param header - text to be displayed in the window top ribbon
    # @param text - text to be displayed and manipulated
    # @param label1 - text to be displayed on first line above editorfield
    # @param label2 - text to be displayed on secpond line above editorfield
    # @param label_low - text to be displayed on below editorfield
    # @param size - size of dialog
    def attach_text(self, header, text, label1, label2, label_low, size):
        self.SetSize(size)
        self.SetTitle(header)
        self.text_text.SetValue(text)
        if label1: self.label_text_1.SetLabel(label1)
        if label2: self.label_text_2.SetLabel(label2)
        if label_low: self.label_lower.SetLabel(label_low)
    ## set the dialog edit modus
    def set_direct_editing(self):
        self.choice_Edit.SetSelection(1)
        self.text_text.SetEditable(True)
        self.text_text.SetBackgroundColour(self.editcolor) 
    ## return Ok flag, to be called in calling routine
    def get_Ok(self):
        return self.Ok
    ## return actuel text, to be called in calling routine
    def get_text(self):
        ret_text = self.text_text.GetValue()
        print "AfpDialog_TextEditor.get_text:", ret_text
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
        self.lower_sizer.Add(self.button_Cancel,3,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Delete,3,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Ok,3,wx.EXPAND)
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
                self.sizers[-1].Add(self.label[-1],5,wx.EXPAND)
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
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.lower_sizer, 0, wx.EXPAND)
        self.sizer.AddSpacer(10)
        #self.SetSizer(self.sizer)
        self.SetSizerAndFit(self.sizer)
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
        #style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        super(AfpDialog, self).__init__(*args, **kw) 
        self.Ok = False
        self.new = False
        self.debug = False
        self.data = None
        self.lock_data = False
        self.panel = None
        self.sizer = None
        self.reload = None
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
    # @param parent - parent wx class (panel or sizer) where widgest should be attached to
    # @param edit - coordinates [0][1] and size [2][3] of edit widget on panel \n
    #                        weight of space left [0] and right [2] and [1] weight of edit widget in sizer
    # @param ok - coordinates [0][1] and size [2][3] of ok widget on panel \n
    #                       weight of space left [0] and right [2] and [1] weight of ok widget in sizer
    def setWx(self, parent, edit, ok):
        if parent is None: return
        if type(parent) == wx._windows.Panel: # parent is a panel
            self.choice_Edit = wx.Choice(parent, -1, pos=(edit[0], edit[1]), size=(edit[2], edit[3]), choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
            self.choice_Edit.SetSelection(0)
            self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
            self.button_Ok = wx.Button(parent, -1, label="&Ok", pos=(ok[0], ok[1]), size=(ok[2], ok[3]), name="Ok")
            self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
        else: # parent is a sizer
            self.choice_Edit = wx.Choice(self, -1, choices=["Lesen", "Ändern".decode("UTF-8"), "Abbruch"], style=0, name="CEdit")
            self.choice_Edit.SetSelection(0)
            self.Bind(wx.EVT_CHOICE, self.On_CEdit, self.choice_Edit)
            self.button_Ok = wx.Button(self, -1, label="&Ok", name="Ok")
            self.Bind(wx.EVT_BUTTON, self.On_Button_Ok, self.button_Ok)
            parent.AddStretchSpacer(edit[0])
            parent.Add(self.choice_Edit,edit[1],wx.EXPAND)
            parent.AddStretchSpacer(edit[2] + ok[0])
            parent.Add(self.button_Ok,ok[1],wx.EXPAND)
            parent.AddStretchSpacer(ok[2])
      
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
    ## routine for reloading data into display, \n
    # optional loading data from database before
    def re_load(self):
        #print "re_load:", self.reload
        if self.reload: 
            if type(self.reload) == bool:
               selnames = self.data.get_selection_names()
            else:
                selnames = self.reload
            for sel in selnames:
                self.data.reload_selection(sel)
        self.Populate()
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
        if not editable: self.re_load()
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
          
## Base class for dialog for the commen unrestricted selection of data from a database table \n
# the following routines must be supplied in the derived class: \n
#  "self.get_grid_felder()"      for selection grid population \n
#  "self.invoke_neu_dialog()" to generate a new database entry
class AfpDialog_Auswahl(wx.Dialog):
    ## constructor
    def __init__(self, *args, **kw):
        super(AfpDialog_Auswahl, self).__init__(*args, **kw) 
        # values from call
        self.mysql = None
        self.globals = None
        self.debug = False
        self.datei = None
        self.modul = None
        self.index = None
        self.select = None
        self.where = None  
        self.search = None  
        self.sizer = None
        # inital values      
        self.rows = 7
        self.new_rows = self.rows
        self.fixed_width = 70
        self.fixed_height = 110
        self.grid_data = None
        # for internal use
        self.used_modul = None
        self.cols = 1
        self.col_percents = []
        self.col_labels = []
        self.feldindex = []
        self.feldlist = ""
        self.dateien = ""
        self.textmap = []
        self.sortname = ""
        self.selectname = ""
        self.valuecol = -1 
        self.link = None  
        self.ident = [None]
        self.offset = 0
        # for the result
        self.result_index = -1
        self.result = None

        self.InitWx()
        self.SetTitle("--Variable-Text--")
        height = self.GetSize()[1] - self.fixed_height
        self.row_height = height/self.rows 
        #print "New:", self.GetSize(), height, self.row_height, self.rows, self.new_rows
        self.Bind(wx.EVT_SIZE, self.On_ReSize)

    ## set up dialog widgets      
    def InitWx(self):
        self.label_Auswahl = wx.StaticText(self, 1, label="-- Bitte Datensatz auswählen --".decode("UTF-8"), name="Auswahl")
        
        self.button_First = wx.Button(self, -1, label="|<", size=(30,28), name="First")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_First, self.button_First)
        self.button_PPage = wx.Button(self, -1, label="&<<", size=(30,28), name="PPage")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_PPage, self.button_PPage)
        self.button_Minus = wx.Button(self, -1, label="&<", size=(30,28), name="Minus")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Prev, self.button_Minus)
        self.button_Plus = wx.Button(self, -1, label="&>", size=(30,28), name="Plus")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Next, self.button_Plus)
        self.button_NPage = wx.Button(self, -1, label="&>>", size=(30,28), name="NPage")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_NPage, self.button_NPage)
        self.button_Last = wx.Button(self, -1, label=">|", size=(30,28), name="Last")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Last, self.button_Last)
        box = wx.StaticBox(self, size=(40, 212))
        self.right_sizer =wx.StaticBoxSizer(box, wx.VERTICAL)
        self.right_sizer.AddStretchSpacer(1)      
        self.right_sizer.Add(self.button_First,0,wx.EXPAND)        
        self.right_sizer.Add(self.button_PPage,0,wx.EXPAND)        
        self.right_sizer.Add(self.button_Minus,0,wx.EXPAND)        
        self.right_sizer.Add(self.button_Plus,0,wx.EXPAND)        
        self.right_sizer.Add(self.button_NPage,0,wx.EXPAND)        
        self.right_sizer.Add(self.button_Last,0,wx.EXPAND)        
        self.right_sizer.AddStretchSpacer(1) 
        
        self.grid_auswahl = wx.grid.Grid(self, -1, style=wx.FULL_REPAINT_ON_RESIZE | wx.ALWAYS_SHOW_SB, name="Auswahl")
        self.extract_grid_column_values()
        self.grid_auswahl.CreateGrid(self.rows, self.cols)
        self.grid_auswahl.SetRowLabelSize(0)
        self.grid_auswahl.SetColLabelSize(18)
        self.grid_auswahl.EnableEditing(0)
        #self.grid_auswahl.EnableDragColSize(0)
        self.grid_auswahl.EnableDragRowSize(0)
        self.grid_auswahl.EnableDragGridSize(0)
        self.grid_auswahl.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)   
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid_auswahl.SetReadOnly(row, col)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_LEFT_CLICK, self.On_LClick, self.grid_auswahl)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_LEFT_DCLICK, self.On_DClick, self.grid_auswahl)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_RIGHT_CLICK, self.On_RClick, self.grid_auswahl)

        self.left_sizer =wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer.Add(self.grid_auswahl,10,wx.EXPAND)        
        
        self.button_Suchen = wx.Button(self, -1, label="&Suchen", name="Suchen")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Suchen, self.button_Suchen)
        self.button_Neu = wx.Button(self, -1, label="&Neu", name="Neu")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Neu, self.button_Neu)
        self.button_Abbruch = wx.Button(self, -1, label="&Abbruch", name="Abbruch")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Abbruch, self.button_Abbruch)
        self.button_Okay = wx.Button(self, -1, label="&OK", name="Okay")
        self.Bind(wx.EVT_BUTTON, self.On_Ausw_Ok, self.button_Okay)
        self.lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Suchen,0,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Neu,0,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(4)
        self.lower_sizer.Add(self.button_Abbruch,0,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        self.lower_sizer.Add(self.button_Okay,0,wx.EXPAND)
        self.lower_sizer.AddStretchSpacer(1)
        # compose sizers
        self.mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mid_sizer.Add(self.left_sizer,1,wx.EXPAND)        
        self.mid_sizer.AddSpacer(10)
        self.mid_sizer.Add(self.right_sizer,0,wx.EXPAND)
        self.mid_sizer.AddSpacer(10)
        self.sizer = wx.BoxSizer(wx.VERTICAL)        
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.label_Auswahl,0,wx.EXPAND)        
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.mid_sizer,1,wx.EXPAND)
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.lower_sizer,0,wx.EXPAND)
        self.sizer.AddSpacer(10)
        
        #self.adjust_grid_rows()
        self.SetSizerAndFit(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
    ## extract witdh, names and values for columns
    def extract_grid_column_values(self): 
         # initialize grid
        felder = self.get_grid_felder()
        #print "AfpDialog_Auswahl.extract_grid_column_values:", felder
        self.feldindex = []        
        self.feldlist = ""
        self.selectname = ""
        if "=" in felder[-1][0]:
            self.link = felder[-1][0]
            lsplit =  self.link.split()
            felder[-1][0] = lsplit[-1]
        lgh = len(felder)
        skip = False
        percent = 0
        name = ""
        for i in range(0,lgh):
            feld = felder[i][0]    
            self.feldindex.append(len(self.col_labels))
            self.feldlist += feld + "," 
            if not felder[i][1] is None:
                new_percent = felder[i][1]
                if skip:  percent += new_percent
                fsplit = feld.split(".") 
                if i == 0:  self.selectname = fsplit[0] + "." + fsplit[1]
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
                        self.valuecol = len(self.col_percents)
                    self.col_labels.append(name)
                    self.col_percents.append(percent)
                    percent = 0
                name = new_name
                if not skip: # direct write
                    self.col_labels.append(fsplit[0])
                    self.col_percents.append(new_percent)
                if not fsplit[1].upper() in self.dateien:
                    self.dateien += " " + fsplit[1].upper()
        self.feldlist = self.feldlist[:-1]
        self.cols = len(self.col_percents) 
    ## adjust grid rows and columns for dynamic resize of window            
    def adjust_grid_rows(self):
        if self.new_rows > self.rows:
            self.grid_auswahl.AppendRows(self.new_rows - self.rows)
            #print "AfpDialog_Auswahl.adjust_grid_rows Add:", self.new_rows - self.rows, self.grid_auswahl.GetNumberRows()
            self.rows = self.new_rows       
            for row in range(self.rows, self.new_rows):
                for col in range(self.cols):
                    self.grid_auswahl.SetReadOnly(row, col)
        elif self.new_rows < self.rows:
            for i in range(self.rows - self.new_rows):
                self.grid_auswahl.DeleteRows(1)
            #print "AfpDialog_Auswahl.adjust_grid_rows Del:", self.rows - self.new_rows, self.grid_auswahl.GetNumberRows()
            self.rows = self.new_rows
        grid_width = self.GetSize()[0] - self.fixed_width
        print "AfpDialog_Auswahl.adjust_grid_rows Width:", grid_width, self.col_percents
        if self.col_percents:
            for col in range(self.cols):  
                self.grid_auswahl.SetColLabelValue(col, self.col_labels[col])
                if col < len(self.col_percents):
                    self.grid_auswahl.SetColSize(col, self.col_percents[col]*grid_width/100)
    ## initialisation of  the dialog \n
    # set up grid, attach data
    # @param globals - global variables including database connection
    # @param index - name of column for sorting values
    # @param value - actuel index value for this selection
    # @param where - filter for this selection
    # @param text - text to be displayed above selection list
    def initialize(self, globals, index, value, where, text): 
        print "AfpDialog_Auswahl.initialize Index:", index, "Value:", value, "Where:", where, "Text:", text
        value = Afp_toInternDateString(value)
        self.globals = globals
        self.mysql = globals.get_mysql()
        self.debug = self.mysql.get_debug()
        self.index = index
        self.search = value
        if self.datei and not self.datei in self.dateien:
            self.dateien += " " + self.datei.upper()
        self.dateien = self.dateien.strip()
        # initialize grid
        if self.globals.os_is_windows():
            self.new_rows = int(1.4 * self.rows)
            height = self.GetSize()[1] - self.fixed_height
            self.row_height = height/self.new_rows 
        indexcol = -1
        split = self.feldlist.split(",")
        for ind, feld in enumerate(split):   
            if self.index + "." in feld: indexcol = ind
        if indexcol > -1:
            self.selectname =  self.index + "." + self.datei
            self.sortname = ""
            self.valuecol = indexcol
        if not self.sortname: 
            self.sortname =   self.selectname
            self.SetTitle("Auswahl " +  self.datei.capitalize() + " Sortierung: " + self.selectname.split(".")[0])
        else:
            self.SetTitle("Auswahl " +  self.datei.capitalize() + " Sortierung: " + self.sortname)
        if text: self.label_Auswahl.SetLabel(text)
        if not value == "":
            self.select = self.selectname  + " >= \"" + value + "\""
        self.where = where
        self.set_size()
        self.adjust_grid_rows()
        self.Pop_grid()
        if not self.grid_is_complete(): # grid not filled comletely, go for last entries
            self.On_Ausw_Last()
    ## set size depending on different glabal variables
    def set_size(self, size = None):
        if size is None:
            size = self.globals.get_value(self.typ + "_Size", self.modul)
            if size is None:
                size = (560,281)
        if size: 
            self.SetSize(size)
    ## populate selection grid
    def Pop_grid(self, dynamic = False):
        limit = str(self.offset) + ","+ str(self.rows)      
        if dynamic:
            if self.grid_data is None or len(self.grid_data) != self.rows:
                self.grid_data = self.mysql.select(self.feldlist, self.select, self.dateien, self.sortname, limit, self.where, self.link)
            rows = self.grid_data
        else:
            rows = self.mysql.select(self.feldlist, self.select, self.dateien, self.sortname, limit, self.where, self.link)
        lgh = len(rows)
        self.ident = []
        #print "AfpDialog_Auswahl.Pop_grid lgh:", lgh, self.rows, self.cols, self.grid_auswahl.GetNumberRows(), self.grid_auswahl.GetNumberCols() 
        for row in range(0, self.rows):
            for col in range(0,self.cols): 
                #print "AfpDialog_Auswahl.Pop_grid indices:", row, col
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
        #print "AfpDialog_Auswahl.set_step_back In:", step, last
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
        #print "AfpDialog_Auswahl.set_step_back Out:", offset, step, self.offset
    ## return result
    def get_result(self):
        return self.result
 
    # Event Handlers 
    ## event handler for resizing window
    def On_ReSize(self, event):
        height = self.GetSize()[1] - self.fixed_height
        self.new_rows = int(height/self.row_height)
        #print "AfpDialog_Auswahl.Resize:", size, height, self.row_height, self.rows, self.new_rows
        self.adjust_grid_rows()
        self.Pop_grid(True)
        event.Skip()   
    ## event handler for the Left Mouse Click 
    def On_LClick(self, event): 
        if self.debug: print "Event handler `On_LClick'"
        self.result_index = event.GetRow()
        event.Skip()   
    ## event handler for the Left Mouse Double Click
    def On_DClick(self, event): 
        if self.debug: print "Event handler `On_DClick'"
        self.result_index = event.GetRow()
        self.On_Ausw_Ok()
        event.Skip()
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
    def On_Ausw_Ok(self, event = None):
        if self.debug: print "Event handler `On_Ausw_Ok'"
        if self.result_index > -1:
            self.result = self.ident[self.result_index]
        if self.globals.get_value("enable_size_memory"):
            self.globals.set_value(self.typ + "_Size", self.GetSize(), self.modul)
        if event: event.Skip()
        self.Destroy()
      
    # routines to be overwritten for customisation
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
    # If different tables are involved the 'Ident column' string must hold the connection formular. \n
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
