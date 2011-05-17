#!/usr/bin/env python

"""
    Utils for Drupy
    
    @package drupy
    @see <a href='http://drupy.net'>Drupy Homepage</a>
    @see <a href='http://drupal.org'>Drupal Homepage</a>
    @note Drupy is a port of the Drupal project.
    @author Brendon Crawford
    @copyright 2008 Brendon Crawford
    @contact message144 at users dot sourceforge dot net
    @created 2008-02-05
    @version 0.1
    @note License:

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to:
    
    The Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor,
    Boston, MA  02110-1301,
    USA
"""

__version__ = "$Revision: 1 $"

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
import htmlentitydefs
import urllib
from PIL import Image


def array_intersect_key(arr):
    pass


def array_flip(arr):
    pass


def base64_encode(data):
    """
        Base 64 encode
        
        @param data String
        @return String
    """
    return base64.encodestring(data);


def base64_decode(data):
  """
   Base 64 encode
  """
  return base64.decodestring(data);



def scandir(path_):
  """
  List files and directories inside the specified path
  
  @param path_ Str
  @return Tuple
  """
  return os.listdir


def uasort(item, func):
  """
   Sort on func
   @param item Iterable
   @param func Function
   @return Iterable
  """
  return sort(item, func)



def array_filter(item, func):
  """
   Array filter
   @param item Iterable
   @param func Function
   @return Iterable
  """
  return filter(func, item)


def getimagesize(filename):
  """
   GD image size
   @param filename Str
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
   @param delim Str
   @param val Str
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
   @param filename Str
   @return Bool
  """ 
  return os.access(filename, os.W_OK)


def is_dir(filename):
  """
   Checks file is directory
   @param filename Str
   @param inplace Bool
   @param empty_source Bool
   @return Bool
  """
  return os.path.isdir(filename)


def array_merge(a1, a2, inplace=False, empty_source=False):
  """
   Merges lists
   @param a1 Dict,List
   @param a2 Dict,List
   @return Dict,List 
  """ 
  if inplace:
    out = a1
  else:
    out = copy.deepcopy(a1)
  if empty_source:
    for i in range(len(out)):
      out.pop()
  for k in a2:
    out[k] = a2[k]
  return out


def array_keys(item):
  """
   Get keys
   @param item Dict
   @return List
  """
  return item.keys()


def array_key_exists(name, item):
  """
   Has key
   @param item Str
   @param item Dict
   @return Bool
  """
  return item.has_key(name);


def isset(obj, val=None, searchGlobal=False):
  """
   Check variable existance
   @param obj Dict,List,Object
   @param val Str,Int
   @param searchGlobal Bool
  """
  sVal = None
  # First check for single None value
  if val is None:
    return (obj is not None)
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
        return True
      else:
        return False
    # List
    elif isinstance(obj, list) or isinstance(obj, tuple):
      if (val < len(obj)):
        return True
      else:
        return False
    # Object
    elif isinstance(obj, object):
      if hasattr(obj, val):
        return True
      else:
        return False
    # Others unknown
    else:
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
   @param val Str,Int
   @param obj List,Dict,Object
   @return Bool
  """
  return (val in obj)


def array_fill(start, cnt, val):
  """
   Fills array
   @param start Int
   @param cnt Int
   @param val Str
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
   @param item List,Dict,Tuple
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



def function_exists(val, scope = globals()):
  """
   Function exists
   @param obj Dict,List,Object
   @param val Str
   @return Bool
  """
  if not isinstance(scope, dict):
    return (hasattr(scope, val) and callable(getattr(scope, val)))
  else:
    return (scope.has_key(val) and callable(scope[val]))


def htmlspecialchars(val, flags = None):
  """
   html special chars
   @param val Str
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



def strtr(text, items):
  """
   Translate characters
   Inspired by snippet from Xavier Defrang
   @see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
  """
  regex = re.compile("(%s)" % "|".join(map(re.escape, items.keys())))
  out = regex.sub(lambda mo: items[mo.string[mo.start():mo.end()]], text)
  return out



def implode(delim, items):
  """
   Implodes
   @param delim Str
   @param items List
   @return Str
  """
  return delim.join(items)


def array_slice(items, a1, a2 = None):
  """
   Array slice
   @param items List,Dict
   @param a1 Int
   @param a2 Int
   @return Mixed
  """
  if (a2 is None):
    return items[a1:]
  else:
    return items[a1:a2]


def rtrim(val, chars = None):
  """
   R Trim
   @param val Str
   @return Str
  """
  if chars != None:
    return val.rstrip(chars)
  else:
    return val.rstrip()


def ltrim(val, chars = None):
  """
   L trim
   @param val Str
   @return Str
  """
  if chars != None:
    return val.lstrip(chars)
  else:
    return val.lstrip()


def is_file(filename):
  """
   Check regular file
   @param filename String
   @return Bool
  """
  return os.path.isfile(filename)


def file_exists(filename):
  """
   Check file exists
   @param filename Str
   @return Bool
  """
  return os.path.exists(filename)



def urldecode(val):
  """
   Url decoder
   @param val Str
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
  if scheme not in (\
                    'file', 'ftp', 'gopher', 'hd1', 'http', 'https', \
                    'imap', 'mailto', 'mms', \
                    'news', 'nntp', 'prospero', 'rsync', 'rtsp', 'rtspu', \
                    'sftp', 'shttp', \
                    'sip', 'sips', 'snews', 'svn', 'svn+ssh', \
                    'telnet', 'wais'):
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


def array_(obj):
  """
   Cast to array
   @param obj Object
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
   @param val Str
   @return Int
  """ 
  return len(val)


def array_reverse(items):
  """
   Reverses list
   @param items List
   @return List
  """
  rItems = copy.deepcopy(items)
  rItems.reverse()
  return rItems


def uniqid(prefix = None, more_entropy = False):
  """
   Returns unique id
   @param prefix Str
   @param more_entropy Bool
   @return Str
  """
  out = ''
  num = (23 if more_entropy else 13)
  if prefix != None:
    random.seed(prefix)
  for i in range(0, num):
    out += random.choice(\
                         'abcdefghijklmnopqrstuvwxyz' + \
                         'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                         '0123456789')
  return out


def mt_rand(min = 0, max = sys.maxint):
  """
   Random
   @param min Int
   @param max Int
   @return Int
  """
  return random.randint(min, max)


def dirname(path):
  """
   dir name
   @param path Str
   @return Str
  """
  return os.path.dirname(path)


def trim(val, chars = None):
  """
   trim whitespace
   @param val Str
   @return Str
  """
  if chars != None:
    return val.strip(chars)
  else:
    return val.strip()


def count(item):
  """
   Gets array count
   @param item List,Dict
   @return Int
  """
  return len(item)


def is_numeric(val):
  """
   Determines whether or not is numeric
   @param val Any
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



def is_string(val):
  """
   Determines if string
   @param Any
   @return Bool
  """
  return (
    isinstance(val, unicode) or \
    isinstance(val, str)      
  )



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
   @param val Any
  """
  return (val is None)


def strpos(haystack, needle):
  """
   Gets str pos
   @param haystack Str
   @param needle Str
   @return Int,Bool
  """
  pos = haystack.find(needle)
  if pos < 0:
    return False
  else:
    return pos


def serialize(obj):
  """
   serializer
   @param obj Any
   @return Str
  """
  return pickle.dumps(obj)


def unserialize(val):
  """
   unserializer
   @param val Str
   @return Obj
  """
  return pickle.loads(val)



def gmdate(format, stamp = None):
  """
   GMT date
   @param format Str
   @param stamp Int
   @return Str
  """
  if stamp is None:
    stamp = time.time()
  dt = datetime.datetime.utcfromtimestamp(stamp)
  return dt.strftime(format)


def stripslashes(val):
  """
   Strip slashes
   @param val Str
   @retun Str
  """
  return val.replace('\\', '')


def addslashes(val):
  """
   Add slashes
   @param val Str
   @return Str
  """
  return re.escape(val)
  

def md5(val):
  """
   md5
   @param val Str
   @return Str
  """
  return hashlib.md5(val).hexdigest()

def gzinflate(val):
  """
   decompress
   @param val Str
   @return Str
  """
  return zlib.decompress(val)


def gzdeflate():
  """
   compress
   @param val Str
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


def str_replace(pat, rep, subject):
  """
   str replace real
   @param pat Str
   @param rep Str
   @param subject Str
   @return Str
  """
  return subject.replace(pat, rep)


