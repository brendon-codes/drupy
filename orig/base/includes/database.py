#!/usr/bin/env python
# $Id: database.inc,v 1.96 2008/07/19 12:31:14 dries Exp $

"""
  Wrapper for database interface code.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/database.inc
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

#
# Includes
#
from lib.drupy import DrupyPHP as php
from sites.default import settings
import appglobals as lib_appglobals
import bootstrap as lib_bootstrap
import database_mysqli as db


#
# A hash value to check when outputting database errors, php.md5('DB_ERROR').
#
# @see drupal_error_handler()
#
DB_ERROR = 'a515ac9c2796ca0e23adbe92c68fc9fc'
DB_QUERY_REGEXP = '/(%d|%s|%%|%f|%b|%n)/';


#
# @defgroup database Database abstraction layer
# @{

def update_sql(sql):
  """
   Allow the use of different database servers using the same code base.
  
   Drupal provides a slim database abstraction layer to provide developers with
   the ability to support multiple database servers easily. The intent of this
   layer is to preserve the syntax and power of SQL as much as possible, while
   letting Drupal control the pieces of queries that need to be written
   differently for different servers and provide basic security checks.
  
   Most Drupal database queries are performed by a call to db_query() or
   db_query_range(). Module authors should also consider using
   pager_query() for
   queries that return results that need to be presented on multiple pages, and
   tablesort_sql() for generating appropriate queries for sortable tables.
  
   For example, one might wish to return a list of the most recent 10 nodes
   authored by a given user. Instead of directly issuing the SQL query
   @code
     SELECT n.title, n.body, n.created FROM node n WHERE n.uid = uid \
       LIMIT 0, 10;
   @endcode
   one would instead call the Drupal functions:
   @code
     result = db_query_range('SELECT n.title, n.body, n.created
       FROM {node} n WHERE n.uid = %d', uid, 0, 10);
     while (node = db_fetch_object(result)) {
       // Perform operations on node->body, etc. here.
     }
   @endcode
   Curly braces are used around "node" to provide table prefixing via
   db_prefix_tables(). The explicit use of a user ID is pulled out into an
   argument passed to db_query() so that SQL injection attacks from user input
   can be caught and nullified. The LIMIT syntax varies between database
   servers,
   so that is abstracted into db_query_range() arguments. Finally, note the
   common pattern of iterating over the result set using db_fetch_object().
  
   Perform an SQL query and return success or failure.
  
   @param sql
     A string containing a complete SQL query.  %-substitution
     parameters are not supported.
   @return
     An array containing the keys:
        success: a boolean indicating whether the query succeeded
        query: the SQL query executed, passed through check_plain()
  """
  result = db_query(sql, true);
  return {'success' : (result != False), 'query' : check_plain(sql)};



def prefix_tables(sql):
  """
   Append a database prefix to all tables in a query.
  
   Queries sent to Drupal should wrap all table names in curly brackets. This
   function searches for this syntax and adds Drupal's table prefix to all
   tables, allowing Drupal to coexist with other systems in the same
   database if necessary.
  
   @param sql
     A string containing a partial or entire SQL query.
   @return
     The properly-prefixed string.
  """
  if (php.is_array(settings.db_prefix)):
    if (php.array_key_exists('default', settings.db_prefix)):
      tmp = settings.db_prefix;
      del(tmp['default']);
      for key,val in tmp.items():
        sql = php.strtr(sql, {('{' + key + '}') : (val + key)});
      return php.strtr(sql, {'{' : settings.db_prefix['default'], '}' : ''});
    else:
      for key,val in settings.db_prefix.items():
        sql = php.strtr(sql, {('{' + key + '}') : (val + key)});
      return php.strtr(sql, {'{' : '', '}' : ''});
  else:
    return php.strtr(sql, {'{' : settings.db_prefix, '}' : ''});


def set_active(name = 'default'):
  """
   Activate a database for future queries.
  
   If it is necessary to use external databases in a project, this function can
   be used to change where database queries are sent. If the database has not
   yet been used, it is initialized using the URL specified for that name in
   Drupal's configuration file. If this name is not defined, a duplicate of the
   default connection is made instead.
  
   Be sure to change the connection back to the default when done with custom
   code.
  
   @param name
     The name assigned to the newly active database connection. If omitted, the
     default connection will be made active.
  
   @return the name of the previously active database or FALSE if non was
   found.
  
   @todo BC: Need to eventually resolve the database importing mechanism here
   right now we are statically loading mysql at the top, but eventually we need
   to get this figured out 
  """
  php.static(set_active, 'db_conns', {})
  php.static(set_active, 'active_name', False)
  if (settings.db_url == None):
    install_goto('install.py');
  if (not php.isset(set_active.db_conns, name)):
    # Initiate a new connection, using the named DB URL specified.
    if (isinstance(settings.db_url, dict)):
      connect_url = (settings.db_url[name] if \
        php.array_key_exists(name, settings.db_url) else \
        settings.db_url['default']);
    else:
      connect_url = settings.db_url;
    lib_appglobals.db_type = \
      php.substr(connect_url, 0, php.strpos(connect_url, '://'));
    #handler = "includes/database_%(db_type)s.py" % {'db_type' : db_type};
    #try:
    #  import db file here
    #except ImportError:
    #  _db_error_page("The database type '" + db_type + \
    #    "' is unsupported. Please use either 'mysql' or " + \
    #    "'mysqli' for MySQL, or 'pgsql' for PostgreSQL databases.");
    set_active.db_conns[name] = db.connect(connect_url);
    # We need to pass around the simpletest database prefix in the request
    # and we put that in the user_agent php.header.
    if (php.preg_match("/^simpletest\d+$/", php.SERVER['HTTP_USER_AGENT'])):
      settings.db_prefix = php.SERVER['HTTP_USER_AGENT'];
  previous_name = set_active.active_name;
  # Set the active connection.
  set_active.active_name = name;
  lib_appglobals.active_db = set_active.db_conns[name];
  return previous_name;



def _error_page(error = ''):
  """
   Helper function to show fatal database errors.
  
   Prints a themed maintenance page with the 'Site off-line' text,
   adding the provided error message in the case of 'display_errors'
   set to on. Ends the page request; no return.
  
   @param error
     The error message to be appended if 'display_errors' is on.
  """
  lib_bootstrap.drupal_maintenance_theme();
  drupal_set_header('HTTP/1.1 503 Service Unavailable');
  drupal_set_title('Site off-line');
  message = '<p>The site is currently not available due to technical ' + \
    'problems. Please try again later. Thank you for your understanding.</p>';
  message += '<hr /><p><small>If you are the maintainer of this site, ' + \
    'please check your database settings in the ' + \
    '<code>settings.php</code> file and ensure that your hosting ' + \
    'provider\'s database server is running. For more help, ' + \
    'see the <a href="http://drupal.org/node/258">handbook</a>, or ' + \
    'contact your hosting provider.</small></p>';
  if (error and ini_get('display_errors')):
    message += '<p><small>The ' + theme('placeholder', \
      lib_appglobals.db_type) + \
      ' error was: ' + theme('placeholder', error) + '.</small></p>';
  print theme('maintenance_page', message);
  exit();


def is_active():
  """
   Returns a boolean depending on the availability of the database.
  """
  return (lib_appglobals.active_db is not None);


def _query_callback(match, init = False):
  """
   Helper function for db_query().
  """
  php.static(_query_callback, 'args')
  if (init):
    _query_callback.args = list(match);
    return;
  # We must use type casting to int to convert FALSE/NULL/(TRUE?)
  if match[1] == '%d': 
    # We don't need db_escape_string as numbers are db-safe
    return str(int(php.array_shift(_query_callback.args))); 
  elif match[1] == '%s':
    return db.escape_string(php.array_shift(_query_callback.args));
  elif match[1] == '%n':
    # Numeric values have arbitrary precision, so can't be treated as float.
    # is_numeric() allows hex values (0xFF), but they are not valid.
    value = php.trim(php.array_shift(args));
    return  (value if (php.is_numeric(value) and not \
      php.stripos(value, 'x')) else '0')
  elif match[1] == '%%':
    return '%';
  elif match[1] == '%f':
    return float(php.array_shift(_query_callback.args));
  elif match[1] == '%b': # binary data
    return db.encode_blob(php.array_shift(_query_callback.args));


def placeholders(arguments, type = 'int'):
  """
   Generate placeholders for an array of query arguments of a single type.
  
   Given a Schema API field type, return correct %-placeholders to
   embed in a query
  
   @param arguments
    An array with at least one element.
   @param type
     The Schema API type of a field (e.g. 'int', 'text', or 'varchar').
  """
  placeholder = db_type_placeholder(type);
  return php.implode(',', php.array_fill(0, php.count(arguments), \
    placeholder));



#
# Helper function for db_rewrite_sql.
#
# Collects JOIN and WHERE statements via hook_db_rewrite_sql()
# Decides whether to select primary_key or DISTINCT(primary_key)
#
# @param query
#   Query to be rewritten.
# @param primary_table
#   Name or alias of the table which has the primary key field for this query.
#   Typical table names would be: {blocks}, {comments}, {forum}, {node},
#   {menu}, {term_data} or {vocabulary}. However, in most cases the usual
#   table alias (b, c, f, n, m, t or v) is used instead of the table name.
# @param primary_field
#   Name of the primary field.
# @param args
#   Array of additional arguments.
# @return
#   An array: join statements, where statements, field or DISTINCT(field).
#
def _rewrite_sql(query = '', primary_table = 'n', primary_field = 'nid', \
    args = []):
  where = []
  join_ = []
  distinct = False
  for plugin in lib_plugin.implements('db_rewrite_sql'):
    result = lib_plugin.invoke(plugin, 'db_rewrite_sql', query, \
      primary_table, primary_field, args)
    if (php.isset(result) and php.is_array(result)):
      if (php.isset(result['where'])):
        where.append( result['where'] )
      if (php.isset(result['join'])):
        join_.append( result['join'] )
      if (php.isset(result['distinct']) and result['distinct']):
        distinct = True
    elif (php.isset(result)):
      where.append( result )
  where = ('' if php.empty(where) else \
    ('(' +  php.implode(') AND (', where)  + ')') )
  join_ = ('' if php.empty(join) else php.implode(' ', join))
  return (join, where, distinct)



#
# Rewrites node, taxonomy and comment queries. Use it for
# listing queries. Do not
# use FROM table1, table2 syntax, use JOIN instead.
#
# @param query
#   Query to be rewritten.
# @param primary_table
#   Name or alias of the table which has the primary key field for this query.
#   Typical table names would be: {blocks}, {comments}, {forum}, {node},
#   {menu}, {term_data} or {vocabulary}. However, it is more common to use the
#   the usual table aliases: b, c, f, n, m, t or v.
# @param primary_field
#   Name of the primary field.
# @param args
#   An array of arguments, passed to the implementations
#   of hook_db_rewrite_sql.
# @return
#   The original query with JOIN and WHERE statements inserted from
#   hook_db_rewrite_sql implementations. nid is rewritten if needed.
#
def rewrite_sql(query, primary_table = 'n', primary_field = 'nid',  args = []):
  join_, where, distinct = _rewrite_sql(query, primary_table, \
    primary_field, args)
  if (distinct):
    query = distinct_field(primary_table, primary_field, query)
  if (not php.empty(where) or not php.empty(join_)):
    pattern = \
      '{ ' + \
      '  # Beginning of the string ' + \
      '  ^ ' + \
      '  ((?P<anonymous_view> ' + \
      '    # Everything within this set of parentheses ' + \
      '    # is named "anonymous view ' + \
      '    (?: ' + \
      '      # anything not parentheses ' + \
      '      [^()]++ ' + \
      '      | ' + \
      '      # an open parenthesis, more anonymous view and ' + \
      '      # finally a close parenthesis. ' + \
      '      \( (?P>anonymous_view) \) ' + \
      '    )* ' + \
      '  )[^()]+WHERE) ' + \
      '}X'
    matches = []
    php.preg_match(pattern, query, matches)
    if (where):
      n = php.strlen(matches[1])
      second_part = php.substr(query, n)
      first_part = php.substr(matches[1], 0, n - 5) + \
        " join WHERE where AND ( "
      # PHP 4 does not support strrpos for strings. We emulate it.
      haystack_reverse = php.strrev(second_part)
      # No need to use strrev on the needle, we supply GROUP, ORDER, LIMIT
      # reversed.
      for needle_reverse in ('PUORG', 'REDRO', 'TIMIL'):
        pos = php.strpos(haystack_reverse, needle_reverse)
        if (pos != False):
          # All needles are five characters long.
          pos += 5
          break
      if (pos == False):
        query = first_part +  second_part  + ')'
      else:
        query = first_part +  substr(second_part, 0, -pos)  + ')' + \
          php.substr(second_part, -pos)
    else:
      query = matches[1] +  " join "  + \
        php.substr(query, php.strlen(matches[1]))
  return query



#
# Restrict a dynamic table, column or constraint name to safe characters.
#
# Only keeps alphanumeric and underscores.
#
def escape_table(string_):
  return php.preg_replace('/[^A-Za-z0-9_]+/', '', string_)


#
# A Drupal schema definition is an array structure representing one or
# more tables and their related keys and indexes. A schema is defined by
# hook_schema(), which usually lives in a modulename.install file.
#
# By implementing hook_schema() and specifying the tables your module
# declares, you can easily create and drop these tables on all
# supported database engines. You don't have to deal with the
# different SQL dialects for table creation and alteration of the
# supported database engines.
#
# hook_schema() should return an array with a key for each table that
# the module defines.
#
# The following keys are defined:
#
#   - 'description': A string describing this table and its purpose.
#     References to other tables should be enclosed in
#     curly-brackets.  For example, the node_revisions table
#     description field might contain "Stores per-revision title and
#     body data for each {node}."
#   - 'fields': An associative array ('fieldname' : specification)
#     that describes the table's database columns.  The specification
#     is also an array.  The following specification parameters are defined:
#
#     - 'description': A string describing this field and its purpose.
#       References to other tables should be enclosed in
#       curly-brackets.  For example, the node table vid field
#       description might contain "Always holds the largest (most
#       recent):node_revisions}.vid value for this nid."
#     - 'type': The generic datatype: 'varchar', 'int', 'serial'
#       'float', 'numeric', 'text', 'blob' or 'datetime'.  Most types
#       just map to the according database engine specific
#       datatypes.  Use 'serial' for auto incrementing fields. This
#       will expand to 'int auto_increment' on mysql.
#     - 'size': The data size: 'tiny', 'small', 'medium', 'normal',
#       'big'.  This is a hint about the largest value the field will
#       store and determines which of the database engine specific
#       datatypes will be used (e.g. on MySQL, TINYINT vs. INT vs. BIGINT).
#       'normal', the default, selects the base type (e.g. on MySQL,
#       INT, VARCHAR, BLOB, etc.).
#
#       Not all sizes are available for all data types. See
#       db_type_map() for possible combinations.
#     - 'not None': If True, no None values will be allowed in this
#       database column.  Defaults to False.
#     - 'default': The field's default value.  The PHP type of the
#       value matters: '', '0', and 0 are all different.  If you
#       specify '0' as the default value for a type 'int' field it
#       will not work because '0' is a string containing the
#       character "zero", not an integer.
#     - 'length': The maximal length of a type 'varchar' or 'text'
#       field.  Ignored for other field types.
#     - 'unsigned': A boolean indicating whether a type 'int', 'float'
#       and 'numeric' only is signed or unsigned.  Defaults to
#       False.  Ignored for other field types.
#     - 'precision', 'scale': For type 'numeric' fields, indicates
#       the precision (total number of significant digits) and scale
#       (decimal digits right of the decimal point).  Both values are
#       mandatory.  Ignored for other field types.
#
#     All parameters apart from 'type' are optional except that type
#     'numeric' columns must specify 'precision' and 'scale'.
#
#  - 'primary key': An array of one or more key column specifiers (see below)
#    that form the primary key.
#  - 'unique key': An associative array of unique keys ('keyname' :
#    specification).  Each specification is an array of one or more
#    key column specifiers (see below) that form a unique key on the table.
#  - 'indexes':  An associative array of indexes ('indexame' :
#    specification).  Each specification is an array of one or more
#    key column specifiers (see below) that form an index on the
#    table.
#
# A key column specifier is either a string naming a column or an
# array of two elements, column name and length, specifying a prefix
# of the named column.
#
# As an example, here is a SUBSET of the schema definition for
# Drupal's 'node' table.  It show four fields (nid, vid, type, and
# title), the primary key on field 'nid', a unique key named 'vid' on
# field 'vid', and two indexes, one named 'nid' on field 'nid' and
# one named 'node_title_type' on the field 'title' and the first four
# bytes of the field 'type':
#
# @code
# schema['node'] = array(
#   'fields' : array(
#     'nid'      : array('type' : 'serial', 'unsigned' : True, \
#       'not None' : True),
#     'vid'      : array('type' : 'int', 'unsigned' : True, \
#       'not None' : True, 'default' : 0),
#     'type'     : array('type' : 'varchar', 'length' : 32, \
#       'not None' : True, 'default' : ''),
#     'title'    : array('type' : 'varchar', 'length' : 128, \
#       'not None' : True, 'default' : ''),
#   ),
#   'primary key' : array('nid'),
#   'unique keys' : array(
#     'vid'     : array('vid')
#   ),
#   'indexes' : array(
#     'nid'                 : array('nid'),
#     'node_title_type'     : array('title', array('type', 4)),
#   ),
# )
# @endcode
#
# @see drupal_install_schema()
#
#
# Create a new table from a Drupal table definition.
#
# @param ret
#   Array to which query results will be added.
# @param name
#   The name of the table to create.
# @param table
#   A Schema API table definition array.
#
def db_create_table(ret, name, table):
  php.Reference.check(ret)
  statements = create_table_sql(name, table)
  for statement in statements:
    ret.append( update_sql(statement) )


#
# Return an array of field names from an array of key/index column specifiers.
#
# This is usually an identity function but if a key/index uses a column prefix
# specification, this function extracts just the name.
#
# @param fields
#   An array of key/index column specifiers.
# @return
#   An array of field names.
#
def field_names(fields):
  ret = []
  for field in fields:
    if (php.is_array(field)):
      ret.append( field[0] )
    else:
      ret.append( field )
  return ret


#
# Given a Schema API field type, return the correct %-placeholder.
#
# Embed the placeholder in a query to be passed to db_query and and pass as an
# argument to db_query a value of the specified type.
#
# @param type
#   The Schema API type of a field.
# @return
#   The placeholder string to embed in a query for that type.
#
def type_placeholder(type_):
  if \
      type_ == 'varchar' or \
      type_ == 'char' or \
      type_ == 'text' or \
      type_ == 'datetime':
    return "'%s'"
  elif type_ == 'numeric':
    # Numeric values are arbitrary precision numbers.  Syntacically, numerics
    # should be specified directly in SQL. However, without single quotes
    # the %s placeholder does not protect against non-numeric characters such
    # as spaces which would expose us to SQL injection.
    return '%n'
  elif \
      type_ == 'serial' or \
      type_ == 'int':
    return '%d'
  elif type_ == 'float':
    return '%f'
  elif type_ == 'blob':
    return '%b'
  # There is no safe value to return here, so return something that
  # will cause the query to fail.
  return 'unsupported type ' +  type_  + 'for db_type_placeholder'








#
# Aliases
#
result = db.result
query = db.query
fetch_object = db.fetch_object
fetch_assoc = db.fetch_assoc
escape_string = db.escape_string


