import time
import os
from urlparse import urlparse


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
# Set Aliases
#
static = define
set_global = define
require_once = include
require = include
include_once = include







