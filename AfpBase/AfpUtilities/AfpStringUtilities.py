#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package AfpBase.AfpUtilities.AfpStringUtilities
# AfpStringUtilities module provides general solely python dependend utilitiy routines
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


import datetime

import AfpBaseUtilities
from AfpBaseUtilities import *

## list of german "Umlaute" to be replaced \n
# - 228 a-uml 
# - 252 u-uml
# - 246 o-uml
# - 223 sz
# - 225 a-ghraph
# - 233 e-egu
umlaute = ((228, 'ae'),(252, 'ue'),(246, 'oe'),(223, 'ss'),(225, 'a'),(233, 'e'))

# conversions between values and strings
## convert data to string
# @param data - data to be converted
def Afp_toString(data):
    string = ""
    typ  = type(data)   
    if typ == str:
        string = data.decode('iso8859_15')
        #string = data
    elif typ == unicode:
        string = data
    elif typ == int or typ == long:
        string = str(data)
    elif typ == float:
        string = ("%8.2f")%(data)
    elif typ == datetime.date:
        string = data.strftime("%d.%m.%y")
    elif typ == datetime.timedelta or typ == datetime.time:
        if (typ == datetime.time and data == datetime.time.max) or (typ == datetime.timedelta and data.days > 0):
            string = "24:00"
        else:
            split = str(data).split(":")
            #print "Afp_toString",data,split
            if  len(split) > 2 and float(split[2]) > 59:
                split[1] = str(int(split[1]) + 1)
                if split[1] == "60":
                    split[1] = "00"
                    split[0] = str(int(split[0]) + 1)
            string = split[0] + ":" + split[1]
    elif typ == list:
        string = "".join(str(data))
    elif not data is None:
        print "WARNING: \"" + typ.__name__ + "\" conversion type not specified!", data
    return string 
## convert data to string, string to quoted strings, 
# dates and times to strings describing the  timedelta or date creation
# @param data - data to be converted
def Afp_toQuotedString(data):
    string = Afp_toString(data)
    typ = type(data)
    if Afp_isString(data): string = "\"" + string + "\""
    elif  typ == datetime.timedelta or typ == datetime.time:
        if string == "24:00": string = "datetime.timedelta(days=1)"
        else: 
            split = string.split(":")
            string = "datetime.timedelta(hours=" + split[0] + ", minutes=" + split[1] + ")"
    elif typ == datetime.date:
        split = string.split(".")
        if len(split[2]) < 3: split[2] = "20" + split[2]
        string = "datetime.date(" + split[2] + ", " + split[1] + ", " + split[0] + ")"
    return string
## convert data to string, 
# dates and times are converted to internal representation (yyyy-mm-dd)
# @param data - data to be converted
def Afp_toInternDateString(data):
    string = Afp_toString(data)
    if type(data) == datetime.date:
        string = data.strftime("%y-%m-%d")
    elif type(data) == datetime.time:
        string = data.strftime("%H:%M:%S.%f")
    return string
## convert data to string, 
# dates are converted to short format without year (dd.mm)
# @param data - data to be converted
def Afp_toShortDateString(data):
    string = Afp_toString(data)
    if type(data) == datetime.date:
        split = string.split(".")
        string = split[0] + "." + split[1]
    return string
## direct conversion of float data to string
# @param data - data to be converted
# @param format - format of data in string
def Afp_toFloatString(data, format = "8.2f"):
    if data is None: return ""
    string = ("%" + format)%(data)
    return string.strip()
## analyse string and extract data from it
# @param string - string to be converted
# - "xx.xx" or "xx,xx" -> float (x - digit)
# - "dd.mm.yy[yy]"  -> date, short year will be mapped in actuel century
# - "hh:mm[:ss]" -> time
# - "xxx" -> int (x - digit)
# - other -> string
def Afp_fromString(string):
    if not Afp_isString(string): return string
    string = string.strip()
    data = None
    if not " " in string:
        if "." in string:
            split = string.split(".")
        elif "," in string:
            split = string.split(",")
        else:
            split = [string]
        if len(split) > 2 and len(string) < 11:
            day = 0
            if split[0].isdigit(): day = int(split[0])
            month = 0
            if split[1].isdigit(): month = int(split[1])
            year = 0
            if split[2].isdigit(): year = int(split[2])
            if day > 0 and month > 0 and year > 0:
                if year < 1000: year += 100* int(datetime.date.today().year/100) 
                data = datetime.date(year, month, day)
        elif len(split) > 1:
            left = 0
            if split[0].isdigit(): left = int(split[0])
            right = 0
            if split[1].isdigit(): right = int(split[1])
            if (not left == 0 or Afp_isZeroString(split[0])) and (right > 0 or Afp_isZeroString(split[1])):
                data = float(split[0] + "." + split[1])
        elif ":" in string and len(string) < 9:
            split = string.split(":")
            hours = 0
            if split[0].isdigit(): hours = int(split[0])
            if hours > 23:
                #data = datetime.time.max
                data = datetime.timedelta(days=1)
            else:
                minutes = 0
                if len(split) > 1:
                    if split[1].isdigit(): minutes = int(split[1])
                seconds = 0
                if len(split) > 2:
                    if split[2].isdigit(): seconds = int(split[2])
                #data = datetime.time(hours, minutes, seconds)
                data = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        elif string:
            val = 0
            #print "Afp_fromString:", string
            if string.isdigit() or (string[0] == "-" and string[1:].isdigit()) : val = int(string)
            if not val == 0 or string == "0":
                data = val
    if data:
        return data
    else:
        return string
## convert string to an integer
# @param string - string to be converted
# @param init - value, if no integer can be assigned
def Afp_intString(string, init = 0):
    result = init
    data = Afp_fromString(string)
    if Afp_isNumeric(data):
        result = int(data)
    return result
## convert string to a float
# @param string - string to be converted
def Afp_floatString(string):
    result = 0.0
    data = Afp_fromString(string)
    if Afp_isNumeric(data):
        result = float(data)
    return result
## convert string to a date, if no conversion is found, today is returned
# @param string - string to be converted
def Afp_dateString(string):
    result = Afp_fromString(string)
    if type(result) != datetime.date:
        result = datetime.now().date()
    return result
## convert string to a time value
# @param string - string to be converted
# @param end - indicates that maxtime should be set instead or mintime 
# in case no timevalue can be extracted
def Afp_timeString(string, end = False):
    result = Afp_fromString(string)
    typ = type(result)
    if typ == datetime.timedelta:      
        result = Afp_toTime(result)
    elif typ != datetime.time:
        if Afp_isNumeric(string):
            value = Afp_toFloat(string)
            if value:
                hours = int(value)
                mins = int(60*(value - hours))
                result = datetime.time(hours, minutes)
            else:
                if end:
                    result = datetime.time.max
                else:
                    result = datetime.time.min
    return result
## generate datetime data from date- and timestring
# @param datestring - string holding date
# @param timestring - string holding time
# @param end - for time creation: indicates that maxtime should be set instead or mintime 
def Afp_datetimeString(datestring, timestring, end = False):
    date = Afp_dateString(datestring)
    time = Afp_timeString(timestring, end)
    return datetime.datetime.combine(date, time)
## convert a number given by a string to a proper float string
# @param string - string to be converted
def Afp_stringFloatString(string):
    return Afp_toString(Afp_floatString(string))
 
##  convert all entries of a array to strings, routine will be called recursively for inner lists
def Afp_ArraytoString_dep(array):
    for i in range(len(array)):
        if type(array[i]) == list:
            array[i] = Afp_ArraytoString(array[i])
        else:
            array[i] = Afp_toString(array[i])
    return array
## convert all entries of a up to 2-dim array to strings  
# @param array - value array to be converted
def Afp_ArraytoString(array):
    #print "Afp_ArraytoString"
    new_array = []
    if array:
        for row in array:
            if type(row) == list or type(row) == tuple:
                new_array.append(Afp_ArraytoString(row))
            else:
                new_array.append(Afp_toString(row))
    return new_array
##merges an array int one string, separated by blanks
# @param liste - list of values to be merged
# @param max - maximum number of elements used for merging
def Afp_genLineOfArr(liste, max = None):
    if max is None: max = len(liste)
    count = 0
    zeile = ""
    for entry in liste:
        if count < max:
            zeile += Afp_toString(entry) + " "
            count += 1
    return zeile[:-1]

# type of strings and values
## flag is value is a stringtype
# @param wert - value to be analysed
def Afp_isString(wert):
    typ = type(wert)
    if typ == str or typ == unicode: return True
    return False
## flag is value is a string not enclosed by quotes
# @param wert - value to be analysed
def Afp_isPlainString(wert):
    if Afp_isString(wert):
        wert = wert.strip()
        if (wert[0] == "\""and wert[-1] == "\"") or (wert[0] == "'"and wert[-1] == "'"):
            return False
        else:
            return True
    return False
## flag is sign indicates a	comparison
# @param sign - string to be analysed
def Afp_isCompare(sign):
    if "=" in sign or ">" in sign or "<" in sign or "LIKE" in sign:
        return True
    else:
        return False
## flag if string represents an empty line
# @param string - string to be analysed
def Afp_isNewline(string):
    return string.strip() == ""
## flag if string represents an zero value
# @param string - string to be analysed
def Afp_isZeroString(string):
    for char in string.strip():
        if not char == "0": return False
    return True
## flag if string may represent IP4 address
# @param string - string to be analysed
def Afp_isIP4(string):
    return Afp_hasNumericValue(string, 4)
## flag if string may represent a numeric value
# @param string - string to be analysed
# @param check - maximum number of parts accepted when split at a "." \n
# - check == 2: default, less then 2 parts are accepted \n
# - check > 2: exact number of parts has to be available
def Afp_hasNumericValue(string, check=2):
    if "." in string:
        split = string.split(".")
        if check > 2 and not len(split) == check:
            numeric = False
        else:
            numeric = True
        for i in range(0,len(split)):
            if i < check and not split[i].isdigit():
                numeric = False
        return numeric
    elif string.isdigit():
        if check < 3: return True
        else: return False
    else:
        return False
## mask double qoutes in string values
# @param value - value to be analysed
def Afp_maskiere(value):
    if value is None: return None
    if Afp_isString(value):
        return value.replace('"','\\"')
    return  value
## combine values to one string, if only one value is indicated each value type is possible
# @param indices - indices of values to be extracted from array and combined
# @param array- list of values
def Afp_combineValues(indices, array):
    wert = ""
    if indices is None:
        for value in array:
            if wert == "": leer = ""
            else: leer = " "
            wert += leer +  Afp_maskiere(Afp_toString(value))
    else:
        if len(indices) == 1:
            # single index, each type possible
            wert = array[indices[0]]
            if type(wert) == str:
                wert = Afp_maskiere(wert)
        else:
            # multiple index, only string possible
            for ind in indices:
                if wert == "": leer = ""
                else: leer = " "
                wert += leer +  Afp_maskiere(Afp_toString(array[ind]))
    return wert
   
## DEPRECATED FUNCTION: use Afp_extractPureValues or Afp_extractStringValues instead
def Afp_extractValues(indices, array):
    #print "deprecated function Afp_extractValues:",indices, array
    if indices is None:
        wert = []
        for entry in array:
            wert.append(Afp_maskiere(Afp_toString(entry)))
    else:
        if len(indices) == 1:
            # single index, each type possible
            wert = array[indices[0]]
            if type(wert) == str:
                wert = Afp_maskiere(wert)
            #print "Afp_extractValues", wert, type(wert), array
        else:
            # multiple index, only string possible
            wert = []
            for ind in indices:
                wert.append(Afp_maskiere(Afp_toString(array[ind])))
    return wert
## extract values from array (list) and convert them to strings
# @param indices - indices of values to be extracted from array, None all entries are extracted
# @param array- list of values
def Afp_extractStringValues(indices, array):
    #print "Afp_extractStringValues:",indices, array
    werte = Afp_extractPureValues(indices,array)
    strings = []
    for entry in werte:
        strings.append(Afp_maskiere(Afp_toString(entry)))
    return strings

## compare two values extracted from database
# @param v1 - first value
# @param v2 - second value
# @param debug - flag for debug output
def Afp_compareSql(v1, v2, debug = False):
    if Afp_isNumeric(v1):
        return (v1 == v2)
    elif v1.lower() == v2.lower():
        return True
    v1 = Afp_replaceUml(v1.lower())
    v2 = Afp_replaceUml(v2.lower())
    if debug: print v1,v2
    return (v1 == v2)
## replace special german letters to compare words
# @param string - string to be manipulated
def Afp_replaceUml(string):
    newstring = ''
    modified = False
    for char in string:
        uni = ord(char)
        #print char, uni
        if uni > 222:
            modified = True
            for un, uml in umlaute:
                if uni == un: 
                    char = uml
                    break
        newstring += char
    if modified:
        return newstring
    else:
        return string
## extract word from string which include special phrases
# @param in_string - string to be analysed
# @param including - string to included in word
def Afp_getWords(in_string, including=None):
    words = []
    str = ""
    if including:
        split = in_string.split(including)
    else:
        split = [in_string]
    lastwords = None
    for teilstr in split:
        str = ""
        currentwords = []
        for s in teilstr:
            if s in string.ascii_letters:
                str += s
            else:
                if str:  currentwords.append(str)
                str = ""
        if str: currentwords.append(str)
        if not lastwords is None:
            word = ""
            if lastwords: word += lastwords[-1]
            word += including
            if currentwords: word += currentwords[0]
            words.append(word)
        lastwords = currentwords
    if including is None:
        words = currentwords
    return words
## removes end of string behind last occurence of char
# @param string - string to be cut
# @param char - char where string should be cut
def Afp_getToLastChar(string, char):
    if char in string:
        split = string.split(char)
        result = ""
        for i in range(len(split)-1):
            result += split[i] + char
        return result
    else:
        return string
## get letters in front of numeric figures
# @param  string - string where letters have to be extracted
def Afp_getStartLetters(string):
    letters = ""
    test = True
    for s in string:
        if test:
            if s.isdigit(): test = False
            else: letters += s
    return letters
 
## devide string into phrases inside and outside the start/end brackets
# @param  string - string to be analysed
# @param  start - opening bracket
# @param  end  - closing bracket \n
# output: \n
# - len(instrings)     == len(outstrings): in[i] + out[i] + ...
# - len(instrings)+1 == len(outstrings): out[i] + in[i] + out[i+1] + ...
def Afp_between(string, start, end):
    sstring = string.split(start)
    instrings = []
    outstrings = []
    for strg in sstring:
        split= strg.split(end)  
        if len(split) > 1: 
            instrings.append(split[0])
            outstrings.append(split[1])
            if len(split)>2:
                print "Assymetric ", start , end,  " pair in \"" + string +"\""
        else:
            outstrings.append(split[0])
    return instrings,outstrings

## devide string into phrases inside and outside a double quote pair
# @param  string - string to be analysed
def Afp_maskedText(string):
    masked = []
    unmasked = []
    split = string.split("\"")
    mask = False
    for part in split:
        if mask: masked.append(part)
        else: unmasked.append(part)
        mask = not mask
    return unmasked, masked
   
## extract variable and function body from string \n
# split at "=". "+=","-=","*=" are handled also
# @param  string - string to be analysed
def Afp_getFuncVar(string):
    # get variable name and function
    if not "=" in string: return None, string
    split = string.split("=")
    if len(split) > 2: return None, string
    var = split[0].strip()
    func = split[1].strip()
    sign = ""
    if not var.isalpha():
        sign = var[-1]
        var = var[:-1].strip()
        func = var + sign + func
    return var, func
## split function fromula at signs, devide variables and signs
# @param  string - string to be analysed
def Afp_splitFormula(string):
    vars = []
    signs = []
    wort = ""
    for c in string:
        if c == "*" or c == "/" or c == "+" or c == "-" or c == ")": 
            if len(signs) > 0 and signs[-1] == ")":
                signs[-1] = signs[-1] + c
            else:
                signs.append(c)
                vars.append(wort.strip())
            wort = ""
        elif c =="(": 
            signs[-1] = signs[-1] + c
        else: 
            wort += c
    if wort: vars.append(wort.strip())
    return vars, signs  
 
 ## split string at different limiters
# @param in_string - string to be analysed
# @param limiters - list of limiters where string has to be split
def Afp_split(in_string, limiters):
    strings = [in_string]
    split = []
    for limit in limiters:
        split = []
        for string in strings:
            split.append(string.split(limit))
        strings = []
        for s1 in split:
            for s in s1:
                strings.append(s)
    return strings

## assure pathname to recognise wanted conventions for the path separator, \n
#  used for either Unix "/" or Windows "\\" separator.
# @param path - pathname to be checked
# @param delimit - path separartor, defaul Unix
# @param file - flag if path is a filename (otherwise an addtional delimiter is added at end)
def Afp_pathname(path, delimit = None, file = False):
    delimiter = "/"
    if delimit: delimiter = delimit
    if delimiter == "\\":
        path = path.replace("/",delimiter)
    else:
        path = path.replace("\\",delimiter)
    if not file and not path[-1] == delimiter: path += delimiter
    return path
## check if given name holds a complete path (includig a root), \n
# if not, given rootdir is added at the beginning of the name.
# @param rootdir - rootpath to be added
# @param filename - name to be checked
def Afp_addRootpath(rootdir, filename):
    if filename[0] == "/" or ":" in filename:
        # root already in filename, don't do anything
        composite = filename
    else:
        if rootdir:
            if not (rootdir[-1] == "/" or rootdir[-1] == "\\"):
                if "\\" in rootdir:
                    rootdir += "\\"
                else:
                    rootdir += "/"
        composite = rootdir + filename
    return composite

## countes the starting spaces in the string
# @param string - string to be analysed
def Afp_leftSpCnt(string):
    # left space count
    return  len(string) - len(string.lstrip())

## check if string holds a date, \n
# possibly complete date with current day, month or year.
# @param string - string to be analysed
# @param only_past - flag if date is assumed to lie in the past,  \n
# short years will be completed with the last century, if the normal completation would set them to lie in the future.
def Afp_ChDatum(string, only_past = False):
    if string is None: return string
    today = datetime.date.today()
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)[2:]
    nodigits = []   
    chars = ""
    for char in string:
        if char.isdigit():
            if chars and not chars in nodigits: 
                nodigits.append(chars)
            chars = ""
        else:
            chars += char
    if chars and not chars in nodigits: 
        nodigits.append(chars)
    zahlen = Afp_split(string, nodigits)
    # complete date-string
    lgh = len(zahlen)
    for i in range(lgh-1,-1,-1):
        if not zahlen[i]: del zahlen[i]
    lgh = len(zahlen)
    if lgh < 3:
        if lgh == 0: zahlen.append(day)
        if lgh <= 1: zahlen.append(month)
        if lgh <= 2: zahlen.append(year)
    # check if year is in future
    if only_past and int(zahlen[2]) > int(year):
        zahlen[2] = str(today.year - 100)[:2] + zahlen[2]
    # check date values
    monat = int(zahlen[1])
    if monat < 1: zahlen[1] = '1'   
    if monat > 12: zahlen[1] = '12'   
    tag = int(zahlen[0])
    if tag < 1: zahlen[0] = '1'   
    if tag > 28: 
        if monat == 2:
            jahr = int(zahlen[2])
            if jahr%4 == 0: zahlen[0] = '29'
            else: zahlen[0] = '28'
        elif tag > 30:
            if monat%2:
                if monat > 7:  zahlen[0] = '30'
                else:  zahlen[0] = '31'
            else:
                if monat > 7:  zahlen[0] = '31'
                else:  zahlen[0] = '30'
    if len(zahlen[1]) == 1:
        zahlen[1] = '0' + zahlen[1]
    string = zahlen[0] + "." + zahlen[1] + "." + zahlen[2]
    return string
## check if string holds a time value, \n
# return the cleaned time string and the number of days extracted from this string
# @param string - string to be analysed
def Afp_ChZeit(string):
    if not string: return None, 0
    char = ":"
    if "." in string and not ":" in string: char = "."
    split = string.split(char)
    hours = int(split[0])
    minutes = None
    seconds = None
    if len(split) > 1:
        if split[1]:
            minutes = int(split[1])
        else:
            minutes = 0
        if len(split) > 2:
            if spli[2]:
                seconds = int(split[2])
            else:
                seconds = 0
    else:
        minutes = 0
    added = 0
    if seconds:
        added = seconds/60
        seconds = seconds%60
    if minutes:
        minutes += added
        added = minutes/60
        minutes = minutes%60
    hours += added
    days = hours/24
    hours = hours%24
    zeitstr = str(hours)
    #if minutes:
    zeitstr += ":"
    if minutes < 10: zeitstr += "0"
    zeitstr += str(minutes)
    if seconds:
        zeitstr += ":"
        if seconds < 10: zeitstr += "0"
        zeitstr += str(seconds)
    if days == 1 and zeitstr == "0:00":
        days = 0
        zeitstr = "24:00"
    #print "Afp_ChZeit:", zeitstr, days
    return zeitstr, days

## convert "Superbase" Field.Filename to mysql tablenames used in select statements.
# @param string - string where names should be converted
# @param dateien - names of tables involved in this statement
def Afp_SbToDbName(string,dateien):
    unmasked, masked = Afp_maskedText(string)
    out_unmasked = []
    for part in unmasked:
        out_part = ""
        words = part.split()
        space = ""
        i = -1
        for word in words:
            i = -1
            if "." in word:
                wsplit = word.split(".")
                if wsplit[1] in dateien: i = dateien.index(wsplit[1])
                else: i = dateien.index(wsplit[1].upper())
                if i > -1: 
                    out_part += space + "D" + str(i) + ".`" + wsplit[0] + "`"
            if i < 0: out_part += space + word
            space = " "
        out_unmasked.append(out_part)
    lgh = len(out_unmasked)
    lghm = len(masked)
    out_string = ""
    for i in range(0,lgh):
        out_string += out_unmasked[i]
        if i < lghm: out_string += " \"" + masked[i] + "\""
    return out_string
 ## complete the select statement with the .table extension for all tablecolumns
# @param select - select statement to be completetd 
# @param dbname - name of table for extensions
def AfpSelectEnrich_dbname(select, dbname):
    if select is None: return None
    enriched = ""   
    if select:
        ssplit = select.split()
        lastentry = ""
        for entry in ssplit:
            if lastentry and  Afp_isCompare(entry):
                lastentry += "." + dbname
            if lastentry:
                if enriched: space = " "
                else: space = ""
                enriched += space + lastentry
            lastentry = entry
        enriched += " " + lastentry
    return enriched
         
   
    
