#!/usr/bin/env python


"""
 @package Drupy
 @see http://drupy.net
 @note Drupy is a port of the Drupal project.
  The Drupal project can be found at http://drupal.org
 @file DrupyHelper.py
  A PHP/MySQL abstraction layer for Python
 @author Brendon Crawford
 @copyright 2008 Brendon Crawford
 @contact message144 at users dot sourceforge dot net
 @created 2008-05-10
 @version 0.1
 @depends MySQLdb
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

import MySQLdb
from lib.drupy import DrupyPHP as p 
from lib.drupy import DrupyHelper

MYSQLI_ASSOC = 0
MYSQLI_CLIENT_FOUND_ROWS = 0

class __DrupyMySQLMeta:
  """
  Stores error information
  """
  def __init__(self):
    self.error_connect = [-1, 'No Error']

  def setErrorConnect(self, n, v):
    self.error_connect = [n, v]

  def getErrorConnect(self):
    return self.error_connect


class __DrupyMySQLRow:
  """
   Stores row information
  """
  def __init__(self):
    pass


def mysqli_real_connect(host = None, username = None, passwd = None,
    dbname = None, port = None, socket = '', flags = None):
  """
   Opens DB Connections
   
   @param NoneType link
   @param Str host
   @param Str username
   @param Str passwd
   @param Str dbname
   @param Int port
   @param Socket socket
   @param Int flags
   @return Instance[MySQLdb.connect]
  """
  global __DB_META
  connection = None
  try:
    connection = MySQLdb.connect(host, username, passwd, dbname, port)
  except MySQLdb.Error, e:
    __DB_META.setErrorConnect(e.args[0], e.args[1])
  return connection;


def mysqli_connect_errno():
  """
   Gets last connect errno
  
   @return Int
  """ 
  global __DB_META
  return __DB_META.getErrorConnect()[0]


def mysqli_connect_error():
  """
   Gets last connect error
  
   @return Str
  """
  global __DB_META
  return __DB_META.getErrorConnect()[1]


def mysqli_errno(connection):
  """
   Gets last db errno
   @param Instance[MySQLdb.connect] connection
   @return Int
  """
  return connection.errno()


def mysqli_error(connection):
  """
   Gets last db error
   @param Instance[MySQLdb.connect] connection
   @return Str
  """
  return connection.error()



def mysqli_query(connection, query, resultmode = None):
  """
   Runs a query
  
   @param Instance[MySQLdb.connect] connection
   @param Str query
   @param Int resultmode
   @return ???
  """
  #DrupyHelper.output(True, type(connection))
  cursor = MySQLdb.cursors.DictCursor(connection)
  try:
    cursor.execute(query)
  except MySQLdb.Error, e:
    pass
  return cursor


def mysqli_fetch_row(cursor):
  """
   Fetches one row
  
   @param MySQLdb.cursors.DictCursor cursor
   @return Tuple
  """
  return tuple(cursor.fetchone().values())


def mysqli_fetch_assoc(cursor):
  """
   Fetches row as dict
  
   @param MySQLdb.cursors.DictCursor cursor
   @return Dict
  """
  return cursor.fetchone()


"""
 Fetches row as object

 @param MySQLdb.cursors.DictCursor cursor
 @return Object[DrupyMySQL_row]
"""
def mysqli_fetch_object(cursor):
  row = cursor.fetchone()
  out = __DrupyMySQLRow()
  if row != None:
    for k,v in row.items():
      setattr(out, k, v)
    return out
  else:
    return False

def mysqli_real_escape_string(connection, text):
  """
   Escapes string
   @param MySQLdb.connection connection
   @param Str text
   @return Str
  """
  if isinstance(text, str):
    return connection.escape_string(text)
  else:
    return text


def mysqli_fetch_array(cursor, w = None):
  """
   Alias for other fetch functions
   @param MySQLdb.cursors.DictCursor cursor
   @return Object[DrupyMySQL_row] | Dict 
  """
  if w == MYSQLI_ASSOC:
    return mysqli_fetch_assoc(cursor)
  else:
    return mysqli_fetch_row(cursor)


def mysqli_affected_rows(cursor):
  """
   Gets affexted rows
   @param MySQLdb.cursors.DictCursor cursor
   @return Int
  """
  return int(cursor.rowcount)


def mysqli_init():
  """
   Dummy function
   @return None
  """
  return None



__DB_META = __DrupyMySQLMeta()

#
# Aliases
#
mysqli_num_rows = mysqli_affected_rows


