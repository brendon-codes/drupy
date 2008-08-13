#!/usr/bin/env python
# Id: database.mysqli.inc,v 1.57 2008/04/14 17:48:33 dries Exp $

"""
  Database interface code for MySQL database servers using the mysqli client
  libraries. mysqli is included in PHP 5 by default and allows developers to
  use the advanced features of MySQL 4.1.x, 5.0.x and beyond.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note
    This file was ported from Drupal's includes/database_mysqli.inc and
    includes/database-mysql_common.inc
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-01-10
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

# Maintainers of this file should consult:
# http://www.php.net/manual/en/ref.mysqli.php

from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyMySQL
import bootstrap as lib_bootstrap
import database as lib_database

def status_report(phase):
  """
   Report database status.
  """
  t = get_t()
  version = db_version()
  form['mysql'] = {
    'title' : t('MySQL database'),
    'value' : (l(version, 'admin/reports/status/sql') if \
      (phase == 'runtime') else version),
  }
  if (version_compare(version, DRUPAL_MINIMUM_MYSQL) < 0):
    form['mysql']['severity'] = REQUIREMENT_ERROR
    form['mysql']['description'] = t(\
      'Your MySQL Server is too old + Drupal requires at least ' + \
      'MySQL %version.', {'%version' : DRUPAL_MINIMUM_MYSQL})
  return form



def version():
  """
   Returns the version of the database server currently in use.
  
   @return Database server version
  """
  global active_db
  version = php.explode('-', DrupyMySQL.mysqli_get_server_info(active_db))
  return version



def connect(url):
  """
   Initialise a database connection.
  
   Note that mysqli does not support persistent connections.
  """
  # Check if MySQLi support is present in PHP
  url = php.parse_url(url, 3306)
  # Decode url-encoded information in the db connection string
  url['user'] = php.urldecode(url['user'])
  # Test if database url has a password.
  url['pass'] = (php.urldecode(url['pass']) if php.isset(url, 'pass') else '')
  url['host'] = php.urldecode(url['host'])
  url['path'] = php.urldecode(url['path'])
  if (not php.isset(url, 'port')):
    url['port'] = None
  connection  = DrupyMySQL.mysqli_real_connect(\
    url['host'], url['user'], url['pass'], php.substr(url['path'], 1), \
    url['port'], '', DrupyMySQL.MYSQLI_CLIENT_FOUND_ROWS)
  if (DrupyMySQL.mysqli_connect_errno() > 0):
    _db_error_page(DrupyMySQL.mysqli_connect_error())
  # Force UTF-8.
  DrupyMySQL.mysqli_query(connection, 'SET NAMES "utf8"')
  # Require ANSI mode to improve SQL portability.
  DrupyMySQL.mysqli_query(connection, "SET php.SESSION sql_mode='ANSI'")
  return connection



def _query(query, debug = 0):
  """
   Helper function for db_query().
  """
  global active_db, queries, user
  if (lib_bootstrap.variable_get('dev_query', 0)):
    usec,sec = php.explode(' ', php.microtime())
    timer = float(usec) + float(sec)
    # If devel.plugin query logging is enabled, prepend a comment 
    # with the username and calling function
    # to the SQL string. This is useful when running mysql's 
    # SHOW PROCESSLIST to learn what exact
    # code is issueing the slow query.
    bt = debug_backtrace()
    # t() may not be available yet so we don't wrap 'Anonymous'
    name = (user.name if (user.uid > 0) else \
      variable_get('anonymous', 'Anonymous'))
    # php.str_replace() to prevent SQL injection via username
    # or anonymous name.
    name = php.str_replace(['*', '/'], '', name)
    query = '/* ' +  name  + ' : ' . bt[2]['function'] + ' */ ' + query
  result = DrupyMySQL.mysqli_query(lib_database.active_db, query)
  if (lib_bootstrap.variable_get('dev_query', 0)):
    query = bt[2]['function'] +  "\n"  + query
    usec,sec = php.explode(' ', php.microtime())
    stop = float(usec) + float(sec)
    diff = stop - timer
    queries.append( [query, diff] )
  if (debug):
    print '<p>query: ' +  query  + '<br />error:' + \
      DrupyMySQL.mysqli_error(active_db) + '</p>'
  if (not DrupyMySQL.mysqli_errno(lib_database.active_db)):
    return result
  else:
    # Indicate to drupal_error_handler that this is a database error.
    DB_ERROR = True
    php.trigger_error(lib_bootstrap.check_plain(\
      DrupyMySQL.mysqli_error(lib_database.active_db) +  \
      "\nquery: "  + query), php.E_USER_WARNING)
    return False



def fetch_object(result):
  """
   Fetch one result row from the previous query as an object.
  
   @param result
     A database query result resource, as returned from db_query().
   @return
     An object representing the next row of the result,
     or False. The attributes
     of this object are the table fields selected by the query.
  """
  if (result):
    object_ = DrupyMySQL.mysqli_fetch_object(result)
    return (object_ if (object_ != None) else False)




def fetch_array(result):
  """
   Fetch one result row from the previous query as an array.
  
   @param result
     A database query result resource, as returned from db_query().
   @return
     An associative array representing the next row of the result, or False.
     The keys of this object are the names of the table fields selected by the
     query, and the values are the field values for this result row.
  """
  if (result):
    array_ = DrupyMySQL.mysqli_fetch_array(result, DrupyMySQL.MYSQLI_ASSOC)
    return (array_ if (array_ != None) else False)



def result(result):
  """
   Return an individual result field from the previous query.
  
   Only use this function if exactly one field is being selected; otherwise,
   use db_fetch_object() or db_fetch_array().
  
   @param result
     A database query result resource, as returned from db_query().
   @return
     The resulting field or False.
  """
  if (result and DrupyMySQL.mysqli_num_rows(result) > 0):
    # The DrupyMySQL.mysqli_fetch_row function has an optional second
    # parameter row
    # but that can't be used for compatibility with Oracle, DB2, etc.
    array_ = DrupyMySQL.mysqli_fetch_row(result)
    return array_[0]
  return False



def error():
  """
   Determine whether the previous query caused an error.
  """
  return DrupyMySQL.mysqli_errno(lib_database.active_db)




def affected_rows():
  """
   Determine the number of rows changed by the preceding query.
  """
  return DrupyMySQL.mysqli_affected_rows(lib_database.active_db)



def query_range(query):
  """
   Runs a limited-range query in the active database.
  
   Use this as a substitute for db_query() when a subset of the query is to be
   returned. User-supplied arguments to the query should be passed in as
   separate parameters so that they can be properly escaped to avoid SQL
   injection attacks.
  
   @param query
     A string containing an SQL query.
   @param ...
     A variable number of arguments which are substituted into the query
     using printf() syntax. The query arguments can be enclosed in one
     array instead.
     Valid %-modifiers are: %s, %d, %f, %b (binary data, do not enclose
     in '') and %%.
     NOTE: using this syntax will cast None and False values to decimal 0,
     and True values to decimal 1.
   @param from
     The first result row to return.
   @param count
     The maximum number of result rows to return.
   @return
     A database query result resource, or False if the query was not executed
     correctly.
  """
  args = func_get_args()
  count = php.array_pop(args)
  from_ = php.array_pop(args)
  php.array_shift(args)
  query = db_prefix_tables(query)
  # 'All arguments in one array' syntax
  if (php.isset(args, 0) and php.is_array(args, 0)): 
    args = args[0]
  _db_query_callback(args, True)
  query = php.preg_replace_callback(DB_QUERY_REGEXP, \
    '_db_query_callback', query)
  query += ' LIMIT ' +  int(from_)  + ', ' . int(count)
  return _db_query(query)




def query_temporary(query):
  """
   Runs a SELECT query and stores its results in a temporary table.
  
   Use this as a substitute for db_query() when the results need to stored
   in a temporary table. Temporary tables exist for the duration of the page
   request.
   User-supplied arguments to the query should be passed in as
   separate parameters
   so that they can be properly escaped to avoid SQL injection attacks.
  
   Note that if you need to know how many results were returned, you should do
   a SELECT COUNT(*) on the temporary table afterwards. db_affected_rows() does
   not give consistent result across different database types in this case.
  
   @param query
     A string containing a normal SELECT SQL query.
   @param ...
     A variable number of arguments which are substituted into the query
     using printf() syntax. The query arguments can be enclosed in one
     array instead.
     Valid %-modifiers are: %s, %d, %f, %b (binary data, do not enclose
     in '') and %%.
  
     NOTE: using this syntax will cast None and False values to decimal 0,
     and True values to decimal 1.
  
   @param table
     The name of the temporary table to select into. This name will not be
     prefixed as there is no risk of collision.
   @return
     A database query result resource, or False if the query was not executed
     correctly.
  """
  args = func_get_args()
  tablename = php.array_pop(args)
  php.array_shift(args)
  query = php.preg_replace('/^SELECT/i', 'CREATE TEMPORARY TABLE ' +  \
    tablename  + ' Engine=HEAP SELECT', db_prefix_tables(query))
  # 'All arguments in one array' syntax
  if (php.isset(args, 0) and php.is_array(args, 0)): 
    args = args[0]
  _db_query_callback(args, True)
  query = php.preg_replace_callback(DB_QUERY_REGEXP, \
    '_db_query_callback', query)
  return _db_query(query)



def encode_blob(data):
  """
   Returns a properly formatted Binary Large Object value.
  
   @param data
     Data to encode.
   @return
    Encoded data.
  """
  return "'" +  DrupyMySQL.mysqli_real_escape_string(lib_database.active_db, \
    data)  + "'"



def decode_blob(data):
  """
   Returns text from a Binary Large OBject value.
  
   @param data
     Data to decode.
   @return
    Decoded data.
  """
  return data


def escape_string(text):
  """
   Prepare user input for use in a database query, preventing
   SQL injection attacks.
  """
  return DrupyMySQL.mysqli_real_escape_string(lib_database.active_db, text)



def lock_table(table):
  """
   Lock a table.
  """
  db_query('LOCK TABLES {' +  db_escape_table(table)  + '} WRITE')




def unlock_tables():
  """
   Unlock all locked tables.
  """
  db_query('UNLOCK TABLES')


def table_exists(table):
  """
   Check if a table exists.
  """
  return bool(lib_database.fetch_object(\
    lib_database.query("SHOW TABLES LIKE '{" +  \
    lib_database.escape_table(table)  + "}'")))


def column_exists(table, column):
  """
   Check if a column exists in the given table.
  """
  return bool(lib_database.fetch_object(\
    lib_database.query("SHOW COLUMNS FROM {" + \
    lib_database.escape_table(table)  + "} LIKE '" + \
    lib_database.escape_table(column) + "'")))


def distinct_field(table, field, query):
  """
   Wraps the given table.field entry with a DISTINCT(). The wrapper is added to
   the SELECT list entry of the given query and the resulting query is
   returned. This function only applies the wrapper if a DISTINCT doesn't
   already exist in the query.
  
   @param table Table containing the field to set as DISTINCT
   @param field Field to set as DISTINCT
   @param query Query to apply the wrapper to
   @return SQL query with the DISTINCT wrapper surrounding the given
   table.field.
  """
  field_to_select = 'DISTINCT(' +  table  + '.' + field + ')'
  # (?<not text) is a negative look-behind
  # (no need to rewrite queries that already use DISTINCT).
  return php.preg_replace('/(SELECT.*)(?:' +  table  + \
    '\.|\s)(?<not DISTINCT\()(?<not DISTINCT\(' + table + '\.)' + field + \
    '(.*FROM )/AUsi', '\1 ' + field_to_select + '\2', query)



#
# @} End of "ingroup database".
#

#
# These functions were originally located in includes/mysql-common.inc
#


def query(query_, *args):
  """
   Runs a basic query in the active database.
  
   User-supplied arguments to the query should be passed in as separate
   parameters so that they can be properly escaped to avoid SQL injection
   attacks.
  
   @param query
     A string containing an SQL query.
   @param ...
     A variable number of arguments which are substituted into the query
     using printf() syntax. Instead of a variable number of query arguments,
     you may also pass a single array containing the query arguments.
  
     Valid %-modifiers are: %s, %d, %f, %b (binary data, do not enclose
     in '') and %%.
  
     NOTE: using this syntax will cast None and False values to decimal 0,
    and True values to decimal 1.
  
   @return
     A database query result resource, or False if the query was not
     executed correctly.
  """
  this_query = lib_database.prefix_tables(query_)
  # 'All arguments in one array' syntax
  if (php.isset(args, 0) and php.is_array(args[0])): 
    args = args[0]
  lib_database._query_callback(args, True)
  this_query = php.preg_replace_callback(lib_database.DB_QUERY_REGEXP, \
    lib_database._query_callback, this_query)
  #print
  #print "QUERY DEBUG:"
  #print this_query
  #print
  return _query(this_query)


#
# @ingroup schemaapi
# @{
#

def create_table_sql(name, table):
  """
   Generate SQL to create a new table from a Drupal schema definition.
  
   @param name
     The name of the table to create.
   @param table
     A Schema API table definition array.
   @return
     An array of SQL statements to create the table.
  """
  if (php.empty(table['mysql_suffix'])):
    table['mysql_suffix'] = "/*not 40100 DEFAULT CHARACTER SET UTF8 */"
  sql = "CREATE TABLE {" +  name  + "} (\n"
  # Add the SQL statement for each field.
  for field_name,field in table['fields'].items():
    sql += _db_create_field_sql(field_name, _db_process_field(field)) +  ", \n"
  # Process keys & indexes.
  keys = _db_create_keys_sql(table)
  if (php.count(keys)):
    sql += php.implode(", \n", keys) +  ", \n"
  # Remove the last comma and space.
  sql = php.substr(sql, 0, -3) +  "\n) "
  sql += table['mysql_suffix']
  return array(sql)



def _create_keys_sql(spec):
  keys = {}
  if (not php.empty(spec['primary key'])):
    keys.append( 'PRIMARY KEY (' +  \
      _db_create_key_sql(spec['primary key'])  + ')' )
  if (not php.empty(spec['unique keys'])):
    for key,fields in spec['unique keys'].items():
      keys.append( 'UNIQUE KEY ' +  key  + \
        ' (' + _db_create_key_sql(fields) + ')' )
  if (not php.empty(spec['indexes'])):
    for index,fields in spec['indexes'].items():
      keys.append( 'INDEX ' +  index  + ' (' + \
        _db_create_key_sql(fields) + ')' )
  return keys




def _create_key_sql(fields):
  ret = []
  for field in fields:
    if (php.is_array(field)):
      ret.append( field[0] +  '('  + field[1] + ')' )
    else:
      ret.append( field )
  return php.implode(', ', ret)


def _process_field(field):
  """
   Set database-engine specific properties for a field.
  
   @param field
     A field description array, as specified in the schema documentation.
  """
  if (not php.isset(field, 'size')):
    field['size'] = 'normal'
  # Set the correct database-engine specific datatype.
  if (not php.isset(field, 'mysql_type')):
    map_ = db_type_map()
    field['mysql_type'] = map_[field['type'] +  ':'  + field['size']]
  if (field['type'] == 'serial'):
    field['auto_increment'] = True
  return field



def _create_field_sql(name, spec):
  """
   Create an SQL string for a field to be used in table creation or alteration.
  
   Before passing a field out of a schema definition into this function it has
   to be processed by _db_process_field().
  
   @param name
      Name of the field.
   @param spec
      The field specification, as per the schema data structure format.
  """
  sql = "`" +  name  + "` " . spec['mysql_type']
  if (php.isset(spec, 'length')):
    sql += '(' +  spec['length']  + ')'
  elif (php.isset(spec, 'precision') and php.isset(spec, 'scale')):
    sql += '(' +  spec['precision']  + ', ' + spec['scale'] + ')'
  if (not php.empty(spec['unsigned'])):
    sql += ' unsigned'
  if (not php.empty(spec['not None'])):
    sql += ' NOT None'
  if (not php.empty(spec['auto_increment'])):
    sql += ' auto_increment'
  if (php.isset(spec, 'default')):
    if (is_string(spec['default'])):
      spec['default'] = "'" +  spec['default']  + "'"
    sql += ' DEFAULT ' +  spec['default']
  if (php.empty(spec['not None']) and not php.isset(spec, 'default')):
    sql += ' DEFAULT None'
  return sql





def type_map():
  """
   This maps a generic data type in combination with its data size
   to the engine-specific data type.
  """
  # Put :normal last so it gets preserved by array_flip.  This makes
  # it much easier for plugins (such as schema.plugin) to map
  # database types back into schema types.
  map_ = {
    'varchar:normal'  : 'VARCHAR',
    'char:normal'     : 'CHAR',
    'text:tiny'       : 'TINYTEXT',
    'text:small'      : 'TINYTEXT',
    'text:medium'     : 'MEDIUMTEXT',
    'text:big'        : 'LONGTEXT',
    'text:normal'     : 'TEXT',
    'serial:tiny'     : 'TINYINT',
    'serial:small'    : 'SMALLINT',
    'serial:medium'   : 'MEDIUMINT',
    'serial:big'      : 'BIGINT',
    'serial:normal'   : 'INT',
    'int:tiny'        : 'TINYINT',
    'int:small'       : 'SMALLINT',
    'int:medium'      : 'MEDIUMINT',
    'int:big'         : 'BIGINT',
    'int:normal'      : 'INT',
    'float:tiny'      : 'FLOAT',
    'float:small'     : 'FLOAT',
    'float:medium'    : 'FLOAT',
    'float:big'       : 'DOUBLE',
    'float:normal'    : 'FLOAT',
    'numeric:normal'  : 'DECIMAL',
    'blob:big'        : 'LONGBLOB',
    'blob:normal'     : 'BLOB',
    'datetime:normal' : 'DATETIME'
  }
  return map_



def rename_table(ret, table, new_name):
  """
   Rename a table.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be renamed.
   @param new_name
     The new name for the table.
  """
  php.Reference.check(ref)
  ret.append( update_sql('ALTER TABLE {' +  table  + '} RENAME TO {' + \
    new_name + '}') )



def drop_table(ret, table):
  """
   Drop a table.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be dropped.
  """
  php.Reference.check(ref)
  php.array_merge( update_sql('DROP TABLE {' +  table  + '}'), ret, True )



def add_field(ret, table, field, spec, keys_new = []):
  """
   Add a new field to a table.
  
   @param ret
     Array to which query results will be added.
   @param table
     Name of the table to be altered.
   @param field
     Name of the field to be added.
   @param spec
     The field specification array, as taken from a schema definition.
     The specification may also contain the key 'initial', the newly
     created field will be set to the value of the key in all rows.
     This is most useful for creating NOT None columns with no default
     value in existing tables.
   @param keys_new
     Optional keys and indexes specification to be created on the
     table along with adding the field. The format is the same as a
     table specification but without the 'fields' element.  If you are
     adding a type 'serial' field, you MUST specify at least one key
     or index including it in this array. @see db_change_field for more
     explanation why.
  """
  php.Reference.check(ret)
  fixNone = False
  if (not php.empty(spec['not None']) and not php.isset(spec, 'default')):
    fixNone = True
    spec['not None'] = False
  query = 'ALTER TABLE {' +  table  + '} ADD '
  query += _db_create_field_sql(field, _db_process_field(spec))
  if (php.count(keys_new)):
    query += ', ADD ' +  php.implode(', ADD ', _db_create_keys_sql(keys_new))
  ret.append( update_sql(query) )
  if (php.isset(spec, 'initial')):
    # All this because update_sql does not support %-placeholders.
    sql = 'UPDATE {' +  table  + '} SET ' + field + ' = ' + \
      db_type_placeholder(spec['type'])
    result = db_query(sql, spec['initial'])
    ret.append( {'success' : result != False, \
      'query' : check_plain(sql +  ' ('  + spec['initial'] + ')')})
  if (fixNone):
    spec['not None'] = True
    db_change_field(ret, table, field, field, spec)



def drop_field(ret, table, field):
  """
   Drop a field.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param field
     The field to be dropped.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + '} DROP ' + field) )


def field_set_default(ret, table, field, default):
  """
   Set the default value for a field.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param field
     The field to be altered.
   @param default
     Default value to be set. None for 'default None'.
  """
  php.Reference.check(ret)
  if (default == None):
    default = 'None'
  else:
    default = ("'default'" if is_string(default) else default)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} ALTER COLUMN ' + field + ' SET DEFAULT ' + default) )



def field_set_no_default(ret, table, field):
  """
   Set a field to have no default value.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param field
     The field to be altered.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} ALTER COLUMN ' + field + ' DROP DEFAULT') )




def add_primary_key(ret, table, fields):
  """
   Add a primary key.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param fields
     Fields for the primary key.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} ADD PRIMARY KEY (' + _db_create_key_sql(fields) +  ')') )



def drop_primary_key(ret, table):
  """
   Drop the primary key.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} DROP PRIMARY KEY') )



def add_unique_key(ret, table, name, fields):
  """
   Add a unique key.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param name
     The name of the key.
   @param fields
     An array of field names.
  """
  php.Reference.check(ret)
  ret.val.append( update_sql('ALTER TABLE {' +  table  + \
    '} ADD UNIQUE KEY ' + name +  ' ('  + _db_create_key_sql(fields) + ')') )



def drop_unique_key(ret, table, name):
  """
   Drop a unique key.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param name
     The name of the key.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} DROP KEY ' + name) )



def add_index(ret, table, name, fields):
  """
   Add an index.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param name
     The name of the index.
   @param fields
     An array of field names.
  """
  php.Reference.check(ret)
  query = 'ALTER TABLE {' +  table  + '} ADD INDEX ' + name + \
    ' (' + _db_create_key_sql(fields) + ')'
  ret.append( update_sql(query) )



def drop_index(ret, table, name):
  """
   Drop an index.
  
   @param ret
     Array to which query results will be added.
   @param table
     The table to be altered.
   @param name
     The name of the index.
  """
  php.Reference.check(ret)
  ret.append( update_sql('ALTER TABLE {' +  table  + \
    '} DROP INDEX ' + name) )



def change_field(ret, table, field, field_new, spec, keys_new = []):
  """
   Change a field definition.
  
   IMPORTANT NOTE: To maintain database portability, you have to explicitly
   recreate all indices and primary keys that are using the changed field.
  
   That means that you have to drop all affected keys and indexes with
   db_drop_{primary_key,unique_key,index}() before calling db_change_field().
   To recreate the keys and indices, pass the key definitions as the
   optional keys_new argument directly to db_change_field().
  
   For example, suppose you have:
   @code
   schema['foo'] = array(
     'fields' : array(
       'bar' : array('type' : 'int', 'not None' : True)
     ),
     'primary key' : array('bar')
   )
   @endcode
   and you want to change foo.bar to be type serial, leaving it as the
   primary key.  The correct sequence is:
   @code
   db_drop_primary_key(ret, 'foo')
   db_change_field(ret, 'foo', 'bar', 'bar',
     array('type' : 'serial', 'not None' : True),
     array('primary key' : array('bar')))
   @endcode
  
   The reasons for this are due to the different database engines:
  
   On PostgreSQL, changing a field definition involves adding a new field
   and dropping an old one which* causes any indices, primary keys and
   sequences (from serial-type fields) that use the changed field to be
   dropped.
  
   On MySQL, all type 'serial' fields must be part of at least one key
   or index as soon as they are created.  You cannot use
   db_add_{primary_key,unique_key,index}() for this purpose because
   the ALTER TABLE command will fail to add the column without a key
   or index specification.  The solution is to use the optional
   keys_new argument to create the key or index at the same time as
   field.
  
   You could use db_add_{primary_key,unique_key,index}() in all cases
   unless you are converting a field to be type serial. You can use
   the keys_new argument in all cases.
  
   @param ret
     Array to which query results will be added.
   @param table
     Name of the table.
   @param field
     Name of the field to change.
   @param field_new
     New name for the field (set to the same as field if you don't want to
     change the name).
   @param spec
     The field specification for the new field.
   @param keys_new
     Optional keys and indexes specification to be created on the
     table along with changing the field. The format is the same as a
     table specification but without the 'fields' element.
  """
  php.Reference.check(ret)
  sql = 'ALTER TABLE {' +  table  + '} CHANGE ' + field + ' ' + \
    _db_create_field_sql(field_new, _db_process_field(spec))
  if (php.count(keys_new) > 0):
    sql += ', ADD ' +  php.implode(', ADD ', _db_create_keys_sql(keys_new))
  ret.append( update_sql(sql) )


def last_insert_id(table, field):
  """
   Returns the last insert id.
  
   @param table
     The name of the table you inserted into.
   @param field
     The name of the autoincrement field.
  """
  return db_result(db_query('SELECT LAST_INSERT_ID()'))



def escape_string(data):
  """
   Wrapper to escape a string
  """
  return DrupyMySQL.mysqli_real_escape_string(lib_database.active_db, data)



#
# Aliases
#
fetch_assoc = fetch_array

