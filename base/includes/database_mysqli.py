# Id: database.mysqli.inc,v 1.57 2008/04/14 17:48:33 dries Exp $


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The drupal project can be found at http://drupal.org
# @file database_mysqli.py (ported from Drupal's database.mysqli.inc)
#  Database interface code for MySQL database servers using the mysqli client
#  libraries. mysqli is included in PHP 5 by default and allows developers to
#  use the advanced features of MySQL 4.1.x, 5.0.x and beyond.
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-01-10
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


 # Maintainers of this file should consult:
 # http://www.php.net/manual/en/ref.mysqli.php
#
# @ingroup database
# @{
#

# Include functions shared between mysql and mysqli.
require_once( './includes/database_mysql-common.py' )


#
# Report database status.
#
def db_status_report(phase):
  t = get_t()
  version = db_version()
  form['mysql'] = {
    'title' : t('MySQL database'),
    'value' : (l(version, 'admin/reports/status/sql') if (phase == 'runtime') else version),
  }
  if (version_compare(version, DRUPAL_MINIMUM_MYSQL) < 0):
    form['mysql']['severity'] = REQUIREMENT_ERROR
    form['mysql']['description'] = t('Your MySQL Server is too old + Drupal requires at least MySQL %version.', {'%version' : DRUPAL_MINIMUM_MYSQL})
  return form



#
# Returns the version of the database server currently in use.
#
# @return Database server version
#
def db_version():
  global active_db
  version = explode('-', mysqli_get_server_info(active_db))
  return version



#
# Initialise a database connection.
#
# Note that mysqli does not support persistent connections.
#
def db_connect(url):
  # Check if MySQLi support is present in PHP
  if (not function_exists('mysqli_init') and not extension_loaded('mysqli')):
    _db_error_page('Unable to use the MySQLi database because the MySQLi extension for PHP is not installed + Check your <code>php.ini</code> to see how you can enable it.')
  url = parse_url(url, 3306)
  # Decode url-encoded information in the db connection string
  url['user'] = urldecode(url['user'])
  # Test if database url has a password.
  url['pass'] = (urldecode(url['pass']) if isset(url, 'pass') else '')
  url['host'] = urldecode(url['host'])
  url['path'] = urldecode(url['path'])
  if (not isset(url, 'port')):
    url['port'] = None
  connection  = mysqli_real_connect(url['host'], url['user'], url['pass'], substr(url['path'], 1), url['port'], '', MYSQLI_CLIENT_FOUND_ROWS)
  if (mysqli_connect_errno() > 0):
    _db_error_page(mysqli_connect_error())
  # Force UTF-8.
  mysqli_query(connection, 'SET NAMES "utf8"')
  # Require ANSI mode to improve SQL portability.
  mysqli_query(connection, "SET SESSION sql_mode='ANSI'")
  return connection



#
# Helper function for db_query().
#
def _db_query(query, debug = 0):
  global active_db, queries, user
  if (variable_get('dev_query', 0)):
    usec,sec = explode(' ', microtime())
    timer = float(usec) + float(sec)
    # If devel.module query logging is enabled, prepend a comment with the username and calling function
    # to the SQL string. This is useful when running mysql's SHOW PROCESSLIST to learn what exact
    # code is issueing the slow query.
    bt = debug_backtrace()
    # t() may not be available yet so we don't wrap 'Anonymous'
    name = (user.name if (user.uid > 0) else variable_get('anonymous', 'Anonymous'))
    # str_replace() to prevent SQL injection via username or anonymous name.
    name = str_replace(['*', '/'], '', name)
    query = '/* ' +  name  + ' : ' . bt[2]['function'] + ' */ ' + query
  result = mysqli_query(active_db, query)
  if (variable_get('dev_query', 0)):
    query = bt[2]['function'] +  "\n"  + query
    usec,sec = explode(' ', microtime())
    stop = float(usec) + float(sec)
    diff = stop - timer
    queries.append( [query, diff] )
  if (debug):
    print '<p>query: ' +  query  + '<br />error:' + mysqli_error(active_db) + '</p>'
  if (not mysqli_errno(active_db)):
    return result
  else:
    # Indicate to drupal_error_handler that this is a database error.
    DB_ERROR = True
    trigger_error(check_plain(mysqli_error(active_db) +  "\nquery: "  + query), E_USER_WARNING)
    return False



#
# Fetch one result row from the previous query as an object.
#
# @param result
#   A database query result resource, as returned from db_query().
# @return
#   An object representing the next row of the result, or False. The attributes
#   of this object are the table fields selected by the query.
#
def db_fetch_object(result):
  if (result):
    _object = mysqli_fetch_object(result)
    return (_object if (_object != None) else False)




#
# Fetch one result row from the previous query as an array.
#
# @param result
#   A database query result resource, as returned from db_query().
# @return
#   An associative array representing the next row of the result, or False.
#   The keys of this object are the names of the table fields selected by the
#   query, and the values are the field values for this result row.
#
def db_fetch_array(result):
  if (result):
    _array = mysqli_fetch_array(result, MYSQLI_ASSOC)
    return (_array if (_array != None) else False)



#
# Return an individual result field from the previous query.
#
# Only use this function if exactly one field is being selected; otherwise,
# use db_fetch_object() or db_fetch_array().
#
# @param result
#   A database query result resource, as returned from db_query().
# @return
#   The resulting field or False.
#
def db_result(result):
  if (result and mysqli_num_rows(result) > 0):
    # The mysqli_fetch_row function has an optional second parameter row
    # but that can't be used for compatibility with Oracle, DB2, etc.
    _array = mysqli_fetch_row(result)
    return _array[0]
  return False




#
# Determine whether the previous query caused an error.
#
def db_error():
  global active_db
  return mysqli_errno(active_db)




#
# Determine the number of rows changed by the preceding query.
#
def db_affected_rows():
  global active_db # mysqli connection resource
  return mysqli_affected_rows(active_db)



#
# Runs a limited-range query in the active database.
#
# Use this as a substitute for db_query() when a subset of the query is to be
# returned.
# User-supplied arguments to the query should be passed in as separate parameters
# so that they can be properly escaped to avoid SQL injection attacks.
#
# @param query
#   A string containing an SQL query.
# @param ...
#   A variable number of arguments which are substituted into the query
#   using printf() syntax. The query arguments can be enclosed in one
#   array instead.
#   Valid %-modifiers are: %s, %d, %f, %b (binary data, do not enclose
#   in '') and %%.
#
#   NOTE: using this syntax will cast None and False values to decimal 0,
#   and True values to decimal 1.
#
# @param from
#   The first result row to return.
# @param count
#   The maximum number of result rows to return.
# @return
#   A database query result resource, or False if the query was not executed
#   correctly.
#
def db_query_range(query):
  args = func_get_args()
  count = array_pop(args)
  _from = array_pop(args)
  array_shift(args)
  query = db_prefix_tables(query)
  if (isset(args, 0) and is_array(args, 0)): # 'All arguments in one array' syntax
    args = args[0]
  _db_query_callback(args, True)
  query = preg_replace_callback(DB_QUERY_REGEXP, '_db_query_callback', query)
  query += ' LIMIT ' +  int(_from)  + ', ' . int(count)
  return _db_query(query)




#
# Runs a SELECT query and stores its results in a temporary table.
#
# Use this as a substitute for db_query() when the results need to stored
# in a temporary table. Temporary tables exist for the duration of the page
# request.
# User-supplied arguments to the query should be passed in as separate parameters
# so that they can be properly escaped to avoid SQL injection attacks.
#
# Note that if you need to know how many results were returned, you should do
# a SELECT COUNT(*) on the temporary table afterwards. db_affected_rows() does
# not give consistent result across different database types in this case.
#
# @param query
#   A string containing a normal SELECT SQL query.
# @param ...
#   A variable number of arguments which are substituted into the query
#   using printf() syntax. The query arguments can be enclosed in one
#   array instead.
#   Valid %-modifiers are: %s, %d, %f, %b (binary data, do not enclose
#   in '') and %%.
#
#   NOTE: using this syntax will cast None and False values to decimal 0,
#   and True values to decimal 1.
#
# @param table
#   The name of the temporary table to select into. This name will not be
#   prefixed as there is no risk of collision.
# @return
#   A database query result resource, or False if the query was not executed
#   correctly.
#
def db_query_temporary(query):
  args = func_get_args()
  tablename = array_pop(args)
  array_shift(args)
  query = preg_replace('/^SELECT/i', 'CREATE TEMPORARY TABLE ' +  tablename  + ' Engine=HEAP SELECT', db_prefix_tables(query))
  if (isset(args, 0) and is_array(args, 0)): # 'All arguments in one array' syntax
    args = args[0]
  _db_query_callback(args, True)
  query = preg_replace_callback(DB_QUERY_REGEXP, '_db_query_callback', query)
  return _db_query(query)



#
# Returns a properly formatted Binary Large Object value.
#
# @param data
#   Data to encode.
# @return
#  Encoded data.
#
def db_encode_blob(data):
  global active_db
  return "'" +  mysqli_real_escape_string(active_db, data)  + "'"



#
# Returns text from a Binary Large OBject value.
#
# @param data
#   Data to decode.
# @return
#  Decoded data.
#
def db_decode_blob(data):
  return data



#
# Prepare user input for use in a database query, preventing SQL injection attacks.
#
def db_escape_string(text):
  global active_db
  return mysqli_real_escape_string(active_db, text)



#
# Lock a table.
#
def db_lock_table(table):
  db_query('LOCK TABLES {' +  db_escape_table(table)  + '} WRITE')




#
# Unlock all locked tables.
#
def db_unlock_tables():
  db_query('UNLOCK TABLES')



#
# Check if a table exists.
#
def db_table_exists(table):
  return bool(db_fetch_object(db_query("SHOW TABLES LIKE '{" +  db_escape_table(table)  + "}'")))



#
# Check if a column exists in the given table.
#
def db_column_exists(table, column):
  return bool(db_fetch_object(db_query("SHOW COLUMNS FROM {" +  db_escape_table(table)  + "} LIKE '" + db_escape_table(column) + "'")))



#
# Wraps the given table.field entry with a DISTINCT(). The wrapper is added to
# the SELECT list entry of the given query and the resulting query is returned.
# This function only applies the wrapper if a DISTINCT doesn't already exist in
# the query.
#
# @param table Table containing the field to set as DISTINCT
# @param field Field to set as DISTINCT
# @param query Query to apply the wrapper to
# @return SQL query with the DISTINCT wrapper surrounding the given table.field.
#
def db_distinct_field(table, field, query):
  field_to_select = 'DISTINCT(' +  table  + '.' + field + ')'
  # (?<not text) is a negative look-behind (no need to rewrite queries that already use DISTINCT).
  return preg_replace('/(SELECT.*)(?:' +  table  + '\.|\s)(?<not DISTINCT\()(?<not DISTINCT\(' + table + '\.)' + field + '(.*FROM )/AUsi', '\1 ' + field_to_select + '\2', query)



#
# @} End of "ingroup database".
#

