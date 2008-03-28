#
# Drupy/PHP.py
# A PHP abstraction layer for Python
# 
# @package Drupy
# @file php.py
# @module drupy.php
# @author Brendon Crawford
# @see http://drupy.sourceforge.net
# @created 2008-02-05
# @version 0.1.1
# @modified 2008-08-20
#
#

import sys
import StringIO
import time
import datetime
import os
import urlparse
import random
import copy
import re
import pickle
import hashlib
import zlib
import htmlentitydefs
import cgi
import cgitb; cgitb.enable()
import urllib
import DrupyHelper

#
# Drupy helpers
#
global drupy_buffer; drupy_buffer = []

#
# PHP Constants
#
global ENT_QUOTES; ENT_QUOTES = 1
global E_ALL; E_ALL = 6143

#
# Get POST fields
# @return Dict[Str,List]
#
def __postFields():
  a = {}
  f = cgi.FieldStorage()
  for i in f:
    if isinstance(f[i], list):
      a[i] = []
      for j in f[i]:
        a[i].append(j.value)
    else:
      a[i] = f[i].value
  return a


#
# Gets error.
# This does not mimic the exact behaviour of the
# corresponding PHP function
#
# @return Tuple
# @returnprop Int 0
# @returnprop Str 1
# @returnprop Str 2
# @returnprop Int 3
# @returnprop Dict 4
# @returnprop Type 5
#
def error_get_last():
  err = sys.exc_info();
  return (
    E_ALL,            #errno
    err[1],           #errstr
    "NOT-AVAILABLE",  #errfile
    err[2].tb_lineno, #errline
    globals(),        #errcontext
    err[0]            #errtype
  )



#
# Sort on func
# @param Iterable item
# @param Function func
# @return Iterable
#
def uasort(item, func):
  return sort(item, func)


#
# Output buffering start
# @return Int
#
def ob_start():
  global drupy_buffer
  drupy_buffer.append( StringIO.StringIO() )
  outIndex = len(drupy_buffer) - 1
  sys.stdout = drupy_buffer[outIndex]
  return outIndex


#
# Get output buffering contents
# @return Str
#
def ob_get_clean():
  global drupy_buffer
  outLen = len(drupy_buffer)
  if outLen < 1:
    return None
  outIndex = outLen - 1
  data = drupy_buffer[outIndex].getValue()  
  if outIndex > 0:
    sys.stdout = drupy_buffer[outIndex - 1]
  else:
    sys.stdout = sys.__stdout__
  close(drupy_buffer[outIndex])
  del drupy_buffer[outIndex]
  return data
  


#
# Array filter
# @param Iterable item
# @param Function func
# @return Iterable
#
def array_filter(item, func):
  return filter(func, item)



#
# Sets globals variable
# @param Str name
# @param Number,Str val
# @return Bool
#
def define(name, val = None):
  vars = {'name':name}
  if \
      isinstance(val, int) or \
      isinstance(val, float) or \
      isinstance(val, bool) or \
      val == None:
    vars['val'] = val
  elif isinstance(val, str):
    vars['val'] = "'%(val)s'" % {'val':val}
  else:
    return false 
  out = \
    ("global %(name)s\n" + \
    "%(name)s = %(val)s") \
    % vars
  exec(out, globals())
  return True


#
# Splits string on delim
# @param Str delim
# @param Str val
# @return Str
#  
def explode(delim, val, limit = None):
  if limit != None:
    return val.split(delim, limit)
  else:
    return val.split(delim)


#
# Gets microtime
# @return Str
#
def microtime():
  (sec, usec) = str(time.time()).split('.')
  return " ".join(['.' + usec, sec])


#
# CHecks file is writeable
# @param Str filename
# @return Bool
# 
def is_writable(filename):
  return os.access(filename, os.W_OK)


#
# Checks file is directory
# @param Str filename
# @return Bool
#
def is_dir(filename):
  return os.path.isdir(filename)


#
# Merges lists
# @param Dict,List a1
# @param Dict,List a2
# @return Dict,List 
# 
def array_merge(a1, a2):
  out = copy.deepcopy(a1)
  for k in a2:
    out[k] = a2[k]
  return out


#
# Get keys
# @param Dict item
# @return List
#
def array_keys(item):
  return item.keys()


#
# Has key
# @param Str item
# @param Dict item
# @return Bool
#
def array_key_exists(name, item):
  return item.has_key(name);


#
# Check variable existance
# @param Dict,List,Object obj
# @param Str,Int val
# @param Bool searchGlobal  
#
def isset(obj, val, searchGlobal = False, data = {}):
  sVal = None
  # Dict
  if \
      isinstance(obj, dict) or \
      isinstance(obj, tuple):
    # Get globals also
    if searchGlobal:
      sVal = array_merge(obj, globals())
    else:
      sVal = obj
    if sVal.has_key(val):
      data['val'] = obj[val]
      data['msg'] = "Is Dict, Has Key, Globals: %s" % str(sVal)
      return True
    else:
      data['val'] = None
      data['msg'] = "Is Dict, Has Not Key, Globals: %s" % str(sVal)     
      return False
  # List
  elif isinstance(obj, list):
    if (val < len(obj)):
      data['val'] = obj[val]
      data['msg'] = "Is Index, Has Key, Globals: %s" % str(sVal)
      return True
    else:
      data['val'] = None
      data['msg'] = "Is Index, Has Not Key, Globals: %s" % str(sVal)
      return False
  # Object
  elif isinstance(obj, object):
    if hasattr(obj, val):
      data['val'] = getattr(obj, val)
      data['msg'] = "Is Object, Has Key, Globals: %s" % str(sVal)
      return True
    else:
      data['val'] = None
      data['msg'] = "Is Object, Has Not Key, Globals: %s" % str(sVal)
      return False
  # Others unknown
  else:
    data['Val'] = None
    data['msg'] = "Is Unknown, Has Not Key Globals: %s" % str(sVal)
    return False


#
# Get time
# @return Int
# 
def drupy_time():
  return time.time()


#
# In array
# @param Str,Int val
# @param List,Dict,Object obj
# @return Bool
#
def in_array(val, obj):
  return isset(obj, val)


#
# Fills array
# @param Int start
# @param Int cnt
# @param Str val
# @return Dict
#
def array_fill(start, cnt, val):
  r = {}
  i = start
  while i <= (start + cnt):
    r[i] = val
    i += 1
  return r


#
# Shifts array
# @param List,Dict,Tuple item
# @return Mixed
#
def array_shift(item):
  if isinstance(item, list):
    if len(item) > 0:
      return item.pop(0)
    else:
      return None
  elif isintance(item, dict):
    k = item.keys()
    if len(k) > 0:
      return item.pop(k[0])
    else:
      return None
  else:
    return None


#
# Function exists
# @param Dict,List,Object obj
# @param Str val
# @return Bool
#
def function_exists(val, loc = None):
  if _loc == None:
    exists = isset(globals(), val)
  else:
    exists = isset(loc, val, True)
  return (exists and isinstance(obj[val], function))


#
# html special chars
# @param Str val
# @return Str 
#
def htmlspecialchars(val, flags = None):
  out = ""
  for i in range(0, len(val)):
    num = ord(unicode(val[i]))
    if htmlentitydefs.codepoint2name.has_key(num):
      out += "&%s;" % htmlentitydefs.codepoint2name[num]
    else:
      out += val[i]
  return out



#
# Checks for empty
# @param Any obj
# @param Str val
# @param Bool searchGlobal
# @return Bool
# 
def empty(val):
  # Boolean
  if \
      isinstance(data['val'], bool) and \
      (data['val'] == False):
    return True
  # None
  elif \
      data['val'] == None:
    return True  
  # Lists
  elif \
      isinstance(data['val'], list) or \
      isinstance(data['val'], tuple) or \
      isinstance(data['val'], dict):
    return (len(data['val']) <= 0)
  # Numbers
  elif \
      isinstance(data['val'], int) or \
      isinstance(data['val'], float):
    return (data['val'] <= 0)
  # String
  elif \
      isinstance(data['val'], str):
    return (data['val'].strip() == '')
  # Anything else
  else:
    return False



#
# Translate characters
# Inspired by snippet from Xavier Defrang
# @see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
#
def strtr(text, items):
  regex = re.compile("(%s)" % "|".join(map(re.escape, items.keys())))
  out = regex.sub(lambda mo: items[mo.string[mo.start():mo.end()]], text)
  return out


#
# Check if uploaded file
# @param Str filename
# @return Bool
#
def is_uploaded_file(filename):
  return True



#
# Implodes
# @param Str delim
# @param List items
# @return Str
#
def implode(delim, items):
  return delim.join(items)


#
# Array slice
# @param List,Dict items
# @param Int a1
# @param Int a2
# @return Mixed
#
def array_slice(items, a1, a2 = None):
  if (a2 == None):
    return items[a1:]
  else:
    return items[a1:a2]


#
# R Trim
# @param Str val
# @return Str
#
def rtrim(val, chars = None):
  if chars != None:
    return val.rstrip(chars)
  else:
    return val.rstrip()


#
# L trim
# @param Str val
# @return Str
#
def ltrim(val, chars = None):
  if chars != None:
    return val.lstrip(chars)
  else:
    return val.lstrip()


#
# Check regular file
# @param String filename
# @return Bool
#
def is_file(filename):
  return os.path.isfile(filename)


#
# Check file exists
# @param Str filename
# @return Bool
#
def file_exists(filename):
  return os.path.exists(filename)


#
# Includes file
# @param Str filename
# @param Dict scope
# @return Bool
# 
def include(filename, scope = None):
  if (scope != None):
    execfile(filename, scope)
  else:
    execfile(filename)
  return True


#
# Url decoder
# @param Str val
# @return Str
#
def urldecode(val):
  return urllib.unquote_plus(val)



#
# Parse url
# @param url
# @return Dict
#
def parse_url(url):
  u = urlparse.urlparse(url)
  return {
    'scheme' : u[0],
    'host' : u[1],
    'path' : u[2],
    'query' : u[4],
    'fragment' : u[5]
  }

#
# Cast to object
# @param Dict dic
# @return Object
#
def drupy_object(dic):
  out = stdClass()
  for i in dic:
    setattr(out, i, dic[i])
  return out



#
# Get strlen
# @param Str val
# @return Int
# 
def strlen(val):
  return len(val)


#
# Reverses list
# @param List items
# @return List
#
def array_reverse(items):
  rItems = copy.deepcopy(items)
  rItems.reverse()
  return rItems


#
# prepares pattern for python regex
# @param Str pat
# @return _sre.SRE_Pattern
#    Regular Expression object
#
def __preg_setup(pat):
  delim = pat[0]
  flg = 0
  pat = pat.lstrip(delim)
  i = len(pat) - 1
  while True:
    if i < 1:
      break
    else:
      if pat[i] == delim:
        pat = pat[0:len(pat)-1]
        break
      else:
        flg = flg | (eval('re.' + pat[i].upper(), globals()))
        pat = pat[0:len(pat)-1]
        i = i - 1
  return re.compile(pat, flg)


#
# Escapes regular expression
# @param Str val
# @param Any delim
#    Not used
# @return Str
#
def preg_quote(val, delim = None):
  return re.escape(val)


#
# Convert PHP preg_match to Python matcher
# @param Str pat
# @param Str subject
# @param Dict match
# @return Dict
# @returnprop List match
#
def preg_match(pat, subject, match = None):
  if match != None:
    DrupyHelper.Reference.check(match)
  reg = __preg_setup(pat)
  g = list(reg.search(subject).groups())
  g.insert(0, ''.join(g))
  if match != None:
    match.val = g
  return len(g)



#
# Preg Match all
# @param Str pat
# @param Str subject
# @param Reference &matches
# @return Int
#
def preg_match_all(pat, subject, matches = None):
  if matches != None:
    DrupyHelper.Reference.check(matches)
  reg = __preg_setup(pat)
  g = list( reg.finditer(subject) )
  if len(g) > 0:
    out = range(len(g[0].groups()))
    for i in range(len(out)):
      out[i] = []
      for j in g:
        out[i].append(j.group(i))
    matches.val = out
    return len(g)
  else:
    out = [[]]
    matches.val = out
    return 0
    



#
# Returns unique id
# @param Str prefix
# @param Bool more_entropy
# @return Str
#
def uniqid(prefix = None, more_entropy = False):
  out = ''
  num = (23 if more_entropy else 13)
  if prefix != None:
    random.seed(prefix)
  for i in range(0, num):
    out += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
  return out



#
# Random
# @param Int min
# @param Int max
# @return Int
#
def mt_rand(min = 0, max = sys.maxint):
  return random.randint(min, max)


#
# str replace wrapper
# @param Str pat
# @param Str rep
# @param Str subject
# @return Str
#
def str_replace(pat, rep, subject):
  out = subject
  if isinstance(pat, list):
    repIsStr = isinstance(rep, list)
    for i in pat:
      if repIsStr:
        repStr = rep
      else:
        repStr = rep[i]
      out = __str_replace_str(pat[i], repStr, out)
  else:
    out = __str_replace_str(pat, rep, subject)
  return out
  

#
# str replace real
# @param Str pat
# @param Str rep
# @param Str subject
# @return Str
#
def __str_replace_str(pat, rep, subject):
  return sub.replace(pat, rep)



#
# preg_replace wrapper
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def preg_replace(pat, replace, subject):
  out = subject
  if isinstance(pat, list):
    repIsStr = isinstance(rep, list)
    for i in pat:
      if repIsStr:
        repStr = rep
      else:
        repStr = rep[i]
      out = __preg_replace_str(pat[i], repStr, out)
  else:
    out = __preg_replace_str(pat, rep, subject)
  return out
    

#
# Real preg replace
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def __preg_replace_str(pat, rep, subject):
  reg = preg_setup(pat)
  return reg.sub(rep, subject)


#
# dir name
# @param Str path
# @return Str
#
def dirname(path):
  return os.path.dirname(path)


#
# trim whitespace
# @param Str val
# @return Str
#
def trim(val, chars = None):
  if chars != None:
    return val.strip(chars)
  else:
    return val.strip()


#
# Gets array count
# @param List,Dict item
# @return Int
#
def count(item):
  return len(item)


#
# Determines whether or not is numeric
# @param Any val
# @return Bool
#
def is_numeric(val):
  if \
      isinstance(val, int) or \
      isinstance(val, float):
    return True
  elif \
      isinstance(val, str) and \
      val.isdigit():
    return True
  else:
    return False



#
# Is null
# @param Any val
#
def is_null(val):
  return (val == None)


#
# Gets str pos
# @param Str haystack
# @param Str needle
# @return Int,Bool
#
def strpos(haystack, needle):
  pos = haystack.find(needle)
  if pos < 0:
    return False
  else:
    return pos


#
# Pretends to set an ini
# Actually just sets a global
# @param Str name
# @param Str,Number,None,Bool val
# @return Bool
#
def ini_set(name, val):
  define(name.replace('.', '_'), val)
  return True


#
# Sets session name
# @param Str name
# @return Bool
#
def session_name(name):
  return 'session'


#
# serializer
# @param Any obj
# @return Str
#
def serialize(obj):
  return pickle.dumps(obj)


#
# unserializer
# @param Str val
# @return Obj
#
def unserialize(val):
  return pickle.loads(val)


#
# Checks for defined var
#
def defined(val):
  return isset(globals(), val)


#
# GMT date
# @param Str format
# @param Int stamp
# @return Str
#
def gmdate(format, stamp = None):
  if stamp == None:
    stamp = time.time()
  dt = datetime.datetime.utcfromtimestamp(stamp)
  return dt.strftime(format)


#
# Strip slashes
# @param Str val
# @retun Str
#
def stripslashes(val):
  return val.replace('\\', '')


#
# Add slashes
# @param Str val
# @return Str
#
def addslashes(val):
  return re.escape(val)
  

#
# md5
# @param Str val
# @return Str
#
def do_md5(val):
  return hashlib.md5(val).hexdigest()


#
# decompress
# @param Str val
# @return Str
#
def gzinflate(val):
  return zlib.decompress(val)


#
# compress
# @param Str val
# @return Str
#
def gzdeflate():
  return zlib.compress(val)

#
# Pops item
# @param item
# @return Mixed
#
def array_pop(item):
  return item.pop()


#
# Std class
#
class stdClass:
  def __init__(self): pass
        
    
    
#
# Set Aliases
#
array_key_exists = in_array
gzencode = gzdeflate
gzdecode = gzinflate
sizeof = count
static = define
set_global = define
require_once = include
require = include
include_once = include
substr = array_slice
defined = isset
preg_replace_callback = preg_replace
is_writeable = is_writable


#
# Superglobals
#
global _SERVER; _SERVER = dict(os.environ)
global _GET; _GET = cgi.parse()
global _POST; _POST = __postFields()
global _REQUEST; _REQUEST = array_merge(_GET, _POST)


