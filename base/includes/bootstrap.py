# $Id: bootstrap.inc,v 1.210 2008/05/13 17:38:42 dries Exp $

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The drupal project can be found at http://drupal.org
# @file bootstrap.py (ported from Drupal's bootstrap.inc)
#  Functions that need to be loaded on every Drupal request.
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

require_once( './lib/drupy/DrupySession.py' )



#
# Global variables
#
user = None
base_url = None
_base_path = None
base_root = None
db_url = None
db_prefix = None
cookie_domain = None
installed_profile = None
update_free_access = None
language = None
timers = None
conf = None



#
# Indicates that the item should never be removed unless explicitly told to
# using cache_clear_all() with a cache ID.
#
CACHE_PERMANENT = 0

#
# Indicates that the item should be removed at the next general cache wipe.
#
CACHE_TEMPORARY = -1

#
# Indicates that page caching is disabled.
#
CACHE_DISABLED = 0

#
# Indicates that page caching is enabled, using "normal" mode.
#
CACHE_NORMAL = 1

#
# Indicates that page caching is using "aggressive" mode. This bypasses
# loading any modules for additional speed, which may break functionality in
# modules that expect to be run on each page load.
#
CACHE_AGGRESSIVE = 2

#
#
# Severity levels, as defined in RFC 3164 http://www.faqs.org/rfcs/rfc3164.html
# @see watchdog()
# @see watchdog_severity_levels()
#
WATCHDOG_EMERG = 0 # Emergency: system is unusable
WATCHDOG_ALERT = 1 # Alert: action must be taken immediately
WATCHDOG_CRITICAL = 2 # Critical: critical conditions
WATCHDOG_ERROR = 3 # Error: error conditions
WATCHDOG_WARNING = 4 # Warning: warning conditions
WATCHDOG_NOTICE = 5 # Notice: normal but significant condition
WATCHDOG_INFO = 6 # Informational: informational messages
WATCHDOG_DEBUG = 7 # Debug: debug-level messages

#
# First bootstrap phase: initialize configuration.
#
DRUPAL_BOOTSTRAP_CONFIGURATION = 0

#
# Second bootstrap phase: try to call a non-database cache
# fetch routine.
#
DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE = 1

#
# Third bootstrap phase: initialize database layer.
#
DRUPAL_BOOTSTRAP_DATABASE = 2

#
# Fourth bootstrap phase: identify and reject banned hosts.
#
DRUPAL_BOOTSTRAP_ACCESS = 3

#
# Fifth bootstrap phase: initialize session handling.
#
DRUPAL_BOOTSTRAP_SESSION = 4

#
# Sixth bootstrap phase: load bootstrap.inc and module.inc, start
# the variable system and try to serve a page from the cache.
#
DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE = 5

#
# Seventh bootstrap phase: find out language of the page.
#
DRUPAL_BOOTSTRAP_LANGUAGE = 6

#
# Eighth bootstrap phase: set _GET['q'] to Drupal path of request.
#
DRUPAL_BOOTSTRAP_PATH = 7

#
# Final bootstrap phase: Drupal is fully loaded; validate and fix
# input data.
#
DRUPAL_BOOTSTRAP_FULL = 8

#
# Role ID for anonymous users; should match what's in the "role" table.
#
DRUPAL_ANONYMOUS_RID = 9

#
# Role ID for authenticated users; should match what's in the "role" table.
#
DRUPAL_AUTHENTICATED_RID = 10

#
# No language negotiation. The default language is used.
#
LANGUAGE_NEGOTIATION_NONE = 0

#
# Path based negotiation with fallback to default language
# if no defined path prefix identified.
#
LANGUAGE_NEGOTIATION_PATH_DEFAULT = 1

#
# Path based negotiation with fallback to user preferences
# and browser language detection if no defined path prefix
# identified.
#
LANGUAGE_NEGOTIATION_PATH = 2

#
# Domain based negotiation with fallback to default language
# if no language identified by domain.
#
LANGUAGE_NEGOTIATION_DOMAIN = 3


#
# Start the timer with the specified name. If you start and stop
# the same timer multiple times, the measured intervals will be
# accumulated.
#
# @param name
#   The name of the timer.
#
def timer_start(name):
  global timers;
  if timers == None:
    timers = {};
  if not isset(timers, name):
    timers[name] = {}
  (usec, sec) = explode(' ', microtime());
  timers[name]['start'] = float(usec) + float(sec);
  timers[name]['count'] = ((timers[name]['count'] + 1) if isset(timers[name],'count') else 1);


#
# Read the current timer value without stopping the timer.
#
# @param name
#   The name of the timer.
# @return
#   The current timer value in ms.
#
def timer_read(name):
  global timers;
  if (isset(timers[name], 'start')):
    (usec, sec) = explode(' ', microtime());
    stop = float(usec) + float(sec);
    diff = round((stop - timers[name]['start']) * 1000, 2);
    if (isset(timers[name], 'time')):
      diff += timers[name]['time'];
    return diff;


#
# Stop the timer with the specified name.
#
# @param name
#   The name of the timer.
# @return
#   A timer array. The array contains the number of times the
#   timer has been started and stopped (count) and the accumulated
#   timer value in ms (time).
#
def timer_stop(name):
  global timers;
  timers[name]['time'] = timer_read(name);
  del(timers[name]['start']);
  return timers[name];


#
# Find the appropriate configuration directory.
#
# Try finding a matching configuration directory by stripping the website's
# hostname from left to right and pathname from right to left. The first
# configuration file found will be used; the remaining will ignored. If no
# configuration file is found, return a default value 'confdir/default'.
#
# Example for a fictitious site installed at
# http://www.drupal.org:8080/mysite/test/ the 'settings.php' is searched in
# the following directories:
#
#  1. confdir/8080.www.drupal.org.mysite.test
#  2. confdir/www.drupal.org.mysite.test
#  3. confdir/drupal.org.mysite.test
#  4. confdir/org.mysite.test
#
#  5. confdir/8080.www.drupal.org.mysite
#  6. confdir/www.drupal.org.mysite
#  7. confdir/drupal.org.mysite
#  8. confdir/org.mysite
#
#  9. confdir/8080.www.drupal.org
# 10. confdir/www.drupal.org
# 11. confdir/drupal.org
# 12. confdir/org
#
# 13. confdir/default
#
# @param require_settings
#   Only configuration directories with an existing settings.php file
#   will be recognized. Defaults to TRUE. During initial installation,
#   this is set to FALSE so that Drupal can detect a matching directory,
#   then create a new settings.php file in it.
# @param reset
#   Force a full search for matching directories even if one had been
#   found previously.
# @return
#   The path of the matching directory.
#
def conf_path(require_settings = True, reset = False):
  static(conf_path, 'conf', '');
  if (not empty(conf_path.conf) and not reset):
    return static_confpath_conf;
  confdir = 'sites';
  uri = explode('/', (_SERVER['SCRIPT_NAME'] if isset(_SERVER, 'SCRIPT_NAME') else _SERVER['SCRIPT_FILENAME']));
  server = explode('.', implode('.', array_reverse(explode(':', rtrim(_SERVER['HTTP_HOST'], '.')))));
  for i in range(count(uri)-1, 0, -1):
    for j in range(count(server), 1, -1):
      _dir = implode('.', array_slice(server, -j)) + implode('.', array_slice(uri, 0, i));
      if (file_exists("%(confdir)s/%(dir)s/settings.py" % {'confdir':confdir, 'dir':_dir}) or \
          (not require_settings and file_exists("confdir/dir"))):
        conf_path.conf = "%(confdir)s/%(dir)s" % {'confdir':confdir, 'dir':_dir};
        return static_confpath_conf;
  conf_path.conf = "%(confdir)s/default" % {'confdir':confdir};
  return conf_path.conf;


#
# Unsets all disallowed global variables. See allowed for what's allowed.
#
def drupal_unset_globals():
  # Do nothing
  pass;

#
# Loads the configuration and sets the base URL, cookie domain, and
# session name correctly.
#
def conf_init():
  global base_url, _base_path, \
    base_root, db_url, db_prefix, \
    cookie_domain, installed_profile, \
    update_free_access, conf;
  conf = {};
  thisConfPath = conf_path();
  if (file_exists('./' + thisConfPath + '/settings.py')):
    include_once( './' + thisConfPath + '/settings.py', globals());
  if (base_url != None):
    # Parse fixed base URL from settings.php.
    parts = parse_url(base_url);
    if (not isset(parts, 'path')):
      parts['path'] = '';
    _base_path = parts['path'] + '/';
    # Build base_root (everything until first slash after "scheme://").
    base_root = substr(base_url, 0, strlen(base_url) - strlen(parts['path']));
  else:
    # Create base URL
    base_root = ('https' if (isset(_SERVER, 'HTTPS') and _SERVER['HTTPS'] == 'on') else 'http');
    # As _SERVER['HTTP_HOST'] is user input, ensure it only contains
    # characters allowed in hostnames.
    base_root += '://' + preg_replace('/[^a-z0-9-:._]/i', '', _SERVER['HTTP_HOST']);
    base_url = base_root;
    # _SERVER['SCRIPT_NAME'] can, in contrast to _SERVER['PHP_SELF'], not
    # be modified by a visitor.
    dir = trim(dirname(_SERVER['SCRIPT_NAME']), '\,/');
    if (len(dir) > 0):
      _base_path = "/dir";
      base_url += _base_path;
      _base_path += '/';
    else:
      _base_path = '/';
  if (cookie_domain != None):
    # If the user specifies the cookie domain, also use it for session name.
    _session_name = cookie_domain;
  else:
    # Otherwise use base_url as session name, without the protocol
    # to use the same session identifiers across http and https.
    (_dummy, _session_name) = explode('://', base_url, 2);
    # We escape the hostname because it can be modified by a visitor.
    if (not empty(_SERVER['HTTP_HOST'])):
      cookie_domain = check_plain(_SERVER['HTTP_HOST']);
  # Strip leading periods, www., and port numbers from cookie domain.
  cookie_domain = ltrim(cookie_domain, '.');
  if (strpos(cookie_domain, 'www.') == 0):
    cookie_domain = substr(cookie_domain, 4);
  cookie_domain = explode(':', cookie_domain);
  cookie_domain = '.' + cookie_domain[0];
  # Per RFC 2109, cookie domains must contain at least one dot other than the
  # first. For hosts such as 'localhost' or IP Addresses we don't set a cookie domain.
  if (count(explode('.', cookie_domain)) > 2 and not is_numeric(str_replace('.', '', cookie_domain))):
    ini_set('session.cookie_domain', cookie_domain);
  #print session_name;
  session_name('SESS' + drupy_md5(_session_name));



#
# Returns and optionally sets the filename for a system item (module,
# theme, etc.). The filename, whether provided, cached, or retrieved
# from the database, is only returned if the file exists.
#
# This def plays a key role in allowing Drupal's resources (modules
# and themes) to be located in different places depending on a site's
# configuration. For example, a module 'foo' may legally be be located
# in any of these three places:
#
# modules/foo/foo.module
# sites/all/modules/foo/foo.module
# sites/example.com/modules/foo/foo.module
#
# Calling drupal_get_filename('module', 'foo') will give you one of
# the above, depending on where the module is located.
#
# @param type
#   The type of the item (i.e. theme, theme_engine, module).
# @param name
#   The name of the item for which the filename is requested.
# @param filename
#   The filename of the item if it is to be set explicitly rather
#   than by consulting the database.
#
# @return
#   The filename of the requested item.
#
def drupal_get_filename(_type, name, filename = None):
  static(drupal_get_filename, 'files', {})
  file = db_result(db_query("SELECT filename FROM {system} WHERE name = '%s' AND type = '%s'", name, _type))
  if (not isset(drupal_get_filename.files, _type)):
    drupal_get_filename.files[_type] = {}
  if (filename != None and file_exists(filename)):
    drupal_get_filename.files[_type][name] = filename;
  elif (isset(drupal_get_filename.files[_type], name)):
    # nothing
    pass;
  # Verify that we have an active database connection, before querying
  # the database.  This is required because this def is called both
  # before we have a database connection (i.e. during installation) and
  # when a database connection fails.
  elif (db_is_active() and (file and file_exists(file))):
    drupal_get_filename.files[_type][name] = file;
  else:
    # Fallback to searching the filesystem if the database connection is
    # not established or the requested file is not found.
    config = conf_path();
    _dir = ('themes/engines' if (_type == 'theme_engine') else (_type + 's'));
    file = (("%(name)s.engine" % {'name':name}) if (_type == 'theme_engine') else ("%(name)s.type" % {'name':name}));
    fileVals = {'name':name, 'file':file, 'dir':_dir, 'config':config};
    fileChecker = [
      "config/dir/file" % fileVals,
      "config/dir/name/file" % fileVals,
      "dir/file" % fileVals,
      "dir/name/file" % fileVals
    ];
    for _file in fileChecker:
      if (file_exists(_file)):
        drupal_get_filename.files[_type][name] = _file;
        break;
  if (isset(drupal_get_filename.files[_type], name)):
    return drupal_get_filename.files[_type][name];



#
# Load the persistent variable table.
#
# The variable table is composed of values that have been saved in the table
# with variable_set() as well as those explicitly specified in the configuration
# file.
#
def variable_init(_conf = {}):
  # NOTE: caching the variables improves performance by 20% when serving cached pages.
  cached = cache_get('variables', 'cache');
  if (cached):
    variables = cached.data;
  else:
    result = db_query('SELECT# FROM {variable}');
    while True:
      variable = db_fetch_object(result);
      if (not variable):
        break;
      variables[variable.name] = unserialize(variable.value);
    cache_set('variables', variables);
  for name,value in _conf.items():
    variables[name] = value;
  return variables;




#
# Return a persistent variable.
#
# @param name
#   The name of the variable to return.
# @param default
#   The default value to use if this variable has never been set.
# @return
#   The value of the variable.
#
def variable_get(name, _default):
  global conf;
  return  (conf[name] if isset(conf, name) else _default);


#
# Set a persistent variable.
#
# @param name
#   The name of the variable to set.
# @param value
#   The value to set. This can be any PHP data type; these functions take care
#   of serialization as necessary.
#
def variable_set(name, value):
  global conf;
  serialized_value = serialize(value);
  db_query("UPDATE {variable} SET value = '%s' WHERE name = '%s'", serialized_value, name);
  if (db_affected_rows() == 0):
    db_query("INSERT INTO {variable} (name, value) VALUES ('%s', '%s')", name, serialized_value);
  cache_clear_all('variables', 'cache');
  conf[name] = value;



#
# Unset a persistent variable.
#
# @param name
#   The name of the variable to undefine.
#
def variable_del(name):
  global conf;
  db_query("DELETE FROM {variable} WHERE name = '%s'", name);
  cache_clear_all('variables', 'cache');
  del(conf[name]);


#
# Retrieve the current page from the cache.
#
# Note: we do not serve cached pages when status messages are waiting (from
# a redirected form submission which was completed).
#
# @param status_only
#   When set to TRUE, retrieve the status of the page cache only
#   (whether it was started in this request or not).
#
def page_get_cache():
  cache = None;
  if (user == None and _SERVER['REQUEST_METHOD'] == 'GET' and count(drupal_set_message()) == 0):
    cache = cache_get(base_root + request_uri(), 'cache_page');
    if (empty(cache)):
      ob_start()
  return cache;




#
# Call all init or exit hooks without including all modules.
#
# @param hook
#   The name of the bootstrap hook we wish to invoke.
#
def bootstrap_invoke_all(hook):
  for module in module_list(True, True):
    module_invoke(module, hook);


#
# Includes a file with the provided type and name. This prevents
# including a theme, engine, module, etc., more than once.
#
# @param type
#   The type of item to load (i.e. theme, theme_engine, module).
# @param name
#   The name of the item to load.
#
# @return
#   TRUE if the item is loaded or has already been loaded.
#
def drupal_load(_type, name):
  static(drupal_load, 'files', {})
  if (not isset(drupal_load.files, type)):
    drupal_load.files[_type] = {}
  if (isset(drupal_load.files[_type], name)):
    return True
  else:
    filename = drupal_get_filename(_type, name);
    if (filename != False):
      include_once("./" + filename);
      drupal_load.files[_type][name] = True;
      return True;
    else:
      return False;


#
# Set HTTP headers in preparation for a page response.
#
# Authenticated users are always given a 'no-cache' header, and will
# fetch a fresh page on every request.  This prevents authenticated
# users seeing locally cached pages that show them as logged out.
#
# @see page_set_cache()
#
def drupal_page_header():
  header("Expires: Sun, 19 Nov 1978 05:00:00 GMT");
  header("Last-Modified: " + gmdate("%D, %d %M %Y %H:%i:%s") + " GMT");
  header("Cache-Control: store, no-cache, must-revalidate");
  header("Cache-Control: post-check=0, pre-check=0", False);



#
# Set HTTP headers in preparation for a cached page response.
#
# The general approach here is that anonymous users can keep a local
# cache of the page, but must revalidate it on every request.  Then,
# they are given a '304 Not Modified' response as long as they stay
# logged out and the page has not been modified.
#
#
def drupal_page_cache_header(cache):
  # Set default values:
  last_modified = gmdate('D, d M Y H:i:s', cache.created) + ' GMT';
  etag = '"' + drupy_md5(last_modified) + '"';
  # See if the client has provided the required HTTP headers:
  if_modified_since =  (stripslashes(_SERVER['HTTP_IF_MODIFIED_SINCE']) \
    if isset(_SERVER, 'HTTP_IF_MODIFIED_SINCE') else False);
  if_none_match = (stripslashes(_SERVER['HTTP_IF_NONE_MATCH']) \
    if isset(_SERVER, 'HTTP_IF_NONE_MATCH') else False);
  if (if_modified_since and if_none_match
      and if_none_match == etag # etag must match
      and if_modified_since == last_modified):  # if-modified-since must match
    header('HTTP/1.1 304 Not Modified');
    # All 304 responses must send an etag if the 200 response for the same object contained an etag
    header("Etag: %(etag)s" % {'etag':etag});
    exit();
  # Send appropriate response:
  header("Last-Modified: %(last_modified)s" % {'last_modified':last_modified});
  header("Etag: %(etag)s" % {'etag':etag});
  # The following headers force validation of cache:
  header("Expires: Sun, 19 Nov 1978 05:00:00 GMT");
  header("Cache-Control: must-revalidate");
  if (variable_get('page_compression', True)):
    # Determine if the browser accepts gzipped data.
    if (strpos(_SERVER['HTTP_ACCEPT_ENCODING'], 'gzip') == False and function_exists('gzencode')):
      # Strip the gzip header and run uncompress.
      cache.data = gzinflate(substr(substr(cache.data, 10), 0, -8));
    elif (function_exists('gzencode')):
      header('Content-Encoding: gzip');
  # Send the original request's headers. We send them one after
  # another so PHP's header() def can deal with duplicate
  # headers.
  headers = explode("\n", cache.headers);
  for _header in headers:
    header(_header);
  print cache.data;




#
# Define the critical hooks that force modules to always be loaded.
#
def bootstrap_hooks():
  return ['boot', 'exit'];



#
# Unserializes and appends elements from a serialized string.
#
# @param obj
#   The object to which the elements are appended.
# @param field
#   The attribute of obj whose value should be unserialized.
#
def drupal_unpack(obj, field = 'data'):
  data = unserialize(obj.field);
  if (obj.field and not empty(data)):
    for key,value in data.items():
      if (not isset(obj, key)):
        setattr(obj, key, value);
  return obj;



#
# Return the URI of the referring page.
#
def referer_uri():
  if (isset(_SERVER, 'HTTP_REFERER')):
    return _SERVER['HTTP_REFERER'];



#
# Encode special characters in a plain-text string for display as HTML.
#
# Uses drupal_validate_utf8 to prevent cross site scripting attacks on
# Internet Explorer 6.
#
def check_plain(text):
  return (htmlspecialchars(text, ENT_QUOTES) if drupal_validate_utf8(text) else '');


#
# Checks whether a string is valid UTF-8.
#
# All functions designed to filter input should use drupal_validate_utf8
# to ensure they operate on valid UTF-8 strings to prevent bypass of the
# filter.
#
# When text containing an invalid UTF-8 lead byte (0xC0 - 0xFF) is presented
# as UTF-8 to Internet Explorer 6, the program may misinterpret subsequent
# bytes. When these subsequent bytes are HTML control characters such as
# quotes or angle brackets, parts of the text that were deemed safe by filters
# end up in locations that are potentially unsafe; An onerror attribute that
# is outside of a tag, and thus deemed safe by a filter, can be interpreted
# by the browser as if it were inside the tag.
#
# This def exploits preg_match behaviour (since PHP 4.3.5) when used
# with the u modifier, as a fast way to find invalid UTF-8. When the matched
# string contains an invalid byte sequence, it will fail silently.
#
# preg_match may not fail on 4 and 5 octet sequences, even though they
# are not supported by the specification.
#
# The specific preg_match behaviour is present since PHP 4.3.5.
#
# @param text
#   The text to check.
# @return
#   TRUE if the text is valid UTF-8, FALSE if not.
#
def drupal_validate_utf8(text):
  if (strlen(text) == 0):
    return True;
  return (preg_match('/^./us', text) == 1);



#
# Since _SERVER['REQUEST_URI'] is only available on Apache, we
# generate an equivalent using other environment variables.
#
def request_uri():
  if (isset(_SERVER, 'REQUEST_URI')):
    uri = _SERVER['REQUEST_URI'];
  else:
    if (isset(_SERVER, 'argv')):
      uri = _SERVER['SCRIPT_NAME'] + '?' + _SERVER['argv'][0];
    elif (isset(_SERVER, 'QUERY_STRING')):
      uri = _SERVER['SCRIPT_NAME'] + '?' + _SERVER['QUERY_STRING'];
    else:
      uri = _SERVER['SCRIPT_NAME'];
  return uri;



#
# Log a system message.
#
# @param type
#   The category to which this message belongs.
# @param message
#   The message to store in the log. See t() for documentation
#   on how message and variables interact. Keep message
#   translatable by not concatenating dynamic values into it!
# @param variables
#   Array of variables to replace in the message on display or
#   NULL if message is already translated or not possible to
#   translate.
# @param severity
#   The severity of the message, as per RFC 3164
# @param link
#   A link to associate with the message.
#
# @see watchdog_severity_levels()
#
def watchdog(type, message, variables = [], severity = WATCHDOG_NOTICE, link = None):
  # Prepare the fields to be logged
  log_message = {
    'type'        : type,
    'message'     : message,
    'variables'   : variables,
    'severity'    : severity,
    'link'        : link,
    'user'        : user,
    'request_uri' : base_root . request_uri(),
    'referer'     : referer_uri(),
    'ip'          : ip_address(),
    'timestamp'   : drupy_time(),
  }
  # Call the logging hooks to log/process the message
  for module in module_implements('watchdog', True):
    module_invoke(module, 'watchdog', log_message);



#
# Set a message which reflects the status of the performed operation.
#
# If the def is called with no arguments, this def returns all set
# messages without clearing them.
#
# @param message
#   The message should begin with a capital letter and always ends with a
#   period '.'.
# @param type
#   The type of the message. One of the following values are possible:
#   - 'status'
#   - 'warning'
#   - 'error'
# @param repeat
#   If this is FALSE and the message is already set, then the message won't
#   be repeated.
#
def drupal_set_message(message = None, type = 'status', repeat = True):
  if (message):
    if (not isset(_SESSION, 'messages')):
      _SESSION['messages'] = {};
    if (not isset(_SESSION['messages'], type)):
      _SESSION['messages'][type] = [];
    if (repeat or not in_array(message, _SESSION['messages'][type])):
      _SESSION['messages'][type].append( message );
  # messages not set when DB connection fails
  return  (_SESSION['messages'] if isset(_SESSION, 'messages') else None);



#
# Return all messages that have been set.
#
# @param type
#   (optional) Only return messages of this type.
# @param clear_queue
#   (optional) Set to FALSE if you do not want to clear the messages queue
# @return
#   An associative array, the key is the message type, the value an array
#   of messages. If the type parameter is passed, you get only that type,
#   or an empty array if there are no such messages. If type is not passed,
#   all message types are returned, or an empty array if none exist.
#
def drupal_get_messages(type = None, clear_queue = True):
  messages = drupal_set_message();
  if (not empty('messages')):
    if (type != None and type != False):
      if (clear_queue):
        del(_SESSION['messages'][type]);
      if (isset(messages, type)):
        return {type : messages[type]};
    else:
      if (clear_queue):
        del(_SESSION['messages']);
      return messages;
  return {};



#
# Check to see if an IP address has been blocked.
#
# Blocked IP addresses are stored in the database by default. However for
# performance reasons we allow an override in settings.php. This allows us
# to avoid querying the database at this critical stage of the bootstrap if
# an administrative interface for IP address blocking is not required.
#
# @param $ip string
#   IP address to check.
# @return bool
#   TRUE if access is denied, FALSE if access is allowed.
#
def drupal_is_denied(ip):
  # Because this function is called on every page request, we first check
  # for an array of IP addresses in settings.php before querying the
  # database.
  blocked_ips = variable_get('blocked_ips', None);
  if (blocked_ips != None and is_array(blocked_ips)):
    return in_array(ip, blocked_ips)
  else:
    sql = "SELECT 1 FROM {blocked_ips} WHERE ip = '%s'";
    return (db_result(db_query(sql, ip)) != False)


#
# Generates a default anonymous user object.
#
# @return Object - the user object.
#
def drupal_anonymous_user(session = ''):
  user = stdClass();
  user.uid = 0;
  user.hostname = ip_address();
  user.roles = {};
  user.roles[DRUPAL_ANONYMOUS_RID] = 'anonymous user';
  user.session = session;
  user.cache = 0;
  return user;



#
# A string describing a phase of Drupal to load. Each phase adds to the
# previous one, so invoking a later phase automatically runs the earlier
# phases too. The most important usage is that if you want to access the
# Drupal database from a script without loading anything else, you can
# include bootstrap.inc, and call drupal_bootstrap(DRUPAL_BOOTSTRAP_DATABASE).
#
# @param phase
#   A constant. Allowed values are:
#     DRUPAL_BOOTSTRAP_CONFIGURATION: initialize configuration.
#     DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE: try to call a non-database cache fetch routine.
#     DRUPAL_BOOTSTRAP_DATABASE: initialize database layer.
#     DRUPAL_BOOTSTRAP_ACCESS: identify and reject banned hosts.
#     DRUPAL_BOOTSTRAP_SESSION: initialize session handling.
#     DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE: load bootstrap.inc and module.inc, start
#       the variable system and try to serve a page from the cache.
#     DRUPAL_BOOTSTRAP_LANGUAGE: identify the language used on the page.
#     DRUPAL_BOOTSTRAP_PATH: set _GET['q'] to Drupal path of request.
#     DRUPAL_BOOTSTRAP_FULL: Drupal is fully loaded, validate and fix input data.
#
def drupal_bootstrap(phase):
  # DRUPY(BC): Why the hell did Drupal set the vars in here as static?
  # No longer needed. 
  phase_index = 0;
  phases = range(DRUPAL_BOOTSTRAP_CONFIGURATION, DRUPAL_BOOTSTRAP_FULL);
  while (phase >= phase_index and isset(phases, phase_index)):
    current_phase = phases[phase_index];
    #Drupal was unsetting the phase var here.
    #This was completely unnecessary and most likely the cause of some bugs
    phase_index += 1;
    _drupal_bootstrap(current_phase);



def _drupal_bootstrap(phase):
  global conf;
  if phase == DRUPAL_BOOTSTRAP_CONFIGURATION:
    # Start a page timer:
    timer_start('page');
    # Initialize the configuration
    conf_init();
  elif phase == DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE:
    # Allow specifying special cache handlers in settings.php, like
    # using memcached or files for storing cache information.
    require_once( variable_get('cache_inc', './includes/cache.py'), globals() );
    # If the page_cache_fastpath is set to TRUE in settings.php and
    # page_cache_fastpath (implemented in the special implementation of
    # cache.inc) printed the page and indicated this with a returned TRUE
    # then we are done.
    if (variable_get('page_cache_fastpath', False) and page_cache_fastpath()):
      exit();
  elif phase == DRUPAL_BOOTSTRAP_DATABASE:
    # Initialize the default database.
    require_once('./includes/database.py', globals());
    db_set_active();
    # Register autoload functions so that we can access classes and interfaces.
    # spl_autoload_register('drupal_autoload_class')
    # spl_autoload_register('drupal_autoload_interface')
  elif phase == DRUPAL_BOOTSTRAP_ACCESS:
    # Deny access to blocked IP addresses - t() is not yet available
    if (drupal_is_denied(ip_address())):
      header('HTTP/1.1 403 Forbidden');
      print 'Sorry, ' + check_plain(ip_address()) + ' has been banned.';
      exit();
  elif phase == DRUPAL_BOOTSTRAP_SESSION:
    require_once(variable_get('session_inc', './includes/session.py'));
    session_set_save_handler('sess_open', 'sess_close', 'sess_read', 'sess_write', 'sess_destroy_sid', 'sess_gc');
    session_start();
  elif phase == DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE:
    # Initialize configuration variables, using values from settings.php if available.
    conf = variable_init( ({} if (conf == None) else conf) );
    # Load module handling.
    require_once('./includes/module.inc', locals());
    cache_mode = variable_get('cache', CACHE_DISABLED);
    # Get the page from the cache.
    cache =  ('' if (cache_mode == CACHE_DISABLED) else page_get_cache());
    # If the skipping of the bootstrap hooks is not enforced, call hook_boot.
    if (cache_mode != CACHE_AGGRESSIVE):
      bootstrap_invoke_all('boot');
    # If there is a cached page, display it.
    if (cache):
      drupal_page_cache_header(cache);
      # If the skipping of the bootstrap hooks is not enforced, call hook_exit.
      if (cache_mode != CACHE_AGGRESSIVE):
        bootstrap_invoke_all('exit');
      # We are done.
      exit();
    # Prepare for non-cached page workflow.
    drupal_page_header();
  elif phase == DRUPAL_BOOTSTRAP_LANGUAGE:
    drupal_init_language();
  elif DRUPAL_BOOTSTRAP_PATH:
    require_once('./includes/path.inc', locals());
    # Initialize _GET['q'] prior to loading modules and invoking hook_init().
    drupal_init_path();
  elif phase == DRUPAL_BOOTSTRAP_FULL:
    require_once('./includes/common.inc', locals());
    _drupal_bootstrap_full();



#
# Enables use of the theme system without requiring database access.
#
# Loads and initializes the theme system for site installs, updates and when
# the site is in off-line mode. This also applies when the database fails.
#
# @see _drupal_maintenance_theme()
#
def drupal_maintenance_theme():
  require_once( './includes/theme_maintenance.py', globals());
  _drupal_maintenance_theme();


#
# Return the name of the localisation function. Use in code that needs to
# run both during installation and normal operation.
#
def get_t():
  static(get_t, 't')
  if (get_t.t == None):
    get_t.t =  ('st' if function_exists('install_main') else 't');
  return get_t.t;



#
#  Choose a language for the current page, based on site and user preferences.
#
def drupal_init_language():
  # Ensure the language is correctly returned, even without multilanguage support.
  # Useful for eg. XML/HTML 'lang' attributes.
  if (variable_get('language_count', 1) == 1):
    language = language_default();
  else:
    include_once('./includes/language.inc', locals());
    language = language_initialize();


#
# Get a list of languages set up indexed by the specified key
#
# @param field The field to index the list with.
# @param reset Boolean to request a reset of the list.
#
def language_list(field = 'language', reset = False):
  static(language_list, 'languages')
  # Reset language list
  if (reset):
    languages_list.languages = {};
  # Init language list
  if (languages_list.languages == None):
    if (variable_get('language_count', 1) > 1 or module_exists('locale')):
      result = db_query('SELECT# FROM {languages} ORDER BY weight ASC, name ASC');
      while True:
        row = db_fetch_object(result);
        if row == None:
          break;
        languages_list.languages['language'][row.language] = row;
    else:
      # No locale module, so use the default language only.
      _default = language_default();
      languages_list.languages['language'][_default.language] = _default;
  # Return the array indexed by the right field
  if (not isset(languages_list.languages, field)):
    languages_list.languages[field] = {};
    for lang in languages_list.languages['language']:
      # Some values should be collected into an array
      if (in_array(field, ['enabled', 'weight'])):
        languages_list.languages[field][lang.field][lang.language] = lang;
      else:
        languages_list.languages[field][lang.field] = lang;
  return languages_list.languages[field];



#
# Default language used on the site
#
# @param property
#   Optional property of the language object to return
#
def language_default(property = None):
  theList = drupy_object({
    'language' : 'en',
    'name' : 'English',
    'native' : 'English',
    'direction' : 0,
    'enabled' : 1,
    'plurals' : 0,
    'formula' : '',
    'domain' : '',
    'prefix' : '',
    'weight' : 0,
    'javascript' : ''
  });
  languagelist_language = variable_get('language_default', theList);
  return (language.property if property else language);


#
# If Drupal is behind a reverse proxy, we use the X-Forwarded-For header
# instead of _SERVER['REMOTE_ADDR'], which would be the IP address
# of the proxy server, and not the client's.
#
# @return
#   IP address of client machine, adjusted for reverse proxy.
#
def ip_address():
  static(ip_address, 'ip_address')
  if (ip_address.ip_address == None):
    ip_address.ip_address = _SERVER['REMOTE_ADDR'];
    if (variable_get('reverse_proxy', 0) and array_key_exists('HTTP_X_FORWARDED_FOR', _SERVER)):
      # If an array of known reverse proxy IPs is provided, then trust
      # the XFF header if request really comes from one of them.
      reverse_proxy_addresses = variable_get('reverse_proxy_addresses', []);
      if (not empty(reverse_proxy_addresses) and \
          in_array(ip_address.ip_address, reverse_proxy_addresses)):
        # If there are several arguments, we need to check the most
        # recently added one, i.e. the last one.
        ip_address.ip_address = array_pop(explode(',', _SERVER['HTTP_X_FORWARDED_FOR']));
  return ip_address.ip_address;


#
# @ingroup registry
# @{
#
#
# Confirm that a function is available.
#
# If the function is already available, this function does nothing.
# If the function is not available, it tries to load the file where the
# function lives. If the file is not available, it returns False, so that it
# can be used as a drop-in replacement for function_exists().
#
# @param function
#   The name of the function to check or load.
# @return
#   True if the function is now available, False otherwise.
#
def drupal_function_exists(function):
  static(drupal_function_exists, 'checked', [])
  if (defined('MAINTENANCE_MODE')):
    return function_exists(function)
  if (isset(drupal_function_exists.checked, function)):
    return drupal_function_exists.checked[function]
  drupal_function_exists.checked[function] = False
  if (function_exists(function)):
    registry_mark_code('function', function)
    drupal_function_exists.checked[function] = True
    return True
  file = db_result(db_query("SELECT filename FROM {registry} WHERE name = '%s' AND type = '%s'", function, 'function'))
  if (file):
    require_once(file)
    drupal_function_exists.checked[function] = function_exists(function)
    if (drupal_function_exists.checked[function]):
      registry_mark_code('function', function)
  return drupal_function_exists.checked[function]



#
# Confirm that an interface is available.
#
# This function parallels drupal_function_exists(), but is rarely
# called directly. Instead, it is registered as an spl_autoload()
# handler, and PHP calls it for us when necessary.
#
# @param interface
#   The name of the interface to check or load.
# @return
#   True if the interface is currently available, False otherwise.
#
def drupal_autoload_interface(interface):
  return _registry_check_code('interface', interface)



#
# Confirm that a class is available.
#
# This function parallels drupal_function_exists(), but is rarely
# called directly. Instead, it is registered as an spl_autoload()
# handler, and PHP calls it for us when necessary.
#
# @param class
#   The name of the class to check or load.
# @return
#   True if the class is currently available, False otherwise.
#
def drupal_autoload_class(_class):
  return _registry_check_code('class', _class)



#
# Helper for registry_check_{interface, class}.
#
def _registry_check_code(_type, name):
  file = db_result(db_query("SELECT filename FROM {registry} WHERE name = '%s' AND type = '%s'", name, _type))
  if (file):
    require_once(file)
    registry_mark_code(_type, name)
    return True


#
# Collect the resources used for this request.
#
# @param type
#   The type of resource.
# @param name
#   The name of the resource.
# @param return
#   Boolean flag to indicate whether to return the resources.
#
def registry_mark_code(_type, name, _return = False):
  static(registry_mark_code, 'resources', [])
  if (_type and name):
    if (not isset(registry_mark_code.resources, _type, )):
      registry_mark_code.resources[_type] = []
    if (not in_array(name, registry_mark_code.resources[_type])):
      registry_mark_code.resources[type].append( name )
  if (_return):
    return registry_mark_code.resources




#
# Rescan all enabled modules and rebuild the registry.
#
# Rescans all code in modules or includes directory, storing a mapping of
# each function, file, and hook implementation in the database.
#
def drupal_rebuild_code_registry():
  require_once( './includes/registry.inc' )
  _drupal_rebuild_code_registry()



#
# Save hook implementations cache.
#
# @param hook
#   Array with the hook name and list of modules that implement it.
# @param write_to_persistent_cache
#   Whether to write to the persistent cache.
#
def registry_cache_hook_implementations(hook, write_to_persistent_cache = False):
  static(registry_cache_hook_implementations, implementations, {})
  if (hook):
    # Newer is always better, so overwrite anything that's come before.
    registry_cache_hook_implementations.implementations[hook['hook']] = hook['modules']
  if (write_to_persistent_cache == True):
    # Only write this to cache if the implementations data we are going to cache
    # is different to what we loaded earlier in the request.
    if (registry_cache_hook_implementations.implementations != registry_get_hook_implementations_cache()):
      cache_set('hooks', implementations, 'cache_registry');




#
# Save the files required by the registry for this path.
#
def registry_cache_path_files():
  used_code = registry_mark_code(None, None, True)
  if (used_code):
    files = []
    type_sql = []
    params = []
    for type,names in used_code.items():
      type_sql.append( "(name IN (" +  db_placeholders(names, 'varchar')  + ") AND type = '%s')" )
      params = array_merge(params, names)
      params.append( type )
    res = db_query("SELECT DISTINCT filename FROM {registry} WHERE " +  implode(' OR ', type_sql), params)
    while True:
      row = db_fetch_object(res)
      if (row == None):
        break
      files.append( row.filename )
    if (files):
      sort(files);
      # Only write this to cache if the file list we are going to cache
      # is different to what we loaded earlier in the request.
      if (files != registry_load_path_files(True)):
        menu = menu_get_item();
        cache_set('registry:' + menu['path'], implode(';', files), 'cache_registry');




#
# registry_load_path_files
#
def registry_load_path_files(_return = False):
  static(registry_load_path_files, 'file_cache_data', [])
  if (_return):
    sort(registry_load_path_files.file_cache_data);
    return registry_load_path_files.file_cache_data;
  menu = menu_get_item();
  cache = cache_get('registry:' + menu['path'], 'cache_registry');
  if (not empty(cache.data)):
    for file in explode(';', cache.data):
      require_once(file);
      registry_load_path_files.file_cache_data.append( file );



#
# registry_get_hook_implementations_cache
#
def registry_get_hook_implementations_cache():
  static(registry_get_hook_implementations_cache, 'implementations')
  if (registry_get_hook_implementations_cache.implementations == None):
    cache = cache_get('hooks', 'cache_registry')
    if (cache):
      registry_get_hook_implementations_cache.implementations = cache.data;
    else:
      registry_get_hook_implementations_cache.implementations = [];
  return registry_get_hook_implementations_cache.implementations;



#
# @} End of "ingroup registry".
#
