#!/usr/bin/env python

"""
 @package Drupy
 @see http://drupy.net
 @note Drupy is a port of the Drupal project.
  The Drupal project can be found at http://drupal.org
 @file DrupyHelper.py
  A PHP abstraction layer for Python
  This file currently is built to working only with CGI.
  Eventually it will be constructed to work with WSGI
 @author Brendon Crawford
 @copyright 2008 Brendon Crawford
 @contact message144 at users dot sourceforge dot net
 @created 2008-02-05
 @version 0.1
 @depends Image (http://www.pythonware.com/products/pil/)
 @depends Hashlib (http://code.krypto.org/python/hashlib/)
 @depends Zlib (http://linux.maruhn.com/sec/python-zlib.html)
 @license: 

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

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

def __init():
  """
   Initiate superglobals and set output buffering
  """
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


class stdClass:
  """
   Std class
  """
  def __init__(self): pass


class Reference:
  """
   Reference class
  """

  """
   Wrapper to setup a reference object
  """
  def __init__(self, item = None):
    self.val = item
  
  """
   Enforces a reference
   @param Object data
   @raise Exception 
   @return Bool
  """
  @staticmethod
  def check(data):
    if not isinstance(data, Reference) or not hasattr(data, 'val'):
      raise Exception, "Argument must be an object and must contain a 'val' property."
    else:
      return True

class __SuperGlobals:  
  """
   Class to handle super globals
  """
  
  @staticmethod
  def getSERVER():
    """
     _SERVER vars
     If this is not being run from a webserver, we will simulate
     the web server vars for CLI testing.
     @return Dict
    """
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
  
  @staticmethod
  def getGET():
    """
     _GET vars
     @return Dict
    """
    return cgi.parse()
  
  @staticmethod
  def getPOST():
    """
     _POST vars
     @return Dict
    """
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

  @staticmethod
  def getREQUEST(get, post):
    """
     _REQUEST vars
     @return Dict
    """
    return array_merge(get, post)
  
  @staticmethod
  def getSESSION():
    """
     _SESSION vars
     @return Dict
    """
    return None

# end __SuperGlobals


class __Output:
  """
   Handles drupy output functions
  """

  def __init__(self, usebuffer = True):
    """
     init
    """
    self._usebuffer = usebuffer
    self._body = ""
    self._headers = {}
    if self._usebuffer:
      cgitb.enable()
      sys.stdout = self

  def write(self, data):
    """
     Write body
     @param Str data
    """
    if self._usebuffer:
      self._body += data
  
  def header(self, data, replace = True):
    """
     Write headers
     @param Str data
    """
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

  def _get_header(self, item, remove = True):
    """
     Get header string
     @param Str item 
    """
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
  

  def _set_header(self, item, val, check = False):
    """
     Set a header
     @param Str item
     @param Str val
     @param Bool check
     @return Bool
    """
    if not check or not self._headers.has_key(item):
      self._headers[item] = val
      return True
    return False
    

  def flush(self):
    """
     Flush buffer
     For now this is only constructed to work with CGI
     Eventually this will need to be modified to work with WSGI
    """
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


def session_set_save_handler(open_, close_, read_, write_, destroy_, gc_):
  """
   Sets user-level session storage functions
   @param Func open_
   @param Func close_
   @param Func read_
   @param Func write_
   @param Func destroy_
   @param Func gc_
   @return Bool
  """
  pass


def session_start():
  """
   Initialize session data
   @return Bool
  """
  global SESSION
  SESSION = session.SessionObject(os.environ, type='file', data_dir='/tmp')._session()
  header(SESSION.cookie)
  return True


def session_name(name = "DrupySession"):
  """
   Get and/or set the current session name
   @param Str name
   @return Str
  """
  pass


def define(name, val = None):
  """
   THIS FUNCTION SHOULD BE DEPRECATED EVENTUALLY
   Sets globals variable
   @param Str name
   @param Number,Str val
   @return Bool
  """
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
    

def base64_encode(data):
  """
   Base 64 encode
  """
  return base64.encodestring(data);


def base64_decode(data):
  """
   Base 64 encode
  """
  return base64.decodestring(data);


def error_get_last():
  """
   Gets error.
   This does not mimic the exact behaviour of the
   corresponding PHP function
  
   @return Tuple
   @returnprop Int 0
   @returnprop Str 1
   @returnprop Str 2
   @returnprop Int 3
   @returnprop Dict 4
   @returnprop Type 5
  """
  err = sys.exc_info();
  return (
    E_ALL,            #errno
    err[1],           #errstr
    "NOT-AVAILABLE",  #errfile
    err[2].tb_lineno, #errline
    globals(),        #errcontext
    err[0]            #errtype
  )



def uasort(item, func):
  """
   Sort on func
   @param Iterable item
   @param Function func
   @return Iterable
  """
  return sort(item, func)



def call_user_func_array(func, args):
  """
   Call user func
   @param Function func
   @param Tuple,List args
   @return Unknown
  """
  return func(*tuple(args))
  


def array_filter(item, func):
  """
   Array filter
   @param Iterable item
   @param Function func
   @return Iterable
  """
  return filter(func, item)


def getimagesize(filename):
  """
   GD image size
   @param Str filename
   @return 
  """
  img = Image.open(filename)
  (w,h) = img.size
  t = "IMAGETYPE_%S" % img.format
  a = "width=\"%d\" height=\"%d\"" % img.size
  return (w,h,t,a)


def explode(delim, val, limit = None):
  """
   Splits string on delim
   @param Str delim
   @param Str val
   @return Str
  """  
  if limit != None:
    return val.split(delim, limit)
  else:
    return val.split(delim)


def microtime():
  """
   Gets microtime
   @return Str
  """
  (sec, usec) = str(time.time()).split('.')
  return " ".join(['.' + usec, sec])


def is_writable(filename):
  """
   CHecks file is writeable
   @param Str filename
   @return Bool
  """ 
  return os.access(filename, os.W_OK)


def is_dir(filename):
  """
   Checks file is directory
   @param Str filename
   @return Bool
  """
  return os.path.isdir(filename)


def array_merge(a1, a2):
  """
   Merges lists
   @param Dict,List a1
   @param Dict,List a2
   @return Dict,List 
  """ 
  out = copy.deepcopy(a1)
  for k in a2:
    out[k] = a2[k]
  return out


def array_keys(item):
  """
   Get keys
   @param Dict item
   @return List
  """
  return item.keys()


def array_key_exists(name, item):
  """
   Has key
   @param Str item
   @param Dict item
   @return Bool
  """
  return item.has_key(name);


def isset(obj, val = None, searchGlobal = False, data = {}):
  """
   Check variable existance
   @param Dict,List,Object obj
   @param Str,Int val
   @param Bool searchGlobal
  """
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


def time_():
  """
   Get time
   @return Int
  """
  return time.time()


def in_array(val, obj):
  """
   In array
   @param Str,Int val
   @param List,Dict,Object obj
   @return Bool
  """
  return (val in obj)


def array_fill(start, cnt, val):
  """
   Fills array
   @param Int start
   @param Int cnt
   @param Str val
   @return Dict
  """
  r = {}
  i = start
  while i <= (start + cnt):
    r[i] = val
    i += 1
  return r


def array_shift(item):
  """
   Shifts array
   @param List,Dict,Tuple item
   @return Mixed
  """
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


def trigger_error(data, errno):
  """
   Triggers error
  
   @param Str data
  """
  print data
  flush()
  exit


def function_exists(val, scope = globals()):
  """
   Function exists
   @param Dict,List,Object obj
   @param Str val
   @return Bool
  """
  return (isset(scope, val) and callable(scope[val]))


def htmlspecialchars(val, flags = None):
  """
   html special chars
   @param Str val
   @return Str
  """
  out = ""
  for i in range(0, len(val)):
    num = ord(unicode(val[i]))
    if htmlentitydefs.codepoint2name.has_key(num):
      out += "&%s;" % htmlentitydefs.codepoint2name[num]
    else:
      out += val[i]
  return out



def empty(val):
  """
   Checks for empty
   @param Any obj
   @param Bool searchGlobal
   @param Str val
   @return Bool
  """
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



def strtr(text, items):
  """
   Translate characters
   Inspired by snippet from Xavier Defrang
   @see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
  """
  regex = re.compile("(%s)" % "|".join(map(re.escape, items.keys())))
  out = regex.sub(lambda mo: items[mo.string[mo.start():mo.end()]], text)
  return out


def is_uploaded_file(filename):
  """
   Check if uploaded file
   @param Str filename
   @return Bool
  """
  return True



def implode(delim, items):
  """
   Implodes
   @param Str delim
   @param List items
   @return Str
  """
  return delim.join(items)


def array_slice(items, a1, a2 = None):
  """
   Array slice
   @param List,Dict items
   @param Int a1
   @param Int a2
   @return Mixed
  """
  if (a2 == None):
    return items[a1:]
  else:
    return items[a1:a2]


def rtrim(val, chars = None):
  """
   R Trim
   @param Str val
   @return Str
  """
  if chars != None:
    return val.rstrip(chars)
  else:
    return val.rstrip()


def ltrim(val, chars = None):
  """
   L trim
   @param Str val
   @return Str
  """
  if chars != None:
    return val.lstrip(chars)
  else:
    return val.lstrip()


def is_file(filename):
  """
   Check regular file
   @param String filename
   @return Bool
  """
  return os.path.isfile(filename)


def file_exists(filename):
  """
   Check file exists
   @param Str filename
   @return Bool
  """
  return os.path.exists(filename)


def include(filename, scope = None):
  """
   Includes file
   @param Str filename
   @param Dict scope
   @return Bool
  """
  if (scope != None):
    execfile(filename, scope)
  else:
    execfile(filename, globals())
  return True


def urldecode(val):
  """
   Url decoder
   @param Str val
   @return Str
  """
  return urllib.unquote_plus(val)


def parse_url(url, port = 80):
  """
   Parse url
   Urlparse doesnt support 'mysql' or 'mysqli' schemes
   so, we need to add a fix for this.
   @param url
   @return Dict
  """
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


def print_r(data, ret = False):
  """
   Recursive pretty printer
   @param Any data
   @param Bool ret
   @return Bool,Str
  """
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

def object_(dic):
  """
   Cast to object
   @param Dict dic
   @return Object
  """
  out = stdClass()
  for i in dic:
    setattr(out, i, dic[i])
  return out

def array_(obj):
  """
   Cast to array
   @param Object obj
   @return Dict
  """
  out = {}
  mag = '__'
  for i in dir(obj):
    if i[0:2] != mag and i[-2:] != mag:
      out[i] = getattr(obj, i)
  return out;


def strlen(val):
  """
   Get strlen
   @param Str val
   @return Int
  """ 
  return len(val)


def array_reverse(items):
  """
   Reverses list
   @param List items
   @return List
  """
  rItems = copy.deepcopy(items)
  rItems.reverse()
  return rItems



def preg_quote(val, delim = None):
  """
   Escapes regular expression
   @param Str val
   @param Any delim
      Not used
   @return Str
  """
  return re.escape(val)


def preg_match(pat, subject, match = None):
  """
   Convert PHP preg_match to Python matcher
   @param Str pat
   @param Str subject
   @param Dict match
   @return Dict
   @returnprop List match
  """
  if match != None:
    Reference.check(match)
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


def preg_match_all(pat, subject, matches = None):
  """
   Preg Match all
   @param Str pat
   @param Str subject
   @param Reference &matches
   @return Int
  """
  if matches != None:
    Reference.check(matches)
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
    

def uniqid(prefix = None, more_entropy = False):
  """
   Returns unique id
   @param Str prefix
   @param Bool more_entropy
   @return Str
  """
  out = ''
  num = (23 if more_entropy else 13)
  if prefix != None:
    random.seed(prefix)
  for i in range(0, num):
    out += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
  return out


def mt_rand(min = 0, max = sys.maxint):
  """
   Random
   @param Int min
   @param Int max
   @return Int
  """
  return random.randint(min, max)


"""
 str replace wrapper
 @param Str pat
 @param Str rep
 @param Str subject
 @return Str
"""
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
  


def preg_replace(pat, rep, subject):
  """
   preg_replace wrapper
   @param Str pat
   @param Str replace
   @param Str subject
   @return Str
  """
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


def dirname(path):
  """
   dir name
   @param Str path
   @return Str
  """
  return os.path.dirname(path)


def trim(val, chars = None):
  """
   trim whitespace
   @param Str val
   @return Str
  """
  if chars != None:
    return val.strip(chars)
  else:
    return val.strip()


def count(item):
  """
   Gets array count
   @param List,Dict item
   @return Int
  """
  return len(item)

def static(func, prop, val = None):
  """
   Sets a static var
  """
  if not hasattr(func, prop):
    setattr(func, prop, val)
    return False
  else:
    return True


def is_numeric(val):
  """
   Determines whether or not is numeric
   @param Any val
   @return Bool
  """
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


def is_array(val):
  """
   Determines if "array"
   @param Any
   @return Bool
  """
  return (
    isinstance(val, tuple) or \
    isinstance(val, dict) or \
    isinstance(val, list)
  )

def is_object(val):
  """
   Determnes if object
  """
  return isinstance(val, object)


def is_null(val):
  """
   Is null
   @param Any val
  """
  return (val == None)


def strpos(haystack, needle):
  """
   Gets str pos
   @param Str haystack
   @param Str needle
   @return Int,Bool
  """
  pos = haystack.find(needle)
  if pos < 0:
    return False
  else:
    return pos


def ini_set(name, val):
  """
   Pretends to set an ini
   Actually just sets a global
   @param Str name
   @param Str,Number,None,Bool val
   @return Bool
  """
  define(name.replace('.', '_'), val)
  return True


def serialize(obj):
  """
   serializer
   @param Any obj
   @return Str
  """
  return pickle.dumps(obj)


def unserialize(val):
  """
   unserializer
   @param Str val
   @return Obj
  """
  return pickle.loads(val)


def defined(val, scope = globals()):
  """
   Checks for defined var
  """
  return isset(scope, val)


def gmdate(format, stamp = None):
  """
   GMT date
   @param Str format
   @param Int stamp
   @return Str
  """
  if stamp == None:
    stamp = time.time()
  dt = datetime.datetime.utcfromtimestamp(stamp)
  return dt.strftime(format)


def stripslashes(val):
  """
   Strip slashes
   @param Str val
   @retun Str
  """
  return val.replace('\\', '')


def addslashes(val):
  """
   Add slashes
   @param Str val
   @return Str
  """
  return re.escape(val)
  

def md5(val):
  """
   md5
   @param Str val
   @return Str
  """
  return hashlib.md5(val).hexdigest()

def gzinflate(val):
  """
   decompress
   @param Str val
   @return Str
  """
  return zlib.decompress(val)


def gzdeflate():
  """
   compress
   @param Str val
   @return Str
  """
  return zlib.compress(val)



def array_pop(item):
  """
   Pops item
   @param item
   @return Mixed
  """
  return item.pop()



def __preg_setup(pat):
  """
   prepares pattern for python regex
   @param Str pat
   @return _sre.SRE_Pattern
      Regular Expression object
  """
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


def __str_replace_str(pat, rep, subject):
  """
   str replace real
   @param Str pat
   @param Str rep
   @param Str subject
   @return Str
  """
  return subject.replace(pat, rep)



def __preg_replace_str(pat, rep, subject):
  """
   Real preg replace
   @param Str pat
   @param Str replace
   @param Str subject
   @return Str
  """
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
