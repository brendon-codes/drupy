
#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file DrupyHelper.py
#  A PHP/MySQL abstraction layer for Python
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-05-10
# @version 0.1
# @depends MySQLdb
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

import MySQLdb

MYSQLI_ASSOC = 0
MYSQLI_CLIENT_FOUND_ROWS = 0

#
# Stores error information
#
class DrupyMySQL_meta:
  def __init__(self):
    self.error_connect = [-1, 'No Error']

  def setErrorConnect(self, n, v):
    self.error_connect = [n, v]

  def getErrorConnect(self):
    return self.error_connect


#
# Stores row information
#
class DrupyMySQL_row:
  def __init__(self):
    pass


#
# Opens DB Connections
# 
# @param NoneType link
# @param Str host
# @param Str username
# @param Str passwd
# @param Str dbname
# @param Int port
# @param Socket socket
# @param Int flags
# @return Instance[MySQLdb.connect]
#
def mysqli_real_connect(host = None, username = None, passwd = None,
    dbname = None, port = None, socket = '', flags = None):
  global DB_META
  connection = None
  try:
    connection = MySQLdb.connect(host, username, passwd, dbname, port)
  except MySQLdb.Error, e:
    DB_META.setErrorConnect(e.args[0], e.args[1])
  return connection;


#
# Gets last connect errno
#
# @return Int
# 
def mysqli_connect_errno():
  global DB_META
  return DB_META.getErrorConnect()[0]


#
# Gets last connect error
#
# @return Str
#
def mysqli_connect_error():
  global DB_META
  return DB_META.getErrorConnect()[1]


#
# Gets last db errno
# @param Instance[MySQLdb.connect] connection
# @return Int
#
def mysqli_errno(connection):
  return connection.errno()



#
# Gets last db error
# @param Instance[MySQLdb.connect] connection
# @return Str
#
def mysqli_error(connection):
  return connection.error()



#
# Runs a query
#
# @param Instance[MySQLdb.connect] connection
# @param Str query
# @param Int resultmode
# @return ???
#
def mysqli_query(connection, query, resultmode = None):
  cursor = MySQLdb.cursors.DictCursor(connection)
  try:
    cursor.execute(query)
  except MySQLdb.Error, e:
    pass
  return cursor


#
# Fetches one row
#
# @param MySQLdb.cursors.DictCursor cursor
# @return Tuple
#
def mysqli_fetch_row(cursor):
  return tuple(cursor.fetchone().values())



#
# Fetches row as dict
#
# @param MySQLdb.cursors.DictCursor cursor
# @return Dict
#
def mysqli_fetch_assoc(cursor):
  return cursor.fetchone()




#
# Fetches row as object
#
# @param MySQLdb.cursors.DictCursor cursor
# @return Object[DrupyMySQL_row]
#
def mysqli_fetch_object(cursor):
  row = cursor.fetchone()
  out = DrupyMySQL_row()
  for k,v in row.items():
    setattr(out, k, v)
  return out


#
# Escapes string
# @param MySQLdb.connection connection
# @param Str text
# @return Str
#
def mysqli_real_escape_string(connection, text):
  if isinstance(text, str):
    return connection.escape_string(text)
  else:
    return text


#
# Alias for other fetch functions
# @param MySQLdb.cursors.DictCursor cursor
# @return Object[DrupyMySQL_row] | Dict 
#
def mysqli_fetch_array(cursor, w = None):
  if w == MYSQLI_ASSOC:
    return mysqli_fetch_assoc(cursor)
  else:
    return mysqli_fetch_row(cursor)


#
# Gets affexted rows
# @param MySQLdb.cursors.DictCursor cursor
# @return Int
#
def mysql_affected_rows(cursor):
  return cursor.rowcount





#
# Dummy function
# @return Non
#
def mysqli_init():
  return None



DB_META = DrupyMySQL_meta()


