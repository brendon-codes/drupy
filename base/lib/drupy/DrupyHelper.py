

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file DrupyHelper.py
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-02-27
# @version 0.1
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
# Converts a filename to import path
# @param filename
# @return Str
#
def get_import(filename):
  name = filename.replace('/', '.')
  mod = __import__(name)
  components = name.split('.')
  for comp in components[1:]:
      mod = getattr(mod, comp)
  return mod


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
# str replace real
# @param Str pat
# @param Str rep
# @param Str subject
# @return Str
#
def str_replace_str(pat, rep, subject):
  return subject.replace(pat, rep)

#
# Real preg replace
# @param Str pat
# @param Str replace
# @param Str subject
# @return Str
#
def preg_replace_str(pat, rep, subject):
  reg = preg_setup(pat)
  # function call
  if callable(rep):
    def __callback(match):
      match_list = list(match.groups())
      match_list.insert(0, subject)
      match_list = tuple(match_list)
      return rep(match_list)
    return reg.sub(__callback, subject)
  # string
  else:
    return reg.sub(rep, subject)


#
# Debug HTTP output message
# @param Str data
#
def output(should_die, *data):
  print "Content-Type: text/plain; Charset=UTF-8;\r\n\r\n"
  print data
  if should_die:
    exit()
  else:
    return True


#
# Reference class
#
class Reference:
  def __init__(self):
    self.val = None
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
class SuperGlobals:
  
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


