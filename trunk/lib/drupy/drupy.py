import time
import os
import urlparse
import copy
import re


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
def isset(obj, val, searchGlobal = False):
  # Dict
  if isinstance(obj, dict):
    # Get globals also
    if searchGlobal:
      sVal = array_merge(obj, globals())
    else:
      sVal = val
    return obj.has_key(sVal)
  # List
  elif isinstance(obj, list):
    return (val < len(obj))
  # Object
  elif isinstance(obj, object):
    return hasattr(obj, val)


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
    return items[a1]
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
# @return List
# @returnprop Str 0
# @returnprop Int 1
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
  return [pat, flg]


#
# Convert PHP preg_match to Python matcher
# @param Str pat
# @param Str subject
# @param Dict match
# @return Dict
# @returnprop List match
#
def preg_match(pat, subject, match = {}):
  (pat, flg) = preg_setup(pat)
  g = list(re.match(pat, subject, flg).groups())
  g.insert(0, ''.join(g))
  match['match'] = g
  return len(g)


#def preg_replace(pat, replace, subject):
#  (pat, flg) = preg_setup(pat)
  



#
# Set Aliases
#
static = define
set_global = define
require_once = include
require = include
include_once = include
substr = array_slice







