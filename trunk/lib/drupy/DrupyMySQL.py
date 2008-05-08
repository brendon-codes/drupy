#
# DrupyMySQL.py
# A PHP/MySQL abstraction layer for Python
# 
# @package Drupy
# @file DrupyMySQL.py
# @module drupy.php
# @author Brendon Crawford
# @see http://drupy.sourceforge.net
# @created 2008-05-08
# @version 0.1.1
# @modified 2008-08-20
#
# Required modules that might not be installed by default or included with Drupy:
#    Image (http://www.pythonware.com/products/pil/)
#    Hashlib (http://code.krypto.org/python/hashlib/)
#    Zlib (http://linux.maruhn.com/sec/python-zlib.html)
#

import MySQLdb

#
# Stores error information
#
class drupymysql_meta:
  def __init__(self):
    self.error = []
    self.error_connect = []
  
  def setError(self, n, v):
    self.error = [n, v]
  
  def setErrorConnect(self, n, v):
    self.error_connect = [n, v]

  def getError(self):
    return self.error
  
  def setErrorConnect(self):
    return self.error_connect



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
def mysqli_real_connect(link = None, host = None, username = None, passwd = None,
    dbname = None, port = None, socket = None, flags = None):
  global DB
  global DB_META
  try:
    DB = MySQLdb.connect(host, username, passwd, dbname, port, socket)
  except MySQLdb.Error, e:
    DB_META.setError(e.args[0], e.args[1])
    DB_META.setErrorConnect(e.args[0], e.args[1])
  return connection;


#
# Gets last connect error
#
# @return Int
# 
def mysqli_connect_errno():
  global DB_META
  return DB_META.getErrorConnect[0]


#
# Runs a query
#
# @param Instance[MySQLdb.connect] connection
# @param Str query
# @param Int resultmode
# @return ???
#
def mysqli_query(connection, query, resultmode = None):
  cursor = connecion.cursor()
  cursor.execute(query)
  return cursor


#
# Fetches one row
#
# @param MySQLdb.cursor cursor
# @return Tuple
#
def mysqli_fetch_row(cursor):
  return cursor.fetchone()



#
# Dummy function
# @return Non
#
def mysqli_init():
  return None



DB_META = drupymysql_meta()
DB = None


