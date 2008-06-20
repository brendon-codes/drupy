#!/usr/bin/env python


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file DrupyHelper.py
#  A PHP abstraction layer for Python
#  This file currently is built to working only with CGI.
#  Eventually it will be constructed to work with WSGI
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-02-05
# @version 0.1
# @depends Image (http://www.pythonware.com/products/pil/)
# @depends Hashlib (http://code.krypto.org/python/hashlib/)
# @depends Zlib (http://linux.maruhn.com/sec/python-zlib.html)
# @license: 
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

#
# Imports
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
import base64
import pickle
import hashlib
import zlib
import pprint
import htmlentitydefs
import cgi
import cgitb;
import urllib
from PIL import Image
from beaker import session
from lib.drupy import DrupyHelper

#
# Superglobals
#
SERVER = None
GET = None
POST = None
REQUEST = None
SESSION = None

#
# PHP Constants
#
ENT_QUOTES = 1
E_USER_WARNING = 512
E_ALL = 6143
CRLF = "\r\n"

#
# Function aliases
#
#
# Set Aliases
#
gzencode = None
gzdecode = None
sizeof = None
require_once = None
require = None
include_once = None
substr = None
preg_replace_callback = None
is_writeable = None
header = None
flush = None

#
# Initiate superglobals and set output buffering
#
def __init():
  global SERVER, GET, POST, REQUEST, SESSION, OUTPUT
  global __DRUPY_OUTPUT
  global header, flush
  global gzencode, gzdecode, sizeof, require_once, require, include_once, \
    substr, preg_replace_callback, is_writeable
  # Set SuperGlobals
  SERVER = __SuperGlobals.getSERVER()
  GET = __SuperGlobals.getGET()
  POST = __SuperGlobals.getPOST()
  REQUEST = __SuperGlobals.getREQUEST(GET, POST)
  SESSION = __SuperGlobals.getSESSION()
  # Set output buffer
  output = __Output(SERVER['WEB'])
  header = output.header
  flush = output.flush
  # Set aliases
  gzencode = gzdeflate
  gzdecode = gzinflate
  sizeof = count
  require_once = include
  require = include
  include_once = include
  substr = array_slice
  preg_replace_callback = preg_replace
  is_writeable = is_writable
  return


#
# Std class
#
class stdClass:

  def __init__(self): pass

#
# Reference class
#
class Reference:

  #
  # Wrapper to setup a reference object
  #
  def __init__(self, item = None):
    self.val = item
  
  #
  # Enforces a reference
  # @param Object data
  # @raise Exception 
  # @return Bool
  #
  @staticmethod
  def check(data):
    if not isinstance(data, Reference) or not hasattr(data, 'val'):
      raise Exception, "Argument must be an object and must contain a 'val' property."
    else:
      return True



#
# Class to handle super globals
#
class __SuperGlobals:
  
  #
  # _SERVER vars
  # If this is not being run from a webserver, we will simulate
  # the web server vars for CLI testing.
  # @return Dict
  #
  @staticmethod
  def getSERVER():
    env = dict(os.environ)
    if not env.has_key('DOCUMENT_ROOT'):
      out = {
        'WEB' : False,
        'DOCUMENT_ROOT': env['PWD'],
        'GATEWAY_INTERFACE': 'CGI/1.1',
        'HTTP_ACCEPT': 'text/xml,application/xml,application/xhtml+xml,' + \
          'text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'HTTP_ACCEPT_ENCODING': 'gzip,deflate',
        'HTTP_ACCEPT_LANGUAGE': 'en-us,en;q=0.5',
        'HTTP_CONNECTION': 'keep-alive',
        'HTTP_HOST': 'localhost',
        'HTTP_KEEP_ALIVE': '300',
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; ' + \
          'en-US; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
        'QUERY_STRING': '',
        'REMOTE_ADDR': '127.0.0.1',
        'REMOTE_PORT': '49999',
        'REQUEST_METHOD': 'GET',
        'REQUEST_URI': '/drupy.py',
        'SCRIPT_FILENAME': env['PWD'] + '/drupy.py',
        'SCRIPT_NAME': '/drupy.py',
        'SERVER_ADDR': '127.0.0.1',
        'SERVER_ADMIN': 'root@localhost',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'SERVER_SIGNATURE': '',
        'SERVER_SOFTWARE': 'Apache/2.2.8 (Unix) PHP/5.2.5'
      }
      return array_merge(env, out)
    else:
      env['WEB'] = True
      return env
  
  #
  # _GET vars
  # @return Dict
  #
  @staticmethod
  def getGET():
    return cgi.parse()
  
  #
  # _POST vars
  # @return Dict
  #
  @staticmethod
  def getPOST():
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
  # _REQUEST vars
  # @return Dict
  #
  @staticmethod
  def getREQUEST(get, post):
    return array_merge(get, post)
  
  #
  # _SESSION vars
  # @return Dict
  #
  @staticmethod
  def getSESSION():
    return None

# end __SuperGlobals



#
# Handles drupy output functions
#
class __Output:
  #
  # init
  #
  def __init__(self, usebuffer = True):
    self._usebuffer = usebuffer
    self._body = ""
    self._headers = {}
    if self._usebuffer:
      cgitb.enable()
      sys.stdout = self

  #
  # Write body
  # @param Str data
  #
  def write(self, data):
    if self._usebuffer:
      self._body += data
  
  #
  # Write headers
  # @param Str data
  #
  def header(self, data, replace = True):
    if self._usebuffer:
      parts = re.split('\s*:\s*', str(data), 1)
      parts_len = len(parts) 
      if parts_len > 0:
        if parts_len == 1:
          name = 'status'
          value = parts[0]
        elif parts_len == 2:
          name = parts[0].lower()
          value = parts[1]
        self._headers[name] = value

  #
  # Get header string
  # @param Str item 
  #
  def _get_header(self, item, remove = True):
    if self._headers.has_key(item):
      if item == 'status':
        out = "%s%s" % (self._headers[item], CRLF)
      else:
        out = "%s: %s%s" % (item, self._headers[item], CRLF)
      if remove:
        self._headers.pop(item)
    else:
      out = ''
    return out
  
  #
  # Set a header
  # @param Str item
  # @param Str val
  # @param Bool check
  # @return Bool
  #
  def _set_header(self, item, val, check = False):
    if not check or not self._headers.has_key(item):
      self._headers[item] = val
      return True
    return False
    
  #
  # Flush buffer
  # For now this is only constructed to work with CGI
  # Eventually this will need to be modified to work with WSGI
  #
  def flush(self):
    if self._usebuffer:
      sys.stdout = sys.__stdout__
      #self._set_header('status', "HTTP/1.1 200 OK", True)
      self._set_header('content-type', "text/html; Charset=UTF-8", True)
      #sys.stdout.write( self._get_header( 'status' ) )
      sys.stdout.write( self._get_header( 'content-type' ) )
      for k,v in self._headers.items():
        sys.stdout.write( self._get_header(k) )
      sys.stdout.write( CRLF )
      sys.stdout.write( self._body )
    
# end __Output



#
# Sets user-level session storage functions
# @param Func open_
# @param Func close_
# @param Func read_
# @param Func write_
# @param Func destroy_
# @param Func gc_
# @return Bool
#
def session_set_save_handler(open_, close_, read_, write_, destroy_, gc_):
  pass


#
# Initialize session data
# @return Bool
#
def session_start():
  global SESSION
  SESSION = session.SessionObject(os.environ, type='file', data_dir='/tmp')._session()
  header(SESSION.cookie)
  return True


#
# Get and/or set the current session name
# @param Str name
# @return Str
#
def session_name(name = "DrupySession"):
  pass


#
# THIS FUNCTION SHOULD BE DEPRECATED EVENTUALLY
# Sets globals variable
# @param Str name
# @param Number,Str val
# @return Bool
#
def define(name, val = None):
  v = {'name':name}
  if \
      isinstance(val, int) or \
      isinstance(val, float) or \
      isinstance(val, bool) or \
      val == None:
    v['val'] = val
  elif isinstance(val, str):
    v['val'] = "'%s'" % val
  else:
    return false
  out = ("%(name)s = %(val)s") % v
  exec(out, globals())
  return True
    

#
# Base 64 encode
#
def base64_encode(data):
  return base64.encodestring(data);

#
# Base 64 encode
#
def base64_decode(data):
  return base64.decodestring(data);



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
# Call user func
# @param Function func
# @param Tuple,List args
# @return Unknown
#
def call_user_func_array(func, args):
  return (eval(func)(*tuple(args)))
  


#
# Array filter
# @param Iterable item
# @param Function func
# @return Iterable
#
def array_filter(item, func):
  return filter(func, item)


#
# GD image size
# @param Str filename
# @return 
#
def getimagesize(filename):
  img = Image.open(filename)
  (w,h) = img.size
  t = "IMAGETYPE_%S" % img.format
  a = "width=\"%d\" height=\"%d\"" % img.size
  return (w,h,t,a)



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
def isset(obj, val = None, searchGlobal = False, data = {}):
  sVal = None
  # First check for single None value
  if val == None:
    return (obj != None)
  # Check object|list|dict > property|index|key
  else:
    # Dict
    if isinstance(obj, dict):
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
    elif isinstance(obj, list) or isinstance(obj, tuple):
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
def time_():
  return time.time()


#
# In array
# @param Str,Int val
# @param List,Dict,Object obj
# @return Bool
#
def in_array(val, obj):
  return (val in obj)


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
  elif isinstance(item, dict):
    k = item.keys()
    if len(k) > 0:
      return item.pop(k[0])
    else:
      return None
  else:
    return None


#
# Triggers error
#
# @param Str data
def trigger_error(data, errno):
  print data
  flush()
  exit

#
# Function exists
# @param Dict,List,Object obj
# @param Str val
# @return Bool
#
def function_exists(val, scope = globals()):
  return (isset(scope, val) and callable(scope[val]))


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
      isinstance(val, bool) and \
      (val == False):
    return True
  # None
  elif \
      val == None:
    return True
  # Lists
  elif \
      isinstance(val, list) or \
      isinstance(val, tuple) or \
      isinstance(val, dict):
    return (len(val) <= 0)
  # Numbers
  elif \
      isinstance(val, int) or \
      isinstance(val, float):
    return (val <= 0)
  # String
  elif \
      isinstance(val, str):
    return (val.strip() == '')
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
    execfile(filename, globals())
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
# Urlparse doesnt support 'mysql' or 'mysqli' schemes
# so, we need to add a fix for this.
# @param url
# @return Dict
#
def parse_url(url, port = 80):
  scheme = url[0:url.find("://")]
  if scheme not in ( \
    'file', 'ftp', 'gopher', 'hd1', 'http', 'https', 'imap', 'mailto', 'mms', \
    'news', 'nntp', 'prospero', 'rsync', 'rtsp', 'rtspu', 'sftp', 'shttp', \
    'sip', 'sips', 'snews', 'svn', 'svn+ssh', 'telnet', 'wais' \
  ):
    no_scheme = True
    url = url.replace(scheme, 'http', 1)
  else:
    no_scheme = False
  u = urlparse.urlparse(url)
  hasuser = u.netloc.find('@')
  d = {
    'scheme' : (scheme if no_scheme else u.scheme),
    'path' : u.path,
    'query' : u.query,
    'fragment' : u.fragment,
    'user' : (u.username if u.username != None else ''),
    'pass' : (u.password if u.password != None else ''),
    'port' : (u.port if u.port != None else port),
    'host' : u.netloc[((hasuser + 1) if (hasuser >= 0) else 0):]
  }
  return d


#
# Recursive pretty printer
# @param Any data
# @param Bool ret
# @return Bool,Str
#
def print_r(data, ret = False):
  try:
    d = dict(data)
  except:
    try:
      d = list(data)
    except:
      try:
        d = tuple(data)
      except:
        d = data
  if ret:
    return pprint.PrettyPrinter().pformat(d)
  else:
    pprint.PrettyPrinter().pprint(d)
    return True



#
# Cast to object
# @param Dict dic
# @return Object
#
def object_(dic):
  out = stdClass()
  for i in dic:
    setattr(out, i, dic[i])
  return out

#
# Cast to array
# @param Object obj
# @return Dict
#
def array_(obj):
  out = {}
  mag = '__'
  for i in dir(obj):
    if i[0:2] != mag and i[-2:] != mag:
      out[i] = getattr(obj, i)
  return out;


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
  searcher = reg.search(subject)
  if searcher == None:
    if match != None:
      match.val = []
    return 0
  else:
    g = list(searcher.groups())
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
# preg_replace wrapper
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def preg_replace(pat, rep, subject):
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
# Sets a static var
#
def static(func, prop, val = None):
  if not hasattr(func, prop):
    setattr(func, prop, val)
    return False
  else:
    return True


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
# Determines if "array"
# @param Any
# @return Bool
#
def is_array(val):
  return (
    isinstance(val, tuple) or \
    isinstance(val, dict) or \
    isinstance(val, list)
  )

#
# Determnes if object
#
def is_object(val):
  return isinstance(val, object)


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
def defined(val, scope = globals()):
  return isset(scope, val)


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
def md5(val):
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
# str replace real
# @param Str pat
# @param Str rep
# @param Str subject
# @return Str
#
def __str_replace_str(pat, rep, subject):
  return subject.replace(pat, rep)

#
# Real preg replace
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def __preg_replace_str(pat, rep, subject):
  reg = __preg_setup(pat)
  # function call
  if callable(rep):
    def __callback(match):
      match_list = list(match.groups())
      match_list.insert(0, subject)
      match_list = tuple(match_list)
      o = rep(match_list)
      return o
    return reg.sub(__callback, subject)
  # string
  else:
    return reg.sub(rep, subject)



#
# Initiate
#
__init()
