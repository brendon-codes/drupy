# $Id: database.inc,v 1.94 2008/04/20 18:23:21 dries Exp $

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file database.py (ported from Drupal's database.inc)
#  Wrapper for database interface code.
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



active_db = None


#
# A hash value to check when outputting database errors, md5('DB_ERROR').
#
# @see drupal_error_handler()
#
DB_ERROR = 'a515ac9c2796ca0e23adbe92c68fc9fc'
DB_QUERY_REGEXP = '/(%d|%s|%%|%f|%b)/'


#
# Includes
#
from lib.drupy.DrupyPHP import *
from sites.default.settings import *
from lib.drupy import DrupyHelper
from lib.drupy.DrupyMySQL import *
import bootstrap as inc_bootstrap
import database_mysqli as db



#
# @defgroup database Database abstraction layer
# @{
# Allow the use of different database servers using the same code base.
#
# Drupal provides a slim database abstraction layer to provide developers with
# the ability to support multiple database servers easily. The intent of this
# layer is to preserve the syntax and power of SQL as much as possible, while
# letting Drupal control the pieces of queries that need to be written
# differently for different servers and provide basic security checks.
#
# Most Drupal database queries are performed by a call to db_query() or
# db_query_range(). Module authors should also consider using pager_query() for
# queries that return results that need to be presented on multiple pages, and
# tablesort_sql() for generating appropriate queries for sortable tables.
#
# For example, one might wish to return a list of the most recent 10 nodes
# authored by a given user. Instead of directly issuing the SQL query
# @code
#   SELECT n.title, n.body, n.created FROM node n WHERE n.uid = uid LIMIT 0, 10;
# @endcode
# one would instead call the Drupal functions:
# @code
#   result = db_query_range('SELECT n.title, n.body, n.created
#     FROM {node} n WHERE n.uid = %d', uid, 0, 10);
#   while (node = db_fetch_object(result)) {
#     // Perform operations on node->body, etc. here.
#   }
# @endcode
# Curly braces are used around "node" to provide table prefixing via
# db_prefix_tables(). The explicit use of a user ID is pulled out into an
# argument passed to db_query() so that SQL injection attacks from user input
# can be caught and nullified. The LIMIT syntax varies between database servers,
# so that is abstracted into db_query_range() arguments. Finally, note the
# common pattern of iterating over the result set using db_fetch_object().
#
#
# Perform an SQL query and return success or failure.
#
# @param sql
#   A string containing a complete SQL query.  %-substitution
#   parameters are not supported.
# @return
#   An array containing the keys:
#      success: a boolean indicating whether the query succeeded
#      query: the SQL query executed, passed through check_plain()
#
def update_sql(sql):
  result = db_query(sql, true);
  return {'success' : (result != False), 'query' : check_plain(sql)};
#
# Append a database prefix to all tables in a query.
#
# Queries sent to Drupal should wrap all table names in curly brackets. This
# function searches for this syntax and adds Drupal's table prefix to all
# tables, allowing Drupal to coexist with other systems in the same database if
# necessary.
#
# @param sql
#   A string containing a partial or entire SQL query.
# @return
#   The properly-prefixed string.
#
def db_prefix_tables(sql):
  global db_prefix;
  if (is_array(db_prefix)):
    if (array_key_exists('default', db_prefix)):
      tmp = db_prefix;
      del(tmp['default']);
      for key,val in tmp.items():
        sql = strtr(sql, {('{' + key + '}') : (val + key)});
      return strtr(sql, {'{' : db_prefix['default'], '}' : ''});
    else:
      for key,val in db_prefix.items():
        sql = strtr(sql, {('{' + key + '}') : (val + key)});
      return strtr(sql, {'{' : '', '}' : ''});
  else:
    return strtr(sql, {'{' : db_prefix, '}' : ''});



#
# Activate a database for future queries.
#
# If it is necessary to use external databases in a project, this function can
# be used to change where database queries are sent. If the database has not
# yet been used, it is initialized using the URL specified for that name in
# Drupal's configuration file. If this name is not defined, a duplicate of the
# default connection is made instead.
#
# Be sure to change the connection back to the default when done with custom
# code.
#
# @param name
#   The name assigned to the newly active database connection. If omitted, the
#   default connection will be made active.
#
# @return the name of the previously active database or FALSE if non was found.
#
# @todo BC: Need to eventually resolve the database importing mechanism here
# right now we are statically loading mysql at the top, but eventually we need
# to get this figured out 
#
def db_set_active(name = 'default'):
  global db_url, db_type, active_db, db_prefix;
  static(db_set_active, 'db_conns', {})
  static(db_set_active, 'active_name', False)
  if (db_url == None):
    include_once('includes/install.py');
    install_goto('install.py');
  if (not isset(db_set_active.db_conns, name)):
    # Initiate a new connection, using the named DB URL specified.
    if (isinstance(db_url, dict)):
      connect_url = (db_url[name] if array_key_exists(name, db_url) else db_url['default']);
    else:
      connect_url = db_url;
    db_type = substr(connect_url, 0, strpos(connect_url, '://'));
    #handler = "includes/database_%(db_type)s.py" % {'db_type' : db_type};
    #try:
    #  import db file here
    #except ImportError:
    #  _db_error_page("The database type '" + db_type + "' is unsupported. Please use either 'mysql' or 'mysqli' for MySQL, or 'pgsql' for PostgreSQL databases.");
    db_set_active.db_conns[name] = db.db_connect(connect_url);
    # We need to pass around the simpletest database prefix in the request
    # and we put that in the user_agent header.
    if (preg_match("/^simpletest\d+$/", SERVER['HTTP_USER_AGENT'])):
      db_prefix = SERVER['HTTP_USER_AGENT'];
  previous_name = db_set_active.active_name;
  # Set the active connection.
  db_set_active.active_name = name;
  active_db = db_set_active.db_conns[name];
  return previous_name;



#
# Helper function to show fatal database errors.
#
# Prints a themed maintenance page with the 'Site off-line' text,
# adding the provided error message in the case of 'display_errors'
# set to on. Ends the page request; no return.
#
# @param error
#   The error message to be appended if 'display_errors' is on.
#
def _db_error_page(error = ''):
  global db_type;
  inc_bootstrap.drupal_maintenance_theme();
  drupal_set_header('HTTP/1.1 503 Service Unavailable');
  drupal_set_title('Site off-line');
  message = '<p>The site is currently not available due to technical problems. Please try again later. Thank you for your understanding.</p>';
  message += '<hr /><p><small>If you are the maintainer of this site, please check your database settings in the <code>settings.php</code> file and ensure that your hosting provider\'s database server is running. For more help, see the <a href="http://drupal.org/node/258">handbook</a>, or contact your hosting provider.</small></p>';
  if (error and ini_get('display_errors')):
    message += '<p><small>The ' + theme('placeholder', db_type) + ' error was: ' + theme('placeholder', error) + '.</small></p>';
  print theme('maintenance_page', message);
  exit();


#
# Returns a boolean depending on the availability of the database.
#
def db_is_active():
  global active_db;
  return (active_db == None);


#
# Helper function for db_query().
#
def _db_query_callback(match, init = False):
  static(_db_query_callback, 'args')
  if (init):
    _db_query_callback.args = match;
    return;
  if match[1] == '%d': # We must use type casting to int to convert FALSE/NULL/(TRUE?)
    #print _db_query_callback.args
    #flush()
    #exit()
    return int(array_shift(_db_query_callback.args)); # We don't need db_escape_string as numbers are db-safe
  elif match[1] == '%s':
    return db.db_escape_string(array_shift(_db_query_callback.args));
  elif match[1] == '%%':
    return '%';
  elif match[1] == '%f':
    return float(array_shift(_db_query_callback.args));
  elif match[1] == '%b': # binary data
    return db.db_encode_blob(array_shift(_db_query_callback.args));



#
# Generate placeholders for an array of query arguments of a single type.
#
# Given a Schema API field type, return correct %-placeholders to
# embed in a query
#
# @param arguments
#  An array with at least one element.
# @param type
#   The Schema API type of a field (e.g. 'int', 'text', or 'varchar').
#
def db_placeholders(arguments, type = 'int'):
  placeholder = db_type_placeholder(type);
  return implode(',', array_fill(0, count(arguments), placeholder));


#
# Indicates the place holders that should be replaced in _db_query_callback().
#
#
# Helper function

#
# Aliases
#
db_result = db.db_result
db_query = db.db_query
db_fetch_object = db.db_fetch_object
db_fetch_assoc = db.db_fetch_assoc
db_escape_string = db.db_escape_string


