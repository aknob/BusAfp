#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package BusAfp
# BusAfp is a software to manage coach and travel acivities \n
#    Copyright (C) 1989 - 2015  afptech.de (Andreas Knoblauch) \n
# \n
#   History: \n
#        19 Okt.2014 - adapt package hierarchy - Andreas.Knoblauch@afptech.de \n
#        30 Nov.2012 - inital code generated - Andreas.Knoblauch@afptech.de

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
import sys
import os.path
import AfpBase
from AfpBase import AfpDatabase, AfpBaseDialog, AfpBaseScreen ,AfpGlobal
from AfpBase.AfpDatabase import AfpSQL

## main class to invoke BusAfp Software
class BusAfp(wx.App):
    ## initialize mysql connection, global variables and application
    # @param debug - flag for debug information
    # @param startpath - path where BusAfp has been started from
    # @param confpath - path to configuration file
    # @param dbhost - host for database
    # @param dbuser - user on host for database
    # @param dbword - password for user on host for database
    def initialize(self, debug, startpath, confpath, dbhost, dbuser, dbword): 
        name = 'BusAfp'
        version = "6.0.1 alpha"       
        copyright = '(C) 1989 - 2015 AfpTech.de'
        website = 'http://www.busafp.de'
        description = """BusAfp ist eine Verwaltungsprogramm für den Buseinsatz 
        für Mietfahrten, sowie der Organisation von eigenen Reisen.
        Es enthält eine mitgeführte Buchhaltung, Zahlungsverfolgung, Einsatzplanung
        und diverse weiter nützliche Hilfsmittel.""".decode("UTF-8")
      
        license = """BusAfp ist eine freie Software, sie kann weiterverteilt und 
        modifiziert werden, gemäß den Bestimmungen der 
        'GNU General Public License' wie von der  'Free Software Foundation' 
        in Version 3 oder höher veröffentlicht,
        Da diese Lizenz nicht in Deutsch zur Verfügung steht folgt hier die 
        rechtssichere englische Version:
      
         BusAfp is a software to manage coach and travel acivities
         Copyright (C) 1989 - 2015  afptech.de (Andreas Knoblauch)

         This program is free software: you can redistribute it and/or modify
         it under the terms of the GNU General Public License as published by
         the Free Software Foundation, either version 3 of the License, or
         (at your option) any later version.
         This program is distributed in the hope that it will be useful, but
         WITHOUT ANY WARRANTY; without even the implied warranty of
         MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
         See the GNU General Public License for more details.
         You should have received a copy of the GNU General Public License
         along with this program.  If not, see <http://www.gnu.org/licenses/>.
         """.decode("UTF-8") 
        picture = 'Bus_relief.png'
        developers = "Andreas Knoblauch - initiale Version".decode("UTF-8")
       
        self.globals = None
        self.module = None
        set = AfpBase.AfpGlobal.AfpSettings(debug, confpath)   
        if startpath: set.set("start-path", startpath)
        if dbhost: set.set("database-host", dbhost)      
        if dbuser: set.set("database-user", dbuser)      
        if not set.exists_key("database-word") and dbword is None:
            if dbuser is None: dbuser = set.get("database-user")
            dbword, ok = AfpBase.AfpBaseDialog.AfpReq_Text("Für die Verbindung zur Datenbank wird eine Authentifizierung benötigt!".decode("UTF-8"),"Bitte das Passwort für den Benutzer '".decode("UTF-8") + dbuser+ "' eingeben:","","Passwort Eingabe",True)
        if not dbword is None: set.set("database-word", dbword)
        mysql = AfpBase.AfpDatabase.AfpSQL.AfpSQL(set.get("database-host"), set.get("database-user"), set.get("database-word"), set.get("database"), set.is_debug())
        self.globals = AfpBase.AfpGlobal.AfpGlobal(name, mysql, set)
        self.globals.set_infos(version, copyright, website, description, license, picture, developers)
        wx.InitAllImageHandlers()
    
    ## load appropriate modul     
    # @param modulname - afp-modul name to be loaded
    def load_module(self, modulname):
        Modul = AfpBase.AfpBaseScreen.Afp_loadScreen(self.globals, modulname)
        if Modul: 
            self.SetTopWindow(Modul)
            return True
        else:
            return False
# end of class BusAfp

# main program
debug = False
execute = True
confpath = ""
module = "Adresse"
dbhost= None
dbuser = None
dbword = None
lgh = len(sys.argv)
ev_indices = []
startpath = os.path.dirname(os.path.abspath(sys.argv[0]))
for i in range(1,lgh):
    if sys.argv[i] == "-p" or sys.argv[i] == "--password": 
        ev_indices.append(i+1)
        if i < lgh-1 and not "-" in sys.argv[i+1]: dbword = sys.argv[i+1]
    if sys.argv[i] == "-s" or sys.argv[i] == "--server": 
        ev_indices.append(i+1)
        if i < lgh-1 and not "-" in sys.argv[i+1]: dbhost= sys.argv[i+1]
    if sys.argv[i] == "-u" or sys.argv[i] == "--user": 
        ev_indices.append(i+1)
        if i < lgh-1 and not "-" in sys.argv[i+1]: dbuser = sys.argv[i+1] 
    if sys.argv[i] == "-m" or sys.argv[i] == "--module": 
        ev_indices.append(i+1)
        if i < lgh-1 and not "-" in sys.argv[i+1]: module = sys.argv[i+1]
    if sys.argv[i] == "-v" or sys.argv[i] == "--verbose": debug = True
    if sys.argv[i] == "-h" or sys.argv[i] == "--help": execute = False
if execute:
    if lgh > 1 and not "-" in sys.argv[lgh-1] and not lgh-1 in ev_indices: confpath = sys.argv[lgh-1]
    BusAfp = BusAfp(0)
    BusAfp.initialize(debug, startpath, confpath, dbhost, dbuser, dbword)
    loaded = BusAfp.load_module(module)
    if loaded:
        BusAfp.MainLoop()
    else:
        print "ERROR: BusAfp Modul '" + module + "' not available!"
else:
    print "usage: BusAfp [option] [file]"
    print "Options and arguments:"
    print "-h,--help      display this text"
    print "-m,--module    module to be started follows"
    print "               Default: module \"Adresse\" will be invoked"
    print "-p,--password  plain text password for mysql authentification follows"
    print "               Default: password has to be entered during program start"
    print "-s,--server    database servername or IP-address follows"
    print "               Default: loclahost (127.0.0.1) will be used"
    print "-u,--user      user for mysql authentification follows"
    print "               Default: user \"server\" will be used"
    print "-v,--verbose   display comments on all actions (debug-information)"
    print "file           configuration read from python script file"
   