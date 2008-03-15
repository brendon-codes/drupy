import time
import datetime
import os
import urlparse
import copy
import re
import pickle
import hashlib
import zlib


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
      isinstance(val, NoneType):
    vars['val'] = val
  elif isinstance(val, str):
    vars['val'] = "'%(val)s'" % {'val':val}
  else:
    return false 
  out = \
    "global %(name)s\n" + \
    "%(name)s = %(val)s" \
    % vars
  exec(out, globals())
  return True


#
# Splits string on delim
# @param Str delim
# @param Str val
# @return Str
#  
def explode(delim, val):
  return val.split(delim)


#
# Gets microtime
# @return Str
#
def microtime():
  (sec, usec) = str(time.time()).split('.')
  return " ".join(['.' + usec, sec])


#
# Merges lists
# @param Dict,List a1
# @param Dict,List a2
# @return Dict,List 
# 
def array_merge(a1, a2):
  out = a1
  for k,v in a2:
    out[k] = v
  return out
  

#
# Check variable existance
# @param Dict,List,Object obj
# @param Str,Int val
# @param Bool searchGlobal  
#
def isset(obj, val, searchGlobal = False, data = {}):
  # Dict
  if isinstance(obj, dict):
    # Get globals also
    if searchGlobal:
      sVal = array_merge(obj, globals())
    else:
      sVal = val
    if obj.has_key(sVal):
      data['val'] = obj[sVal]
      return True
    else:
      data['val'] = None
      return False
  # List
  elif isinstance(obj, list):
    if (val < len(obj)):
      data['val'] = obj[val]
      return True
    else:
      data['val'] = None
      return False
  # Object
  elif isinstance(obj, object):
    if hasattr(obj, val):
      data['val'] = getattr(obj, val)
      return True
    else:
      data['val'] = None
      return False
  # Others unknown
  else:
    return False


#
# Function exists

def function_exists(obj, val):
  return \
    (isset(obj, val, True) and isinstance(obj[val], function))


def htmlspecialchars(val):
  out = ""
  i = 0
  _i = len(val)
  while True:
    pass;


#
# Checks for empty
# @param Any obj
# @param Str val
# @param Bool searchGlobal
# @return Bool
# 
def empty(obj, val, searchGlobal = False):
  set = isset(obj, val, searchGlobal, data)
  # Not set
  if not set:
    return True
  # Boolean
  elif \
      isinstance(data['val'], bool) and \
      (data['val'] == False):
    return True
  # None
  elif \
      isinstance(data['val'], NoneType):
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
def rtrim(val):
  return val.rstrip()


#
# L trim
# @param Str val
# @return Str
#
def ltrim(val):
  return val.lstrip()

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
def preg_setup(pat):
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
# Convert PHP preg_match to Python matcher
# @param Str pat
# @param Str subject
# @param Dict match
# @return Dict
# @returnprop List match
#
def preg_match(pat, subject, match = {}):
  reg = preg_setup(pat)
  g = list(reg.search(subject).groups())
  g.insert(0, ''.join(g))
  match['match'] = g
  return len(g)


#
# preg_replace
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def preg_replace(pat, replace, subject):
  reg = preg_setup(pat)
  return reg.sub(replace, subject)


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
def trim(val):
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
  return True


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
# Set Aliases
#
gzencode = gzdeflate
gzdecode = gzinflate
sizeof = count
static = define
set_global = define
require_once = include
require = include
include_once = include
substr = array_slice







