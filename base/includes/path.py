# $Id: path.inc,v 1.22 2008/04/14 17:48:33 dries Exp $

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file path.py (ported from Drupal's path.inc)
#  Functions to handle paths in Drupy, including path aliasing.
#  These functions are not loaded for cached pages, but modules that need
#  to use them in hook_init() or hook exit() can make them available, by
#  executing "drupal_bootstrap(DRUPAL_BOOTSTRAP_PATH);".
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

from lib.drupy.DrupyPHP import *
import bootstrap as inc_bootstrap
import module as inc_module


# Initialize the GET['q'] variable to the proper normal path.
#
def drupal_init_path():
  if (isset(GET, 'q') and not empty(GET['q'])):
    GET['q'] = drupal_get_normal_path(trim(GET['q'], '/'))
  else:
    GET['q'] = drupal_get_normal_path(inc_bootstrap.variable_get('site_frontpage', 'node'))


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
  static(drupal_lookup_path, '_map', {})
  static(drupal_lookup_path, 'no_src', {})
  # map is an array with language keys, holding arrays of Drupal paths to alias relations
  path_language =  (path_language if (path_language != '') else inc_bootstrap.language_.language)
  if (action == 'wipe' ):
    drupal_lookup_path._map = {}
    drupal_lookup_path.no_src = {}
  elif (inc_module.module_exists('path') and path != ''):
    if (action == 'alias'):
      if (isset(drupal_lookup_path._map[path_language], path)):
        return drupal_lookup_path._map[path_language][path]
      # Get the most fitting result falling back with alias without language
      alias = db_result(db_query("SELECT dst FROM {url_alias} WHERE src = '%s' AND language IN('%s', '') ORDER BY language DESC", path, path_language));
      drupal_lookup_path._map[path_language][path] = alias
      return alias
    # Check no_src for this path in case we've already determined that there
    # isn't a path that has this alias
    elif (action == 'source' and not isset(drupal_lookup_path.no_src[path_language], path)):
      # Look for the value path within the cached map
      src = ''
      src = array_search(path, drupal_lookup_path._map[path_language])
      if (not isset(drupal_lookup_path._map, path_language) or not src):
        # Get the most fitting result falling back with alias without language
        src = db_result(db_query("SELECT src FROM {url_alias} WHERE dst = '%s' AND language IN('%s', '') ORDER BY language DESC", path, path_language))
        if (src):
          drupal_lookup_path._map[path_language][src] = path
        else:
          # We can't record anything into map because we do not have a valid
          # index and there is no need because we have not learned anything
          # about any Drupal path. Thus cache to no_src.
          drupal_lookup_path.no_src[path_language][path] = True
      return src
  return False



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
  result = path
  alias = drupal_lookup_path('alias', path, path_language)
  if (alias):
    result = alias
  return result



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
# When viewing a page at the path "admin/build/types", for example, arg(0)
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
  static(arg, 'arguments')
  if (path == None):
    path = GET['q'];
  if (not isset(arg.arguments, path)):
    arg.arguments[path] = explode('/', path);
  if (index == None):
    return arg.arguments[path];
  if (isset(arg.arguments[path], index)):
    return arg.arguments[path][index];



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
  static(drupal_set_title, 'stored_title')
  if (title == None):
    drupal_set_title.stored_title = title;
  return drupal_set_title.stored_title;


#
# Check if the current page is the front page.
#
# @return
#   Boolean value: TRUE if the current page is the front page; FALSE if otherwise.
#
def drupal_is_front_page():
  # As drupal_init_path updates GET['q'] with the 'site_frontpage' path,
  # we can check it against the 'site_frontpage' variable.
  return (GET['q'] == drupal_get_normal_path(variable_get('site_frontpage', 'node')));


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
  static(drupal_match_path, 'regexps')
  if (not isset(drupal_match_path.regexps, patterns)):
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
    drupal_match_path.regexps[patterns] = pat_final;
    out = preg_match(drupal_match_path.regexps[patterns], path);
  return out;


