#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpGlobal
# AfpGlobal module provides global enviroment and modul variables and flags
# it holds the calsses
# - AfpSettings
# - AfpGlobal
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

import tempfile

import AfpUtilities
from AfpUtilities import *
from AfpUtilities.AfpStringUtilities import Afp_toString, Afp_fromString, Afp_pathname, Afp_isIP4
from AfpUtilities.AfpBaseUtilities import *
import AfpBaseRoutines
from AfpBaseRoutines import Afp_getModulInfo

def Afp_setGlobalVars(settings):
   settings["python-version"] = Afp_getGlobalVar("python-version")
   pythonpath = Afp_getGlobalVar("python-path")
   if pythonpath: settings["python-path"] = pythonpath
   settings["op-system"] = Afp_getGlobalVar("op-system")
   settings["net-name"] = Afp_getGlobalVar("net-name")
   settings["path-delimiter"] = Afp_getGlobalVar("path-delimiter")
   settings["homedir"] = Afp_genHomeDir()
   settings["tempdir"] = tempfile.gettempdir()
   settings["today"] = Afp_getToday()
   return settings
def Afp_iniGlobalVars(settings):
   if not "database" in settings:
      settings["database"] = "BusAfp"
   if not "database-user" in settings:
      settings["database-user"] = "server"      
   #if not "database-word" in settings:
      #settings["database-word"] = "busse".encode('base64')
   if not "database-host" in settings:
      settings["database-host"] = "127.0.0.1"
   if not "Umst" in settings:
      settings["Umst"] = 19
   # decode password for database, when loaded from file
   if "database-word" in settings:
      settings["database-word"] = settings["database-word"].decode('base64')
   if not "afpdir" in settings:
      settings["afpdir"] = settings["homedir"]
   if not "templatedir" in settings:
      settings["templatedir"] = settings["afpdir"] + "template" + settings["path-delimiter"]
   if not "archivdir" in settings:
      settings["archivdir"] = settings["afpdir"] + "Archiv" + settings["path-delimiter"]
   if not "Standartort" in settings:
      settings["Standartort"] = "Braunschweig"
   # set default file handles (not needed for windows)
   if not "office" in settings:
      settings["office"] = "libreoffice"
   if not ".odt" in settings:
      settings[".odt"] = "libreoffice"
   if not ".fodt" in settings:
      settings[".fodt"] = "libreoffice"
   if not ".txt" in settings:
      settings[".txt"] = "vim"
   return settings

class AfpSettings(object):
   def  __init__(self, debug, conf_path = None, modulname = None, homedir = None):
      print "AfpSettings.init:", debug, conf_path, modulname, homedir
      self.debug = debug
      self.modul = None
      self.config = conf_path       
      self.settings = {}
      if modulname : self.modul = modulname 
      else: self.settings = Afp_setGlobalVars(self.settings)
      if self.config is None or self.config == "":
         if self.modul is None:
            self.config = Afp_addPath(self.settings["homedir"], "AfpBase.cfg")
         elif homedir:
            self.config = Afp_addPath(homedir, "Afp" + self.modul + ".cfg")
      if not Afp_existsFile(self.config):
         Afp_genEmptyFile(self.config)
      #print self.config
      # read variables from configuratioin file
      self.read(self.config)
      self.set_pathdelimiter()       
      if self.modul is None:
         self.settings = Afp_iniGlobalVars(self.settings)
      else:
         # load variables from database
         # self.load(modulname)
         print "AfpSettings.load(" + modulname + ") not implemented!"
      if self.debug: print "AfpSettings Konstruktor",self.modul
   def __del__(self):
      if self.debug: print "AfpSettings Destruktor",self.modul
   def is_debug(self):
      return self.debug
   def set_pathdelimiter(self):
      # convention: names of folder pathes end with "dir" (directory)
      for entry in self.settings:
         if entry[-3:] == "dir":
            self.settings[entry] = Afp_pathname(self.settings[entry], Afp_getGlobalVar("path-delimiter"))
   def read(self, path):
      if self.debug: print "AfpSettings.read:", path
      fin = open(path , 'r') 
      for line in fin:
         cline = line.split("#")
         sline = cline[0].split("=",1)
         if len(sline) > 1:
            if self.debug: print "AfpSettings.read:", line[:-1]
            name = sline[0].strip()
            value = self.fromString(sline[1].strip())
            #print name, value
            self.set(name, value)
      fin.close()
   #def load(self, modul):
   def fromString(self, string):
      #take care of special setting possibillities before conversion
      if self.evalString(string):
         befehl = "value = " + string
         exec befehl
      elif self.keepString(string):
         value = string
      else:
         value = Afp_fromString(string)
      return value
   def keepString(self, string):
      # identifiy special strings to be not interpreted and converted to other data types
      if Afp_isIP4(string): # IP4 Adresses
         return True
      # windows pathnames with ":" in second place
      if len(string) > 1 and string[1] == ":" and not string[0].isdigit():
         return True
      return False
   def evalString(self, string):
      if string[0] == "{" and string[-1] == "}":
         return True
      if string[0] == "[" and string[-1] == "]":
         return True
      return False
   def set(self, name, value):
      #print name, value
      self.settings[name] = value
   def exists_key(self, name):
      return name in self.settings
   def get_keys(self):
      return self.settings.keys()
   def get(self, name):
      if name in self.settings: return self.settings[name]
      else: return None

class AfpGlobal(object):
   def  __init__(self, name, mysql, setting):
      self.mysql = mysql
      self.setting = setting
      self.setting.set("name", name)
      self.debug = self.setting.is_debug()
      self.settings = {}
      if self.debug: print "AfpGlobal Konstruktor"
   def __del__(self):
      if self.debug: print "AfpGlobal Destruktor"
   def is_debug(self):
      return self.debug
   def get_mysql(self):
      return self.mysql
   def add_setting(self, module, setting):
      self.settings[module] = setting
   def get_setting(self, module = None):
      if module is None: return self.setting   
      if module in self.settings: return self.settings[module]
      return None
   def set_value(self, name, value, module = None):
      set = self.get_setting(module)
      if set is None and module:
         set = AfpSettings(self.is_debug(), None, module, self.get_value("homedir"))
         self.add_setting(module, set)
      if set and name:
         set.set(name, value)
   def set_infos(self,  version = None, copyright = None, website = None, description = None, license = None, picture = None, developer = None):
      if version: self.set_value("version", version)
      if copyright: self.set_value("copyright", copyright)
      if website: self.set_value("website", website)
      if description: self.set_value("description", description)
      if license: self.set_value("license", license)
      if picture: self.set_value("picture", picture)
      if developer: self.set_value("developer", developer)
   def get_string_value(self, name, module = None):
      value = self.get_value(name, module)
      return Afp_toString(value)
   def get_value(self, name, module = None):
      set = self.get_setting(module)
      return set.get(name)
   def view(self):
      # convenience routine for debug purpose
      print "AfpGlobal.view: Global", self.setting.settings
      for set in self.settings: 
         print  "AfpGlobal.view:", self.settings[set].modul, self.settings[set].settings
   def os_is_windows(self):
      op_sys = self.get_value("op-system")
      is_win = "win" in op_sys or "Win" in op_sys
      return is_win
   # special retrieve routines
   def get_host_header(self):
      return "auf " + self.get_value("database-host") + ", User: \""  + self.get_value("database-user") + "\""
   def get_modul_infos(self):
      infos = ""
      for set in self.settings:
         setting = self.settings[set]
         if setting.modul:
            if not "Info" in setting.settings:
               pythonpath = self.get_value("python-path")
               if not pythonpath: pythonpath = self.get_value("start-path")
               setting.settings["Info"] = Afp_getModulInfo(setting.modul, self.get_value("path-delimiter"), pythonpath)
            infos += setting.get("Info")
      return infos
   # shortcuts to common flags and variables
   def skip_accounting(self):
      if self.get_value("skip_accounting"): return True
      else: return False
   def today(self):
      return self.get_value("today")
      
# Main   
if __name__ == "__main__":
   setting = AfpSettings(False)
   keys = setting.get_keys()
   print "Start"
   for key in keys:
      print key, setting.get(key)
   print "Ende"
