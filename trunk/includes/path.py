# Id: path.inc,v 1.20 2008/02/18 16:49:23 dries Exp $
#
# @file
# Functions to handle paths in Drupal, including path aliasing.
#
# These functions are not loaded for cached pages, but modules that need
# to use them in hook_init() or hook exit() can make them available, by
# executing "drupal_bootstrap(DRUPAL_BOOTSTRAP_PATH);".
#
#

static('static_drupallookuppath_map');
static('static_drupallookuppath_nosrc')
static('static_arg_arguments');
static('static_drupalsettitle_storedtitle');
static('static_drupalmatchpath_regexps');



# Initialize the _GET['q'] variable to the proper normal path.
#
def drupal_init_path():
  if (not empty(_GET['q'])):
    _GET['q'] = drupal_get_normal_path(trim(_GET['q'], '/'));
  else:
    _GET['q'] = drupal_get_normal_path(variable_get('site_frontpage', 'node'));


#
# Given an alias, return its Drupal system URL if one exists. Given a Drupal
# system URL return one of its aliases if such a one exists. Otherwise,
# return FALSE.
#
# @param action
#   One of the following values:
#   - wipe: delete the alias cache.
#   - alias: return an alias for a given Drupal system path (if one exists).
#   - source: return the Drupal system URL for a path alias (if one exists).
# @param path
#   The path to investigate for corresponding aliases or system URLs.
# @param path_language
#   Optional language code to search the path with. Defaults to the page language.
#   If there's no path defined for that language it will search paths without
#   language.
#
# @return
#   Either a Drupal system path, an aliased path, or FALSE if no path was
#   found.
#
def drupal_lookup_path(action, path = '', path_language = ''):
  global language;
  global static_drupallookuppath_map, static_drupallookuppath_nosrc;
  # map is an array with language keys, holding arrays of Drupal paths to alias relations
  path_language =  (path_language if (path_language != '') else language.language);
  if (static_drupallookuppath_map == None):
    static_drupallookuppath_map = {};
  if (static_drupallookuppath_nosrc == None):
    static_drupallookuppath_nosrc = {};  
  if (action == 'wipe' ):
    static_drupallookuppath_map = {};
    static_drupallookuppath_nosrc = {};
  elif (module_exists('path') and path != ''):
    if (action == 'alias'):
      if (isset(static_drupallookuppath_map[path_language], path)):
        return static_drupallookuppath_map[path_language][path];
      # Get the most fitting result falling back with alias without language
      alias = db_result(db_query("SELECT dst FROM {url_alias} WHERE src = '%s' AND language IN('%s', '') ORDER BY language DESC", path, path_language));
      static_drupallookuppath_map[path_language][path] = alias;
      return alias;
    # Check no_src for this path in case we've already determined that there
    # isn't a path that has this alias
    elif (action == 'source' and not isset(static_drupallookuppath_nosrc[path_language], path)):
      # Look for the value path within the cached map
      src = '';
      src = array_search(path, static_drupallookuppath_map[path_language]);
      if (not isset(static_drupallookuppath_map, path_language) or not src):
        # Get the most fitting result falling back with alias without language
        src = db_result(db_query("SELECT src FROM {url_alias} WHERE dst = '%s' AND language IN('%s', '') ORDER BY language DESC", path, path_language));
        if (src):
          static_drupallookuppath_map[path_language][src] = path;
        else:
          # We can't record anything into map because we do not have a valid
          # index and there is no need because we have not learned anything
          # about any Drupal path. Thus cache to no_src.
          static_drupallookuppath_nosrc[path_language][path] = True;
      return src;
  return False;




#
# Given an internal Drupal path, return the alias set by the administrator.
#
# @param path
#   An internal Drupal path.
# @param path_language
#   An optional language code to look up the path in.
#
# @return
#   An aliased path if one was found, or the original path if no alias was
#   found.
#
def drupal_get_path_alias(path, path_language = ''):
  result = path;
  alias = drupal_lookup_path('alias', path, path_language);
  if (alias):
    result = alias;
  return result;



#
# Given a path alias, return the internal path it represents.
#
# @param path
#   A Drupal path alias.
# @param path_language
#   An optional language code to look up the path in.
#
# @return
#   The internal path represented by the alias, or the original alias if no
#   internal path was found.
#
def drupal_get_normal_path(path, path_language = ''):
  result = path;
  src = drupal_lookup_path('source', path, path_language);
  if (src):
    result = src;
  if (function_exists('custom_url_rewrite_inbound')):
    # Modules may alter the inbound request path by reference.
    custom_url_rewrite_inbound(result, path, path_language);
  return result;



#
# Return a component of the current Drupal path.
#
# When viewing a page at the path "admin/content/types", for example, arg(0)
# would return "admin", arg(1) would return "content", and arg(2) would return
# "types".
#
# Avoid use of this function where possible, as resulting code is hard to read.
# Instead, attempt to use named arguments in menu callback functions. See the
# explanation in menu.inc for how to construct callbacks that take arguments.
#
# @param index
#   The index of the component, where each component is separated by a '/'
#   (forward-slash), and where the first component has an index of 0 (zero).
#
# @return
#   The component specified by index, or NULL if the specified component was
#   not found.
#
def arg(index = None, path = None):
  global static_arg_arguments;
  if (path == None):
    path = _GET['q'];
  if (not isset(static_arg_arguments, path)):
    static_arg_arguments[path] = explode('/', path);
  if (index == None):
    return static_arg_arguments[path];
  if (isset(static_arg_arguments[path], index)):
    return static_arg_arguments[path][index];



#
# Get the title of the current page, for display on the page and in the title bar.
#
# @return
#   The current page's title.
#
def drupal_get_title():
  title = drupal_set_title();
  # during a bootstrap, menu.inc is not included and thus we cannot provide a title
  if (title == None and function_exists('menu_get_active_title')):
    title = check_plain(menu_get_active_title());
  return title;


#
# Set the title of the current page, for display on the page and in the title bar.
#
# @param title
#   Optional string value to assign to the page title; or if set to NULL
#   (default), leaves the current title unchanged.
#
# @return
#   The updated title of the current page.
#
def drupal_set_title(title = None):
  global static_drupalsettitle_storedtitle;
  if (title == None):
    static_drupalsettitle_storedtitle = title;
  return static_drupalsettitle_storedtitle;


#
# Check if the current page is the front page.
#
# @return
#   Boolean value: TRUE if the current page is the front page; FALSE if otherwise.
#
def drupal_is_front_page():
  # As drupal_init_path updates _GET['q'] with the 'site_frontpage' path,
  # we can check it against the 'site_frontpage' variable.
  return (_GET['q'] == drupal_get_normal_path(variable_get('site_frontpage', 'node')));


#
# Check if a path matches any pattern in a set of patterns.
#
# @param path
#   The path to match.
# @param patterns
#   String containing a set of patterns separated by \n, \r or \r\n.
#
# @return
#   Boolean value: TRUE if the path matches a pattern, FALSE otherwise.
#
def drupal_match_path(path, patterns):
  global static_drupalmatchpath_regexps;
  if (not isset(static_drupalmatchpath_regexps, patterns)):
    #
    # DRUPY(BC): This had to be severly modified due to some 
    # hideous Drupalisms.
    # @todo: Implement arrays for preg functions
    # @todo: Implement preg_quote
    #
    frnt = variable_get('site_frontpage', 'node');
    frnt_q = preg_quote(frnt, '/');
    frnt_p = '\1' + frnt_q + '\2';
    pra2 = ['|', '.*', frnt_p];
    pra1 = ['/(\r\n?|\n)/', '/\\\\\*/', '/(^|\|)\\\\<front\\\\>($|\|)/'];
    pat_q = preg_quote(patterns, '/');
    pat_prep = preg_replace(pra1, pra2, pat_q);
    pat_final = '/^(' + pat_prep + ')$/';
    static_drupalmatchpath_regexps[patterns] = pat_final;
    out = preg_match(static_drupalmatchpath_regexps[patterns], path);
  return out;


