# Id: bootstrap.inc,v 1.206.2.2 2008/02/11 14:36:21 goba Exp $

#
# @file
# Functions that need to be loaded on every Drupal request.
#

#
# Static variables
# These are meant to emulate a 'static' var within PHP
# These should only be used within the context of their owner functions
#
static('static_confpath_conf');
static('static_drupalgetfilename_files');
static('static_pagegetcache_status');
static('static_drupalload_files');
static('static_gett_t');
static('static_languagelist_languages');
static('static_ipaddress_ipaddress');

#
# Global variables
#
set_global('user');
set_global('base_url');
set_global('_base_path');
set_global('base_root');
set_global('db_url');
set_global('db_prefix');
set_global('cookie_domain');
set_global('installed_profile');
set_global('update_free_access');
set_global('language');
set_global('timers');
set_global('conf');



#
# Indicates that the item should never be removed unless explicitly told to
# using cache_clear_all() with a cache ID.
#
define('CACHE_PERMANENT', 0);

#
# Indicates that the item should be removed at the next general cache wipe.
#
define('CACHE_TEMPORARY', -1);

#
# Indicates that page caching is disabled.
#
define('CACHE_DISABLED', 0);

#
# Indicates that page caching is enabled, using "normal" mode.
#
define('CACHE_NORMAL', 1);

#
# Indicates that page caching is using "aggressive" mode. This bypasses
# loading any modules for additional speed, which may break functionality in
# modules that expect to be run on each page load.
#
define('CACHE_AGGRESSIVE', 2);

#
#
# Severity levels, as defined in RFC 3164 http://www.faqs.org/rfcs/rfc3164.html
# @see watchdog()
# @see watchdog_severity_levels()
#
define('WATCHDOG_EMERG',    0); # Emergency: system is unusable
define('WATCHDOG_ALERT',    1); # Alert: action must be taken immediately
define('WATCHDOG_CRITICAL', 2); # Critical: critical conditions
define('WATCHDOG_ERROR',    3); # Error: error conditions
define('WATCHDOG_WARNING',  4); # Warning: warning conditions
define('WATCHDOG_NOTICE',   5); # Notice: normal but significant condition
define('WATCHDOG_INFO',     6); # Informational: informational messages
define('WATCHDOG_DEBUG',    7); # Debug: debug-level messages

#
# First bootstrap phase: initialize configuration.
#
define('DRUPAL_BOOTSTRAP_CONFIGURATION', 0);

#
# Second bootstrap phase: try to call a non-database cache
# fetch routine.
#
define('DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE', 1);

#
# Third bootstrap phase: initialize database layer.
#
define('DRUPAL_BOOTSTRAP_DATABASE', 2);

#
# Fourth bootstrap phase: identify and reject banned hosts.
#
define('DRUPAL_BOOTSTRAP_ACCESS', 3);

#
# Fifth bootstrap phase: initialize session handling.
#
define('DRUPAL_BOOTSTRAP_SESSION', 4);

#
# Sixth bootstrap phase: load bootstrap.inc and module.inc, start
# the variable system and try to serve a page from the cache.
#
define('DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE', 5);

#
# Seventh bootstrap phase: find out language of the page.
#
define('DRUPAL_BOOTSTRAP_LANGUAGE', 6);

#
# Eighth bootstrap phase: set _GET['q'] to Drupal path of request.
#
define('DRUPAL_BOOTSTRAP_PATH', 7);

#
# Final bootstrap phase: Drupal is fully loaded; validate and fix
# input data.
#
define('DRUPAL_BOOTSTRAP_FULL', 8);

#
# Role ID for anonymous users; should match what's in the "role" table.
#
define('DRUPAL_ANONYMOUS_RID', 1);

#
# Role ID for authenticated users; should match what's in the "role" table.
#
define('DRUPAL_AUTHENTICATED_RID', 2);

#
# No language negotiation. The default language is used.
#
define('LANGUAGE_NEGOTIATION_NONE', 0);

#
# Path based negotiation with fallback to default language
# if no defined path prefix identified.
#
define('LANGUAGE_NEGOTIATION_PATH_DEFAULT', 1);

#
# Path based negotiation with fallback to user preferences
# and browser language detection if no defined path prefix
# identified.
#
define('LANGUAGE_NEGOTIATION_PATH', 2);

#
# Domain based negotiation with fallback to default language
# if no language identified by domain.
#
define('LANGUAGE_NEGOTIATION_DOMAIN', 3);

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
  global static_confpath_conf;
  if (static_confpath_conf != None and not reset):
    return static_confpath_conf;
  confdir = 'sites';
  uri = explode('/', (_SERVER['SCRIPT_NAME'] if isset(_SERVER, 'SCRIPT_NAME') else _SERVER['SCRIPT_FILENAME']));
  server = explode('.', implode('.', array_reverse(explode(':', rtrim(_SERVER['HTTP_HOST'], '.')))));
  for i in range(count(uri)-1, 1, -1):
    for j in range(count(server), 1, -1):
      _dir = implode('.', array_slice(server, -j)) + implode('.', array_slice(uri, 0, i));
      if (file_exists("%(confdir)s/%(dir)s/settings.py" % {'confdir':confdir, 'dir':_dir}) or \
          (not require_settings and file_exists("confdir/dir"))):
        static_confpath_conf = "%(confdir)s/%(dir)s" % {'confdir':confdir, 'dir':_dir};
        return static_confpath_conf;
  static_confpath_conf = "%(confdir)s/default" % {'confdir':confdir};
  return static_confpath_conf;


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
def drupal_get_filename(type, name, filename = None):
  global static_drupalgetfilename_files;
  file = db_result(db_query("SELECT filename FROM {system} WHERE name = '%s' AND type = '%s'", name, type))
  if (static_drupalgetfilename_files == None):
    static_drupalgetfilename_files = {}
    static_drupalgetfilename_files[type] = {}
  if (filename != None and file_exists(filename)):
    static_drupalgetfilename_files[type][name] = filename;
  elif (isset(static_drupalgetfilename_files[type], name)):
    # nothing
    pass;
  # Verify that we have an active database connection, before querying
  # the database.  This is required because this def is called both
  # before we have a database connection (i.e. during installation) and
  # when a database connection fails.
  elif (db_is_active() and (file and file_exists(file))):
    static_drupalgetfilename_files[type][name] = file;
  else:
    # Fallback to searching the filesystem if the database connection is
    # not established or the requested file is not found.
    config = conf_path();
    _dir = ('themes/engines' if (type == 'theme_engine') else (type + 's'));
    file = (("%(name)s.engine" % {'name':name}) if (type == 'theme_engine') else ("%(name)s.type" % {'name':name}));
    fileVals = {'name':name, 'file':file, 'dir':_dir, 'config':config};
    fileChecker = [
      "config/dir/file" % fileVals,
      "config/dir/name/file" % fileVals,
      "dir/file" % fileVals,
      "dir/name/file" % fileVals
    ];
    for _file in fileChecker:
      if (file_exists(_file)):
        static_drupalgetfilename_files[type][name] = _file;
        break;
  if (isset(static_drupalgetfilename_files[type], name)):
    return static_drupalgetfilename_files[type][name];



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
def page_get_cache(status_only = False):
  global static_pagegetcache_status;
  if (status_only):
    return static_pagegetcache_status;
  cache = None;
  if (user == None and _SERVER['REQUEST_METHOD'] == 'GET' and count(drupal_set_message()) == 0):
    cache = cache_get(base_root . request_uri(), 'cache_page');
    if (empty(cache)):
      # This may be needed
      #
      # ob_start()
      #
      static_pagegetcache_status = True;
  return cache;




#
# Call all init or exit hooks without including all modules.
#
# @param hook
#   The name of the bootstrap hook we wish to invoke.
#
def bootstrap_invoke_all(hook):
  for module in module_list(True, True):
    drupal_load('module', module);
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
def drupal_load(type, name):
  global static_drupalload_files;
  if (static_drupalload_files == None):
    static_drupalload_files = {}
  if (not isset(static_drupalload_files, type)):
    static_drupalload_files[type] = {}
  if (isset(static_drupalload_files[type], name)):
    return True
  else:
    filename = drupal_get_filename(type, name);
    if (filename != False):
      include_once("./" + filename);
      static_drupalload_files[type][name] = True;
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
# Perform an access check for a given mask and rule type. Rules are usually
# created via admin/user/rules page.
#
# If any allow rule matches, access is allowed. Otherwise, if any deny rule
# matches, access is denied.  If no rule matches, access is allowed.
#
# @param type string
#   Type of access to check: Allowed values are:
#     - 'host': host name or IP address
#     - 'mail': e-mail address
#     - 'user': username
# @param mask string
#   String or mask to test: '_' matches any character, '%' matches any
#   number of characters.
# @return bool
#   TRUE if access is denied, FALSE if access is allowed.
#
def drupal_is_denied(type, mask):
  # Because this def is called for every page request, both cached
  # and non-cached pages, we tried to optimize it as much as possible.
  # We deny access if the only matching records in the {access} table have
  # status 0 (deny). If any have status 1 (allow), or if there are no
  # matching records, we allow access.
  sql = "SELECT 1 FROM {access} WHERE type = '%s' AND LOWER('%s') LIKE LOWER(mask) AND status = %d";
  return ( \
    db_result( db_query_range(sql, type, mask, 0, 0, 1) ) != False and \
    db_result( db_query_range(sql, type, mask, 1, 0, 1) ) == False \
  );


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
  elif phase == DRUPAL_BOOTSTRAP_ACCESS:
    # Deny access to hosts which were banned - t() is not yet available.
    if (drupal_is_denied('host', ip_address())):
      header('HTTP/1.1 403 Forbidden');
      print 'Sorry, ' + check_plain(ip_address()) + ' has been banned.';
      exit();
  elif phase == DRUPAL_BOOTSTRAP_SESSION:
    require_once(variable_get('session_inc', './includes/session.inc'), locals());
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
  global static_gett_t;
  if (static_gett_t == None):
    t =  ('st' if function_exists('install_main') else 't');
  return t;



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
  global static_languagelist_list;
  # Reset language list
  if (reset):
    static_languagelist_languages = {};
  # Init language list
  if (static_languagelist_languages == None):
    if (variable_get('language_count', 1) > 1 or module_exists('locale')):
      result = db_query('SELECT# FROM {languages} ORDER BY weight ASC, name ASC');
      while True:
        row = db_fetch_object(result);
        if row == None:
          break;
        static_languagelist_languages['language'][row.language] = row;
    else:
      # No locale module, so use the default language only.
      _default = language_default();
      static_languagelist_languages['language'][_default.language] = _default;
  # Return the array indexed by the right field
  if (not isset(static_languagelist_languages, field)):
    static_languagelist_languages[field] = {};
    for lang in static_languagelist_languages['language']:
      # Some values should be collected into an array
      if (in_array(field, ['enabled', 'weight'])):
        static_languagelist_languages[field][lang.field][lang.language] = lang;
      else:
        static_languagelist_languages[field][lang.field] = lang;
  return static_languagelist_languages[field];



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
  global static_ipaddress_ipaddress;
  if (static_ipaddress_ipaddress == None):
    static_ipaddress_ipaddress = _SERVER['REMOTE_ADDR'];
    if (variable_get('reverse_proxy', 0) and array_key_exists('HTTP_X_FORWARDED_FOR', _SERVER)):
      # If an array of known reverse proxy IPs is provided, then trust
      # the XFF header if request really comes from one of them.
      reverse_proxy_addresses = variable_get('reverse_proxy_addresses', []);
      if (not empty(reverse_proxy_addresses) and \
          in_array(static_ipaddress_ipaddress, reverse_proxy_addresses)):
        # If there are several arguments, we need to check the most
        # recently added one, i.e. the last one.
        static_ipaddress_ipaddress = array_pop(explode(',', _SERVER['HTTP_X_FORWARDED_FOR']));
  return static_ipaddress_ipaddress;


