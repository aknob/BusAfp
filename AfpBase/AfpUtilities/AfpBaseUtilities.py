#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpUtilities.AfpBaseUtilities
# AfpBaseUtilities module provides general solely python dependend utilitiy routines
# it does not hold any classes
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


import sys
import os.path
import os
import platform
import datetime
import logging
import shutil

##  get system infos
# @param name - name of value to be extracted
def Afp_getGlobalVar(name):
   if name == "python-version": return sys.version
   if name == "python-path":
      if 'PYTHONPATH' in os.environ:
         return os.environ['PYTHONPATH'].split(os.pathsep)[0]  
      else:
         return None
   if name == "op-system": return platform.system()
   if name == "net-name": return platform.node()
   if name == "path-delimiter": return os.sep
   return None
## type check 'numeric'
def Afp_isNumeric(wert):
   typ = type(wert)
   if typ == int: return True
   if typ == long: return True
   if typ == float: return True
   if typ == datetime.date: return True
   return False
## type check 'date'
def Afp_isDate(wert):
   return type(wert) == datetime.date
## type check 'time'
def Afp_isTime(wert):
   if type(wert) == datetime.datetime: return True
   if type(wert) == datetime.time: return True
   if type(wert) == datetime.timedelta: return True
   return False
   
## numerical check +- eps
# @param value - value to be checked
# @param eps   -  value has to be numerical and abs(value) > eps 
def Afp_isEps(value, eps = 0.01):
   if Afp_isDate(value): return False
   if Afp_isNumeric(value):
      return (value >= eps or value <= -eps)
   else:
      return False
      
## extract values from array (list)
# @param indices - indices of values to be extracted from array, None all entries are extracted
# @param array- list of values
def Afp_extractPureValues(indices, array):
   #print "Afp_extractPureValues:",indices, array
   if indices is None:
      werte = []
      for entry in array:
         werte.append(entry)
   else:
      werte = []
      for ind in indices:
         werte.append(array[ind])
   return werte
   
   # date routines
def Afp_getToday():
   return datetime.date.today()
def Afp_addDaysToDate(date, ndays, sign = "+"):
   if sign == "-":
      newdate = date -  datetime.timedelta(days=ndays)
   else:
      newdate = date +  datetime.timedelta(days=ndays)
   return newdate
def Afp_diffDays(start, ende):
   diff = ende - start
   return diff.days
def Afp_toTime(timedelta):
   if  type(timedelta) != datetime.timedelta: return datetime.time()
   hours = int(timedelta.total_seconds()/3600)
   minutes = int((timedelta.total_seconds() - 3600*hours)/60)
   return datetime.time(hours, minutes)
def Afp_toTimedelta(time, complement = False):
   if time is None: return datetime.timedelta()
   if  type(time) == datetime.timedelta: return time
   if not Afp_isTime(time): return datetime.timedelta()
   hour = time.hour
   minute = time.minute
   second = time.second
   micro = time.microsecond
   if complement:
      hour = 24 - hour
      minute = 60 -  minute
      if minute < 60: hour -= 1
      else: minute = 0
      second = 60 - second
      if second < 60: 
         minute -= 1
         if minute < 0:
            hour -= 1
            minute = 60 - minute
      else: second = 0
      micro = 1000000 - micro
      if micro < 1000000:
         second -= 1
         if second < 0:
            minute -= 1
            second = 60 - second
            if minute < 0:
               hour -= 1
               minute = 60 - minute
      else:
         micro = 0
   return datetime.timedelta(hours=hour, minutes=minute, seconds=second, microseconds=micro)
def Afp_TimeToFloat(time, end = False):
   value = 0.0
   mins = 0.0
   if type(time) == datetime.timedelta: time = Afp_toTime(time)
   if type(time) == datetime.time: 
      value = float(time.hour)
      mins = time.minute/60.0
   if end: 
      value = 24.0 -  value
      value -= mins
   else: 
      value += mins
   return value
def Afp_floatHoursToTime(fhours):
   hours = int(fhours)
   mins = int((fhours - hours)*60)
   time = datetime.timedelta(hours=hours, minutes=mins)
   return time
def Afp_plusTime(time1, time2):
   time = datetime.timedelta()
   if time1: time += time1
   if time2: time += time2
   return time
def Afp_daysFromTime(timedelta, day = None, hday = None):
   days = float(timedelta.days)
   secs = timedelta.total_seconds()
   #print "Afp_daysFromTime input", timedelta, days, secs
   std = 3600
   tag = 24*std
   secs_h = secs - days*tag
   hours = float(secs_h/std)
   #print "Afp_daysFromTime secs", secs_h, hours, tag, std
   #print day, type(day), hday, type(hday)
   if day and hours >= day: 
      hours = 0.0
      days += 1
   if hday and hours >= hday: 
      hours = 0.0
      days += 0.5
   return days, hours
   
def Afp_importFileData(fname):
   if Afp_existsFile(fname):
       fin = open(fname , 'r') 
       data = fin.read()
       fin.close()
       delete = "\x04\x1B" # remove 'EOT' and 'ESC' from filedata
       data = data.translate(None, delete)
       return data
   else:
      return fname
   
def Afp_copyArray(array):
   new_array = []
   for entry in array:
      new_array.append(entry)
   return new_array
def Afp_copyFile(fromFile, toFile):
   shutil.copyfile(fromFile, toFile) 
  
# path and file handling 
def Afp_addPath(path, file):
   return os.path.join(path, file)
def Afp_genHomeDir():
   if 'HOME' in os.environ:
      path = os.environ['HOME']
   else:
      path =  os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
   return path
def Afp_genEmptyFile(filename):
   fout = open(filename, 'w')
   fout.write(" ")
   fout.close()
def Afp_existsFile(filename):
   return os.path.exists(filename)
def Afp_getFileTimestamp(filename):
   return datetime.datetime.fromtimestamp(os.path.getmtime(filename))
      
def Afp_startProgramFile(programname, debug, filename, parameter = None, noWait = False):
   befehl = ""
   if programname: befehl += programname + " " 
   befehl += filename  
   if parameter:
      befehl += " " + parameter
   if noWait: befehl += " &"
   if debug: print befehl
   os.system(befehl )
   #subprocess.call("soffice -pt HP_Color_LaserJet *", shell=True)
   #subprocess.call("soffice --invisible --convert-to pdf filename)
  
def Afp_configLogger(level, to_file):
   # level specify --log=DEBUG or --log=debug
   numeric_level = getattr(logging, level.upper(), None)
   if not isinstance(numeric_level, int):
       print  "WARNING: Invalid log level:", level
       return
   logging.basicConfig(level=numeric_level)
   if to_file:
      logging.basicConfig(filename=to_file)
def Afp_getLogger(name):
   return logging.getLogger(name)

# Main   
if __name__ == "__main__":
   #string = ("2*(13 + 2.7)")
   #pyBefehl = "value = " + string
   #exec pyBefehl
   #print string,"=", value
   zeitstring = "17:29"
   #time = AfpStringUtilities.Afp_fromString(zeitstring)
   val = Afp_TimeToFloat(time, True)
   print val
    
