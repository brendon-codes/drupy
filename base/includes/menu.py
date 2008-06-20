#!/usr/bin/env python

# $Id: menu.inc,v 1.275 2008/06/12 20:49:39 dries Exp $
#

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file menu.py (ported from Drupal's menu.inc)
#  API for the Drupal menu system.
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-05-22
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

from lib.drupy import DrupyPHP as p

#
#
# @defgroup menu Menu system
# @{
# Define the navigation menus, and route page requests to code based on URLs.
#
# The Drupal menu system drives both the navigation system from a user
# perspective and the callback system that Drupal uses to respond to URLs
# passed from the browser. For this reason, a good understanding of the
# menu system is fundamental to the creation of complex modules.
#
# Drupal's menu system follows a simple hierarchy defined by paths.
# Implementations of hook_menu() define menu items and assign them to
# paths (which should be unique). The menu system aggregates these items
# and determines the menu hierarchy from the paths. For example, if the
# paths defined were a, a/b, e, a/b/c/d, f/g, and a/b/h, the menu system
# would form the structure:
# - a
#   - a/b
#     - a/b/c/d
#     - a/b/h
# - e
# - f/g
# Note that the number of elements in the path does not necessarily
# determine the depth of the menu item in the tree.
#
# When responding to a page request, the menu system looks to see if the
# path requested by the browser is registered as a menu item with a
# callback. If not, the system searches up the menu tree for the most
# complete match with a callback it can find. If the path a/b/i is
# requested in the tree above, the callback for a/b would be used.
#
# The found callback function is called with any arguments specified
# in the "page arguments" attribute of its menu item. The
# attribute must be an array. After these arguments, any remaining
# components of the path are appended as further arguments. In this
# way, the callback for a/b above could respond to a request for
# a/b/i differently than a request for a/b/j.
#
# For an illustration of this process, see page_example.module.
#
# Access to the callback functions is also protected by the menu system.
# The "access callback" with an optional "access arguments" of each menu
# item is called before the page callback proceeds. If this returns True,
# then access is granted; if False, then access is denied. Menu items may
# omit this attribute to use the value provided by an ancestor item.
#
# In the default Drupal interface, you will notice many links rendered as
# tabs. These are known in the menu system as "local tasks", and they are
# rendered as tabs by default, though other presentations are possible.
# Local tasks function just as other menu items in most respects. It is
# convention that the names of these tasks should be short verbs if
# possible. In addition, a "default" local task should be provided for
# each set. When visiting a local task's parent menu item, the default
# local task will be rendered as if it is selected; this provides for a
# normal tab user experience. This default task is special in that it
# links not to its provided path, but to its parent item's path instead.
# The default task's path is only used to place it appropriately in the
# menu hierarchy.
#
# Everything described so far is stored in the menu_router table. The
# menu_links table holds the visible menu links. By default these are
# derived from the same hook_menu definitions, however you are free to
# add more with menu_link_save().
#
#
# @name Menu flags
# @{
# Flags for use in the "type" attribute of menu items.
#

#
# Internal menu flag -- menu item is the root of the menu tree.
#
MENU_IS_ROOT = 0x0001

#
# Internal menu flag -- menu item is visible in the menu tree.
#
MENU_VISIBLE_IN_TREE = 0x0002

#
# Internal menu flag -- menu item is visible in the breadcrumb.
#
MENU_VISIBLE_IN_BREADCRUMB = 0x0004

#
# Internal menu flag -- menu item links back to its parnet.
#

MENU_LINKS_TO_PARENT = 0x0008

#
# Internal menu flag -- menu item can be modified by administrator.
#
MENU_MODIFIED_BY_ADMIN = 0x0020

#
# Internal menu flag -- menu item was created by administrator.
#
MENU_CREATED_BY_ADMIN = 0x0040

#
# Internal menu flag -- menu item is a local task.
#
MENU_IS_LOCAL_TASK = 0x0080


#
# @} End of "Menu flags".
#
#
# @name Menu item types
# @{
# Menu item definitions provide one of these constants, which are shortcuts for
# combinations of the above flags.
#
#
# Menu type -- A "normal" menu item that's shown in menu and breadcrumbs.
# Normal menu items show up in the menu tree and can be moved/hidden by
# the administrator. Use this for most menu items. It is the default value if
# no menu item type is specified.
#
MENU_NORMAL_ITEM = MENU_VISIBLE_IN_TREE | MENU_VISIBLE_IN_BREADCRUMB

# Menu type -- A hidden, internal callback, typically used for API calls.
#
# Callbacks simply register a path so that the correct function is fired
# when the URL is accessed. They are not shown in the menu.
#
MENU_CALLBACK = MENU_VISIBLE_IN_BREADCRUMB

# Menu type -- A normal menu item, hidden until enabled by an administrator.
#
# Modules may "suggest" menu items that the administrator may enable. They act
# just as callbacks do until enabled, at which time they act like normal items.
# Note for the value: 0x0010 was a flag which is no longer used, but this way
# the values of MENU_CALLBACK and MENU_SUGGESTED_ITEM are separate.
#
MENU_SUGGESTED_ITEM = MENU_VISIBLE_IN_BREADCRUMB | 0x0010

# Menu type -- A task specific to the parent item, usually rendered as a tab.
#
# Local tasks are menu items that describe actions to be performed on their
# parent item. An example is the path "node/52/edit", which performs the
# "edit" task on "node/52".
MENU_LOCAL_TASK = MENU_IS_LOCAL_TASK

# Menu type -- The "default" local task, which is initially active.
#
# Every set of local tasks should provide one "default" task, that links to the
# same path as its parent when clicked.
#
MENU_DEFAULT_LOCAL_TASK = MENU_IS_LOCAL_TASK | MENU_LINKS_TO_PARENT
#
# @} End of "Menu item types".
#
#
# @name Menu status codes
# @{
# Status codes for menu callbacks.
#

#
# Internal menu status code -- Menu item was found.
#
MENU_FOUND = 1

#
# Internal menu status code -- Menu item was not found.
#
MENU_NOT_FOUND = 2

#
# Internal menu status code -- Menu item access is denied.
#
MENU_ACCESS_DENIED = 3

#
# Internal menu status code -- Menu item inaccessible because site is offline.
#
MENU_SITE_OFFLINE = 4

#
# @} End of "Menu status codes".
#
#
# @Name Menu tree parameters
# @{
# Menu tree
#
#
# The maximum number of path elements for a menu callback
#
MENU_MAX_PARTS = 7
#
# The maximum depth of a menu links tree - matches the number of p columns.
#
MENU_MAX_DEPTH = 9

#
# @} End of "Menu tree parameters".
#
#
# Returns the ancestors (and relevant placeholders) for any given path.
#
# For example, the ancestors of node/12345/edit are:
# - node/12345/edit
# - node/12345/%
# - node/%/edit
# - node/%/%
# - node/12345
# - node/%
# - node
#
# To generate these, we will use binary numbers. Each bit represents a
# part of the path. If the bit is 1, then it represents the original
# value while 0 means wildcard. If the path is node/12/edit/foo
# then the 1011 bitstring represents node/%/edit/foo where % means that
# any argument matches that part.  We limit ourselves to using binary
# numbers that correspond the patterns of wildcards of router items that
# actually exists.  This list of 'masks' is built in menu_rebuild().
#
# @param parts
#   An array of path parts, for the above example
#   array('node', '12345', 'edit').
# @return
#   An array which contains the ancestors and placeholders. Placeholders
#   simply contain as many '%s' as the ancestors.
#
def menu_get_ancestors(parts):
  number_parts = p.count(parts)
  placeholders = []
  ancestors = []
  length =  number_parts - 1
  end = (1 << number_parts) - 1
  masks = variable_get('menu_masks', [])
  # Only examine patterns that actually exist as router items (the masks).
  for i in masks:
    if (i > end):
      # Only look at masks that are not longer than the path of interest.
      continue
    elif (i < (1 << length)):
      # We have exhausted the masks of a given length, so decrease the length.
      length -= 1
    current = ''
    for j in range(length, -1, -1):
      if (i & (1 << j)):
        current += parts[length - j]
      else:
        current += '%'
      if (j):
        current += '/'
    placeholders.append( "'%s'" )
    ancestors.append( current )
  return (ancestors, placeholders)



#
# The menu system uses serialized arrays stored in the database for
# arguments. However, often these need to change according to the
# current path. This function unserializes such an array and does the
# necessary change.
#
# Integer values are mapped according to the map parameter. For
# example, if p.unserialize(data) is array('view', 1) and map is
# array('node', '12345') then 'view' will not be changed because
# it is not an integer, but 1 will as it is an integer. As map[1]
# is '12345', 1 will be replaced with '12345'. So the result will
# be array('node_load', '12345').
#
# @param @data
#   A serialized array.
# @param @map
#   An array of potential replacements.
# @return
#   The data array unserialized and mapped.
#
def menu_unserialize(data, map):
  data = p.unserialize(data)
  if (data):
    for k,v in data.items():
      if (is_int(v)):
        data[k] = (map[v] if p.isset(map, v) else '')
    return data
  else:
    return []



#
# Replaces the statically cached item for a given path.
#
# @param path
#   The path.
# @param router_item
#   The router item. Usually you take a router entry from menu_get_item and
#   set it back either modified or to a different path. This lets you modify the
#   navigation block, the page title, the breadcrumb and the page help in one
#   call.
#
def menu_set_item(path, router_item):
  menu_get_item(path, router_item)



#
# Get a router item.
#
# @param path
#   The path, for example node/5. The function will find the corresponding
#   node/% item and return that.
# @param router_item
#   Internal use only.
# @return
#   The router item, an associate array corresponding to one row in the
#   menu_router table. The value of key map holds the loaded objects. The
#   value of key access is True if the current user can access this page.
#   The values for key title, page_arguments, access_arguments will be
#   filled in based on the database values and the objects loaded.
#
def menu_get_item(path = None, router_item = None):
  p.static(menu_get_item, 'router_items')
  if (not p.isset(path)):
    path = p.GET['q']
  if (router_item != None):
    menu_get_item.router_items[path] = router_item
  if (not p.isset(menu_get_item.router_items, path)):
    original_map = arg(None, path)
    parts = p.array_slice(original_map, 0, MENU_MAX_PARTS)
    (ancestors, placeholders) = menu_get_ancestors(parts)
    router_item = db_fetch_array(db_query_range('SELECT * FROM {menu_router} WHERE path IN (' +  implode (',', placeholders)  + ') ORDER BY fit DESC', ancestors, 0, 1))
    if (router_item):
      map_ = _menu_translate(router_item, original_map)
      if (map_ == False):
        menu_get_item.router_items[path] = False
        return False
      if (router_item['access']):
        router_item['map'] = map
        router_item['page_arguments'] = p.array_merge(menu_unserialize(router_item['page_arguments'], map), p.array_slice(map, router_item['number_parts']))
    menu_get_item.router_items[path] = router_item
  return menu_get_item.router_items[path]


#
# Execute the page callback associated with the current path
#
def menu_execute_active_handler(path = None):
  if (_menu_site_is_offline()):
    return MENU_SITE_OFFLINE
  if (variable_get('menu_rebuild_needed', False)):
    menu_rebuild()
  router_item = menu_get_item(path)
  if (router_item):
    registry_load_path_files()
    if (router_item['access']):
      if (drupal_function_exists(router_item['page_callback'])):
        return router_item['page_callback']( *router_item['page_arguments'] )
    else:
      return MENU_ACCESS_DENIED
  return MENU_NOT_FOUND



#
# Loads objects into the map as defined in the item['load_functions'].
#
# @param item
#   A menu router or menu link item
# @param map
#   An array of path arguments (ex: array('node', '5'))
# @return
#   Returns True for success, False if an object cannot be loaded.
#   Names of object loading functions are placed in item['load_functions'].
#   Loaded objects are placed in map[]; keys are the same as keys in the
#   item['load_functions'] array.
#   item['access'] is set to False if an object cannot be loaded.
#
def _menu_load_objects(item, map_):
  p.Reference.check(item)
  p.Reference.check(map_)
  load_functions = item['load_functions']
  if (load_functions):
    # If someone calls this function twice, then unserialize will fail.
    load_functions_unserialized = p.unserialize(load_functions)
    if (load_functions_unserialized):
      load_functions = load_functions_unserialized
    path_map = map_.val
    for index,function in load_functions.items():
      if (function):
        value = (path_map[index] if p.isset(path_map, index) else '')
        if (p.is_array(function)):
          # Set up arguments for the load function. These were pulled from
          # 'load arguments' in the hook_menu() entry, but they need
          # some processing. In this case the function is the key to the
          # load_function array, and the value is the list of arguments.
          function, args = each(function)
          load_functions[index] = function
          # Some arguments are placeholders for dynamic items to process.
          for i,arg in args.items():
            if (arg == '%index'):
              # Pass on argument index to the load function, so multiple
              # occurances of the same placeholder can be identified.
              args[i] = index
            if (arg == '%map'):
              # Pass on menu map by reference. The accepting function must
              # also declare this as a reference if it wants to modify
              # the map.
              args[i] = map_
            if (is_int(arg)):
              args[i] = (path_map[arg] if p.isset(path_map, arg) else '')
          array_unshift(args, value)
          return_ = function(*args)
        else:
          return_ = function(value)
        # If callback returned an error or there is no callback, trigger 404.
        if (return_ == False):
          item.val['access'] = False
          map_.val = False
          return False
        map.val[index] = return_
    item.val['load_functions'] = load_functions
  return True



#
# Check access to a menu item using the access callback
#
# @param item
#   A menu router or menu link item
# @param map
#   An array of path arguments (ex: array('node', '5'))
# @return
#   item['access'] becomes True if the item is accessible, False otherwise.
#
def _menu_check_access(item, map_):
  p.Reference.check(item)
  # Determine access callback, which will decide whether or not the current
  # user has access to this path.
  callback = (0 if p.empty(item.val['access_callback']) else p.trim(item.val['access_callback']))
  # Check for a True or False value.
  if (p.is_numeric(callback)):
    item.val['access'] = drupy_bool(callback)
  else:
    arguments = menu_unserialize(item.val['access_arguments'], map_)
    # As call_user_func_array is quite slow and user_access is a very common
    # callback, it is worth making a special case for it.
    if (callback == 'user_access'):
      item.val['access'] = (user_access(arguments[0]) if (p.count(arguments) == 1) else user_access(arguments[0], arguments[1]))
    else:
      item.val['access'] = callback(*arguments)



#
# Localize the router item title using t() or another callback.
#
# Translate the title and description to allow storage of English title
# strings in the database, yet display of them in the language required
# by the current user.
#
# @param item
#   A menu router item or a menu link item.
# @param map
#   The path as an array with objects already replaced. E.g., for path
#   node/123 map would be array('node', node) where node is the node
#   object for node 123.
# @param link_translate
#   True if we are translating a menu link item; False if we are
#   translating a menu router item.
# @return
#   No return value.
#   item['title'] is localized according to item['title_callback'].
#   If an item's callback is check_plain(), item['options']['html'] becomes
#   True.
#   item['description'] is translated using t().
#   When doing link translation and the item['options']['attributes']['title']
#   (link title attribute) matches the description, it is translated as well.
#
def _menu_item_localize(item, map_, link_translate = False):
  p.Reference.check(item)
  callback = item.val['title_callback']
  item.val['localized_options'] = item.val['options']
  # If we are not doing link translation or if the title matches the
  # link title of its router item, localize it.
  if (not link_translate or (not p.empty(item.val['title']) and (item.val['title'] == item.val['link_title']))):
    # t() is a special case. Since it is used very close to all the time,
    # we handle it directly instead of using indirect, slower methods.
    if (callback == 't'):
      if (p.empty(item.val['title_arguments'])):
        item.val['title'] = t(item.val['title'])
      else:
        item.val['title'] = t(item.val['title'], menu_unserialize(item.val['title_arguments'], map_))
    elif (callback):
      if (p.empty(item.val['title_arguments'])):
        item.val['title'] = callback(item.val['title'])
      else:
        item.val['title'] = callback(*menu_unserialize(item.val['title_arguments'], map_))
      # Avoid calling check_plain again on l() function.
      if (callback == 'check_plain'):
        item.val['localized_options']['html'] = True
  elif (link_translate):
    item.val['title'] = item.val['link_title']
  # Translate description, see the motivation above.
  if (not p.empty(item.val['description'])):
    original_description = item.val['description']
    item.val['description'] = t(item.val['description'])
    if (link_translate and p.isset(item['options']['attributes'], 'title') and \
        item['options']['attributes']['title'] == original_description):
      item.val['localized_options']['attributes']['title'] = item.val['description']




#
# Handles dynamic path translation and menu access control.
#
# When a user arrives on a page such as node/5, this function determines
# what "5" corresponds to, by inspecting the page's menu path definition,
# node/%node. This will call node_load(5) to load the corresponding node
# object.
#
# It also works in reverse, to allow the display of tabs and menu items which
# contain these dynamic arguments, translating node/%node to node/5.
#
# Translation of menu item titles and descriptions are done here to
# allow for storage of English strings in the database, and translation
# to the language required to generate the current page
#
# @param router_item
#   A menu router item
# @param map
#   An array of path arguments (ex: array('node', '5'))
# @param to_arg
#   Execute item['to_arg_functions'] or not. Use only if you want to render a
#   path from the menu table, for example tabs.
# @return
#   Returns the map with objects loaded as defined in the
#   item['load_functions. item['access'] becomes True if the item is
#   accessible, False otherwise. item['href'] is set according to the map.
#   If an error occurs during calling the load_functions (like trying to load
#   a non existing node) then this function return False.
#
def _menu_translate(router_item, map_, to_arg = False):
  p.Reference.check(router_item)
  path_map = map_
  if (not _menu_load_objects(router_item.val, map_)):
    # An error occurred loading an object.
    router_item.val['access'] = False
    return False
  if (to_arg):
    _menu_link_map_translate(path_map, router_item.val['to_arg_functions'])
  # Generate the link path for the page request or local tasks.
  link_map = p.explode('/', router_item.val['path'])
  for i in range(router_item.val['number_parts']):
    if (link_map[i] == '%'):
      link_map[i] = path_map[i]
  router_item.val['href'] = p.implode('/', link_map)
  router_item.val['options'] = {}
  _menu_check_access(router_item.val, map_)
  # For performance, don't localize an item the user can't access.
  if (router_item.val['access']):
    _menu_item_localize(router_item.val, map_)
  return map_



#
# This function translates the path elements in the map using any to_arg
# helper function. These functions take an argument and return an object.
# See http://drupal.org/node/109153 for more information.
#
# @param map
#   An array of path arguments (ex: array('node', '5'))
# @param to_arg_functions
#   An array of helper function (ex: array(2 : 'menu_tail_to_arg'))
#
def _menu_link_map_translate(map_, to_arg_functions):
  p.Reference.check(map_)
  if (to_arg_functions):
    to_arg_functions = p.unserialize(to_arg_functions)
    for index,function in to_arg_functions.items():
      # Translate place-holders into real values.
      arg = function((map_.val[index] if (not p.empty(map_.val[index])) else ''), map_.val, index)
      if (not p.empty(map[index]) or p.isset(arg)):
        map_.val[index] = arg
      else:
        del(map_.val[index])


def menu_tail_to_arg(arg, map_, index):
  return p.implode('/', p.array_slice(map_, index))


#
# This function is similar to menu_translate_() but does link-specific
# preparation such as always calling to_arg functions
#
# @param item
#   A menu link
# @return
#   Returns the map of path arguments with objects loaded as defined in the
#   item['load_functions'].
#   item['access'] becomes True if the item is accessible, False otherwise.
#   item['href'] is generated from link_path, possibly by to_arg functions.
#   item['title'] is generated from link_title, and may be localized.
#   item['options'] is unserialized; it is also changed within the call here
#   to item['localized_options'] by _menu_item_localize().
#
def _menu_link_translate(item):
  p.Reference.check(item)
  item.val['options'] = p.unserialize(item.val['options'])
  if (item.val['external']):
    item.val['access'] = 1
    map_ = {}
    item.val['href'] = item.val['link_path']
    item.val['title'] = item.val['link_title']
    item.val['localized_options'] = item.val['options']
  else:
    map_ = p.explode('/', item.val['link_path'])
    _menu_link_map_translate(map_, item.val['to_arg_functions'])
    item.val['href'] = p.implode('/', map_)
    # Note - skip callbacks without real values for their arguments.
    if (p.strpos(item.val['href'], '%') != False):
      item.val['access'] = False
      return False
    # menu_tree_check_access() may set this ahead of time for links to nodes.
    if (not p.isset(item.val['access'])):
      if (not _menu_load_objects(item.val, map_)):
        # An error occurred loading an object.
        item.val['access'] = False
        return False
      _menu_check_access(item, map)
    _menu_item_localize(item.val, map_, True)
    # For performance, don't localize a link the user can't access.
    if (item.val['access']):
      _menu_item_localize(item.val, map_, True)
  # Allow other customizations - e.g. adding a page-specific query string to the
  # options array. For performance reasons we only invoke this hook if the link
  # has the 'alter' flag set in the options array.
  if (not p.empty(item.val['options']['alter'])):
    drupal_alter('translated_menu_link', item.val, map_)
  return map_



#
# Get a loaded object from a router item.
#
# menu_get_object() will provide you the current node on paths like node/5,
# node/5/revisions/48 etc. menu_get_object('user') will give you the user
# account on user/5 etc. Note - this function should never be called within a
# _to_arg function (like user_current_to_arg()) since this may result in an
# infinite recursion.
#
# @param type
#   Type of the object. These appear in hook_menu definitons as %type. Core
#   provides aggregator_feed, aggregator_category, contact, filter_format,
#   forum_term, menu, menu_link, node, taxonomy_vocabulary, user. See the
#   relevant {type}_load function for more on each. Defaults to node.
# @param position
#   The expected position for type object. For node/%node this is 1, for
#   comment/reply/%node this is 2. Defaults to 1.
# @param path
#   See menu_get_item() for more on this. Defaults to the current path.
#
def menu_get_object(type_ = 'node', position = 1, path = None):
  router_item = menu_get_item(path)
  if (p.isset(router_item['load_functions'], position) and not p.empty(router_item['map'][position]) and router_item['load_functions'][position] == type_ +  '_load'):
    return router_item['map'][position]



#
# Render a menu tree based on the current path.
#
# The tree is expanded based on the current path and dynamic paths are also
# changed according to the defined to_arg functions (for example the 'My account'
# link is changed from user/% to a link with the current user's uid).
#
# @param menu_name
#   The name of the menu.
# @return
#   The rendered HTML of that menu on the current page.
#
def menu_tree(menu_name = 'navigation'):
  p.static(menu_tree, 'menu_output', {})
  if (not p.isset(menu_tree.menu_output, menu_name)):
    tree = menu_tree_page_data(menu_name)
    menu_tree.menu_output[menu_name] = menu_tree_output(tree)
  return menu_tree.menu_output[menu_name]



#
# Returns a rendered menu tree.
#
# @param tree
#   A data structure representing the tree as returned from menu_tree_data.
# @return
#   The rendered HTML of that data structure.
#
def menu_tree_output(tree):
  output = ''
  items = {}
  # Pull out just the menu items we are going to render so that we
  # get an accurate count for the first/last classes.
  for data in tree:
    if (not data['link']['hidden']):
      items.append( data )
  num_items = p.count(items)
  for i,data in items.items():
    extra_class = None
    if (i == 0):
      extra_class = 'first'
    if (i == num_items - 1):
      extra_class = 'last'
    link = theme('menu_item_link', data['link'])
    if (data['below']):
      output += theme('menu_item', link, data['link']['has_children'], menu_tree_output(data['below']), data['link']['in_active_trail'], extra_class)
    else:
      output += theme('menu_item', link, data['link']['has_children'], '', data['link']['in_active_trail'], extra_class)
  return (theme('menu_tree', output) if output else '')



#
# Get the data structure representing a named menu tree.
#
# Since this can be the full tree including hidden items, the data returned
# may be used for generating an an admin interface or a select.
#
# @param menu_name
#   The named menu links to return
# @param item
#   A fully loaded menu link, or None.  If a link is supplied, only the
#   path to root will be included in the returned tree- as if this link
#   represented the current page in a visible menu.
# @return
#   An tree of menu links in an array, in the order they should be rendered.
#
def menu_tree_all_data(menu_name = 'navigation', item = None):
  p.static(menu_tree_all_data, 'tree', {})
  data = None
  # Use mlid as a flag for whether the data being loaded is for the whole tree.
  mlid = (item['mlid'] if p.isset(item, 'mlid') else 0)
  # Generate a cache ID (cid) specific for this menu_name and item.
  cid = 'links:' +  menu_name  + ':all-cid:' + mlid
  if (not p.isset(menu_tree_all_data.tree, cid)):
    # If the static variable doesn't have the data, check {cache_menu}.
    cache = cache_get(cid, 'cache_menu')
    if (cache and p.isset(cache, 'data')):
      # If the cache entry exists, it will just be the cid for the actual data.
      # This avoids duplication of large amounts of data.
      cache = cache_get(cache.data, 'cache_menu')
      if (cache and p.isset(cache, 'data')):
        data = cache.data
    # If the tree data was not in the cache, data will be None.
    if (not p.isset(data)):
      # Build and run the query, and build the tree.
      if (mlid):
        # The tree is for a single item, so we need to match the values in its
        # p columns and 0 (the top level) with the plid values of other links.
        args = [0]
        for i in range(1, MENU_MAX_DEPTH):
          args.append( item["pi"] )
        args = array_unique(args)
        placeholders = p.implode(', ', p.array_fill(0, p.count(args), '%d'))
        where = ' AND ml.plid IN (' +  placeholders  + ')'
        parents = args
        parents.append( item['mlid'] )
      else:
        # Get all links in this menu.
        where = ''
        args = {}
        parents = {}
      array_unshift(args, menu_name)
      # Select the links from the table, and recursively build the tree.  We
      # LEFT JOIN since there is no match in {menu_router} for an external
      # link.
      data['tree'] = menu_tree_data(db_query( \
        "SELECT m.load_functions, m.to_arg_functions, m.access_callback, " + \
        "m.access_arguments, m.page_callback, m.page_arguments, m.title, " + \
        "m.title_callback, m.title_arguments, m.type, m.description, ml.* " + \
        "FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path " + \
        "WHERE ml.menu_name = '%s'" +  where  + \
        "ORDER BY p1 ASC, p2 ASC, p3 ASC, p4 ASC, p5 ASC, p6 ASC, p7 ASC, p8 ASC, " + \
        "p9 ASC", args), parents)
      data['node_links'] = {}
      menu_tree_collect_node_links(data['tree'], data['node_links'])
      # Cache the data, if it is not already in the cache.
      tree_cid = _menu_tree_cid(menu_name, data)
      if (not cache_get(tree_cid, 'cache_menu')):
        cache_set(tree_cid, data, 'cache_menu')
      # Cache the cid of the (shared) data using the menu and item-specific cid.
      cache_set(cid, tree_cid, 'cache_menu')
    # Check access for the current user to each item in the tree.
    menu_tree_check_access(data['tree'], data['node_links'])
    menu_tree_all_data.tree[cid] = data['tree']
  return menu_tree_all_data.tree[cid]



#
# Get the data structure representing a named menu tree, based on the current page.
#
# The tree order is maintained by storing each parent in an individual
# field, see http://drupal.org/node/141866 for more.
#
# @param menu_name
#   The named menu links to return
# @return
#   An array of menu links, in the order they should be rendered. The array
#   is a list of associative arrays -- these have two keys, link and below.
#   link is a menu item, ready for theming as a link. Below represents the
#   submenu below the link if there is one, and it is a subtree that has the
#   same structure described for the top-level array.
#
def menu_tree_page_data(menu_name = 'navigation'):
  p.static(menu_tree_page_data, 'tree', {})
  # Load the menu item corresponding to the current page.
  data = None
  item = menu_get_item()
  if (item):
    # Generate a cache ID (cid) specific for this page.
    cid = 'links:' +  menu_name  + ':page-cid:' + item['href'] + ':' + int(item['access'])
    if (not p.isset(tree, cid)):
      # If the static variable doesn't have the data, check {cache_menu}.
      cache = cache_get(cid, 'cache_menu')
      if (cache and p.isset(cache, 'data')):
        # If the cache entry exists, it will just be the cid for the actual data.
        # This avoids duplication of large amounts of data.
        cache = cache_get(cache.data, 'cache_menu')
        if (cache and p.isset(cache, 'data')):
          data = cache.data
      # If the tree data was not in the cache, data will be None.
      if (not p.isset(data)):
        # Build and run the query, and build the tree.
        if (item['access']):
          # Check whether a menu link exists that corresponds to the current path.
          args = array(menu_name, item['href'])
          placeholders = "'%s'"
          if (drupal_is_front_page()):
            args.append( '<front>' )
            placeholders += ", '%s'"
          parents = db_fetch_array(db_query("SELECT p1, p2, p3, p4, p5, p6, p7, p8 FROM {menu_links} WHERE menu_name = '%s' AND link_path IN (" +  placeholders  + ")", args))
          if (p.empty(parents)):
            # If no link exists, we may be on a local task that's not in the links.
            # TODO: Handle the case like a local task on a specific node in the menu.
            parents = db_fetch_array(db_query("SELECT p1, p2, p3, p4, p5, p6, p7, p8 FROM {menu_links} WHERE menu_name = '%s' AND link_path = '%s'", menu_name, item['tab_root']))
          # We always want all the top-level links with plid == 0.
          parents.append( '0' )
          # Use array_values() so that the indices are numeric for p.array_merge().
          args = parents = array_unique(array_values(parents))
          placeholders = p.implode(', ', p.array_fill(0, p.count(args), '%d'))
          expanded = variable_get('menu_expanded', [])
          # Check whether the current menu has any links set to be expanded.
          if (p.in_array(menu_name, expanded)):
            # Collect all the links set to be expanded, and then add all of
            # their children to the list as well.
            while True:
              result = db_query( \
                "SELECT mlid FROM {menu_links} WHERE menu_name = '%s' " + \
                "AND expanded = 1 AND has_children = 1 AND plid IN (" +  \
                placeholders  + \
                ") AND mlid NOT IN (" + \
                placeholders + \
                ")", p.array_merge(array(menu_name), args, args))
              num_rows = False
              while True:
                item = db_fetch_array(result)
                if not item:
                  break
                args.append( item['mlid'] )
                num_rows = True
              placeholders = p.implode(', ', p.array_fill(0, p.count(args), '%d'))
              if not num_rows:
                break
          array_unshift(args, menu_name)
        else:
          # Show only the top-level menu items when access is denied.
          args = array(menu_name, '0')
          placeholders = '%d'
          parents = {}
        # Select the links from the table, and recursively build the tree. We
        # LEFT JOIN since there is no match in {menu_router} for an external
        # link.
        data['tree'] = menu_tree_data(db_query( \
          "SELECT m.load_functions, m.to_arg_functions, m.access_callback, " + \
          "m.access_arguments, m.page_callback, m.page_arguments, m.title, " + \
          "m.title_callback, m.title_arguments, m.type, m.description, ml.* " + \
          "FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path " + \
          "WHERE ml.menu_name = '%s' AND ml.plid IN (" +  \
          placeholders  + \
          ") ORDER BY p1 ASC, p2 ASC, p3 ASC, p4 ASC, p5 ASC, p6 ASC, p7 ASC, p8 ASC, " + \
          "p9 ASC", args), parents)
        data['node_links'] = {}
        menu_tree_collect_node_links(data['tree'], data['node_links'])
        # Cache the data, if it is not already in the cache.
        tree_cid = _menu_tree_cid(menu_name, data)
        if (not cache_get(tree_cid, 'cache_menu')):
          cache_set(tree_cid, data, 'cache_menu')
        # Cache the cid of the (shared) data using the page-specific cid.
        cache_set(cid, tree_cid, 'cache_menu')
      # Check access for the current user to each item in the tree.
      menu_tree_check_access(data['tree'], data['node_links'])
      menu_tree_page_data.tree[cid] = data['tree']
    return menu_tree_page_data.tree[cid]
  return {}



#
# Helper function - compute the real cache ID for menu tree data.
#
def _menu_tree_cid(menu_name, data):
  return 'links:' +  menu_name  + ':tree-data:' + p.md5(p.serialize(data))



#
# Recursive helper function - collect node links.
#
def menu_tree_collect_node_links(tree, node_links):
  p.Reference.check(tree)
  p.Reference.check(node_links)
  for key,v in tree.val.items():
    if (tree.val[key]['link']['router_path'] == 'node/%'):
      nid = p.substr(tree[key]['link']['link_path'], 5)
      if (p.is_numeric(nid)):
        node_links.val[nid][tree[key]['link']['mlid']] = p.Reference(tree.val[key]['link'])
        tree.val[key]['link']['access'] = False
    if (tree.val[key]['below']):
      menu_tree_collect_node_links(tree[key]['below'], node_links.val)



#
# Check access and perform other dynamic operations for each link in the tree.
#
def menu_tree_check_access(tree, node_links = {}):
  p.Reference.check(tree)
  if (not p.empty(node_links)):
    # Use db_rewrite_sql to evaluate view access without loading each full node.
    nids = p.array_keys(node_links)
    placeholders = '%d' +  str_repeat(', %d', p.count(nids) - 1)
    result = db_query(db_rewrite_sql("SELECT n.nid FROM {node} n WHERE n.status = 1 AND n.nid IN (" +  placeholders  + ")"), nids)
    while True:
      node = db_fetch_array(result)
      if not node:
        break
      nid = node['nid']
      for mlid,link in node_links[nid].items():
        node_links[nid][mlid]['access'] = True
  _menu_tree_check_access(tree.val)
  return



#
# Recursive helper function for menu_tree_check_access()
#
def _menu_tree_check_access(tree):
  p.Reference.check(tree)
  new_tree = {}
  for key,v in tree.val.items():
    item = p.Reference(tree.val[key]['link'])
    _menu_link_translate(item)
    if (item.val['access']):
      if (tree.val[key]['below']):
        _menu_tree_check_access(tree.val[key]['below'])
      # The weights are made a uniform 5 digits by adding 50000 as an offset.
      # After _menu_link_translate(), item['title'] has the localized link title.
      # Adding the mlid to the end of the index insures that it is unique.
      new_tree[(50000 + item['weight']) +  ' '  + item['title'] + ' ' + item['mlid']] = tree.val[key]
  # Sort siblings in the tree based on the weights and localized titles.
  ksort(new_tree)
  tree.val = new_tree



#
# Build the data representing a menu tree.
#
# @param result
#   The database result.
# @param parents
#   An array of the plid values that represent the path from the current page
#   to the root of the menu tree.
# @param depth
#   The depth of the current menu tree.
# @return
#   See menu_tree_page_data for a description of the data structure.
#
def menu_tree_data(result = None, parents = {}, depth = 1):
  tree = _menu_tree_data(result, parents, depth)[1]
  return tree



#
# Recursive helper function to build the data representing a menu tree.
#
# The function is a bit complex because the rendering of an item depends on
# the next menu item. So we are always rendering the element previously
# processed not the current one.
#
def _menu_tree_data(result, parents, depth, previous_element = ''):
  remnant = None
  tree = {}
  while True:
    item = db_fetch_array(result)
    if not item:
      break
    # We need to determine if we're on the path to root so we can later build
    # the correct active trail and breadcrumb.
    item['in_active_trail'] = p.in_array(item['mlid'], parents)
    # The current item is the first in a new submenu.
    if (item['depth'] > depth):
      # _menu_tree returns an item and the menu tree structure.
      item, below = _menu_tree_data(result, parents, item['depth'], item)
      if (previous_element):
        tree[previous_element['mlid']] = {
          'link': previous_element,
          'below': below,
        }
      else:
        tree = below
      # We need to fall back one level.
      if (item == None or item['depth'] < depth):
        return [item, tree]
      # This will be the link to be output in the next iteration.
      previous_element = item
    # We are at the same depth, so we use the previous element.
    elif (item['depth'] == depth):
      if (previous_element):
        # Only the first time.
        tree[previous_element['mlid']] = {
          'link': previous_element,
          'below': False,
        }
      # This will be the link to be output in the next iteration.
      previous_element = item
    # The submenu ended with the previous item, so pass back the current item.
    else:
      remnant = item
      break
  if (previous_element):
    # We have one more link dangling.
    tree[previous_element['mlid']] = {
      'link': previous_element,
      'below': False,
    }
  return [remnant, tree]



#
# Generate the HTML output for a single menu link.
#
# @ingroup themeable
#
def theme_menu_item_link(link):
  if (p.empty(link['localized_options'])):
    link['localized_options'] = {}
  return l(link['title'], link['href'], link['localized_options'])



#
# Generate the HTML output for a menu tree
#
# @ingroup themeable
#
def theme_menu_tree(tree):
  return '<ul class="menu">' +  tree  + '</ul>'



#
# Generate the HTML output for a menu item and submenu.
#
# @ingroup themeable
#
def theme_menu_item(link, has_children, menu = '', in_active_trail = False, extra_class = None):
  class_ = ('expanded' if not p.empty(menu) else ('collapsed' if has_children else 'leaf'))
  if (not p.empty(extra_class)):
    class_ += ' ' +  extra_class
  if (in_active_trail):
    class_ += ' active-trail'
  return '<li class="' + class_  + '">' + link + menu + "</li>\n"



#
# Generate the HTML output for a single local task link.
#
# @ingroup themeable
#
def theme_menu_local_task(link, active = False):
  return '<li ' +  ('class="active" ' if active else '')  + '>' + link + "</li>\n"



#
# Generates elements for the arg array in the help hook.
#
def drupal_help_arg(arg = []):
  # Note - the number of empty elements should be > MENU_MAX_PARTS.
  return arg + ['', '', '', '', '', '', '', '', '', '', '', '']



#
# Returns the help associated with the active menu item.
#
def menu_get_active_help():
  output = ''
  router_path = menu_tab_root_path()
  arg = drupal_help_arg(arg(None))
  empty_arg = drupal_help_arg()
  for name in module_list():
    if (module_hook(name, 'help')):
      # Lookup help for this path.
      help = module_invoke(name, 'help', router_path, arg)
      if (help):
        output += help +  "\n"
      # Add "more help" link on admin pages if the module provides a
      # standalone help page.
      if (arg[0] == "admin" and module_exists('help') and module_invoke(name, \
          'help', 'admin/help#' + arg[2], empty_arg) and help):
        output += theme("more_help_link", url('admin/help/' +  arg[2]))
  return output



#
# Build a list of named menus.
#
def menu_get_names(reset = False):
  p.static(menu_get_names, 'names', [])
  if (reset or p.empty(menu_get_names.names)):
    result = db_query("SELECT DISTINCT(menu_name) FROM {menu_links} ORDER BY menu_name")
    while True:
      name = db_fetch_array(result)
      if name == None:
        break
      menu_get_names.names.append(name['menu_name'])
  return menu_get_names.names



#
# Return an array containing the names of system-defined (default) menus.
#
def menu_list_system_menus():
  return ['navigation', 'primary-links', 'secondary-links']



#
# Return an array of links to be rendered as the Primary links.
#
def menu_primary_links():
  return menu_navigation_links(variable_get('menu_primary_links_source', 'primary-links'))



#
# Return an array of links to be rendered as the Secondary links.
#
def menu_secondary_links():
  # If the secondary menu source is set as the primary menu, we display the
  # second level of the primary menu.
  if (variable_get('menu_secondary_links_source', 'secondary-links') == variable_get('menu_primary_links_source', 'primary-links')):
    return menu_navigation_links(variable_get('menu_primary_links_source', 'primary-links'), 1)
  else:
    return menu_navigation_links(variable_get('menu_secondary_links_source', 'secondary-links'), 0)



#
# Return an array of links for a navigation menu.
#
# @param menu_name
#   The name of the menu.
# @param level
#   Optional, the depth of the menu to be returned.
# @return
#   An array of links of the specified menu and level.
#
def menu_navigation_links(menu_name, level = 0):
  # Don't even bother querying the menu table if no menu is specified.
  if (p.empty(menu_name)):
    return []
  # Get the menu hierarchy for the current page.
  tree = menu_tree_page_data(menu_name)
  # Go down the active trail until the right level is reached.
  while (level > 0 and tree):
    level -= 1
    # Loop through the current level's items until we find one that is in trail.
    while True:
      item = p.array_shift(tree)
      if p.empty(item):
        break
      if (item['link']['in_active_trail']):
        # If the item is in the active trail, we continue in the subtree.
        tree = ([] if p.empty(item['below']) else item['below'])
        break
  # Create a single level of links.
  links = []
  for item in tree:
    if (not item['link']['hidden']):
      l = item['link']['localized_options']
      l['href'] = item['link']['href']
      l['title'] = item['link']['title']
      if (item['link']['in_active_trail']):
        l['attributes'] = {'class' : 'active-trail'}
      # Keyed with unique menu id to generate classes from theme_links().
      links['menu-' +  item['link']['mlid']] = l
  return links



#
# Collects the local tasks (tabs) for a given level.
#
# @param level
#   The level of tasks you ask for. Primary tasks are 0, secondary are 1.
# @param return_root
#   Whether to return the root path for the current page.
# @return
#   Themed output corresponding to the tabs of the requested level, or
#   router path if return_root == True. This router path corresponds to
#   a parent tab, if the current page is a default local task.
#
def menu_local_tasks(level = 0, return_root = False):
  p.static(menu_local_tasks, 'tabs', [])
  p.static(menu_local_tasks, 'root_path')
  if (p.empty(menu_local_tasks.tabs)):
    router_item = menu_get_item()
    if (not router_item or not router_item['access']):
      return ''
    # Get all tabs and the root page.
    result = db_query("SELECT * FROM {menu_router} WHERE tab_root = '%s' ORDER BY weight, title", router_item['tab_root'])
    map_ = arg()
    children = []
    tasks = []
    menu_local_tasks.rootpath = router_item['path']
    while True:
      item = db_fetch_array(result)
      if item == None:
        break
      _menu_translate(item, map_, True)
      if (item['tab_parent']):
        # All tabs, but not the root page.
        children[item['tab_parent']][item['path']] = item
      # Store the translated item for later use.
      tasks[item['path']] = item
    # Find all tabs below the current path.
    path = router_item['path']
    # Tab parenting may skip levels, so the number of parts in the path may not
    # equal the depth. Thus we use the depth counter (offset by 1000 for ksort).
    depth = 1001
    while (p.isset(children, path)):
      tabs_current = ''
      next_path = ''
      count = 0
      for item in children[path]:
        if (item['access']):
          count += 1
          # The default task is always active.
          if (item['type'] == MENU_DEFAULT_LOCAL_TASK):
            # Find the first parent which is not a default local task.
            p = item['tab_parent']
            while True:
              if tasks[p]['type'] != MENU_DEFAULT_LOCAL_TASK:
                break
              p = tasks[p]['tab_parent']
            link = theme('menu_item_link', {'href' : tasks[p]['href']} + item)
            tabs_current += theme('menu_local_task', link, True)
            next_path = item['path']
          else:
            link = theme('menu_item_link', item)
            tabs_current += theme('menu_local_task', link)
      path = next_path
      menu_local_tasks.tabs[depth]['count'] = count
      menu_local_tasks.tabs[depth]['output'] = tabs_current
      depth += 1
    # Find all tabs at the same level or above the current one.
    parent = router_item['tab_parent']
    path = router_item['path']
    current = router_item
    depth = 1000
    while (p.isset(children, parent)):
      tabs_current = ''
      next_path = ''
      next_parent = ''
      count = 0
      for item in children[parent]:
        if (item['access']):
          count += 1
          if (item['type'] == MENU_DEFAULT_LOCAL_TASK):
            # Find the first parent which is not a default local task.
            p = item['tab_parent']
            while True:
              if tasks[p]['type'] != MENU_DEFAULT_LOCAL_TASK:
                break
              p = tasks[p]['tab_parent']
            link = theme('menu_item_link', {'href' : tasks[p]['href']} + item)
            if (item['path'] == router_item['path']):
              menu_local_tasks.root_path = tasks[p]['path']
          else:
            link = theme('menu_item_link', item)
          # We check for the active tab.
          if (item['path'] == path):
            tabs_current += theme('menu_local_task', link, True)
            next_path = item['tab_parent']
            if (p.isset(tasks, next_path)):
              next_parent = tasks[next_path]['tab_parent']
          else:
            tabs_current += theme('menu_local_task', link)
      path = next_path
      parent = next_parent
      menu_local_tasks.tabs[depth]['count'] = count
      menu_local_tasks.tabs[depth]['output'] = tabs_current
      depth -= 1
    # Sort by depth.
    menu_local_tasks.tabs = ksort(menu_local_tasks.tabs)
    # Remove the depth, we are interested only in their relative placement.
    menu_local_tasks.tabs = array_values(menu_local_tasks.tabs.tabs)
  if (return_root):
    return menu_local_tasks.rootpath
  else:
    # We do not display single tabs.
    return (menu_local_tasks.tabs[level]['output'] if (p.isset(menu_local_tasks.tabs, level) and \
      menu_local_tasks.tabs[level]['count'] > 1) else '')



#
# Returns the rendered local tasks at the top level.
#
def menu_primary_local_tasks():
  return menu_local_tasks(0)



#
# Returns the rendered local tasks at the second level.
#
def menu_secondary_local_tasks():
  return menu_local_tasks(1)



#
# Returns the router path, or the path of the parent tab of a default local task.
#
def menu_tab_root_path():
  return menu_local_tasks(0, True)



#
# Returns the rendered local tasks. The default implementation renders them as tabs.
#
# @ingroup themeable
#
def theme_menu_local_tasks():
  output = ''
  primary = menu_primary_local_tasks()
  if (primary):
    output += "<ul class=\"tabs primary\">\n" +  primary  + "</ul>\n"
  secondary = menu_secondary_local_tasks()
  if (secondary):
    output += "<ul class=\"tabs secondary\">\n" +  secondary  + "</ul>\n"
  return output



#
# Set (or get) the active menu for the current page - determines the active trail.
#
def menu_set_active_menu_name(menu_name = None):
  p.static(menu_set_active_menu_name, 'active')
  if (menu_name != None):
    menu_set_active_menu_name.active = menu_name
  elif (menu_set_active_menu_name.active == None):
    menu_set_active_menu_name.active = 'navigation'
  return menu_set_active_menu_name.active



#
# Get the active menu for the current page - determines the active trail.
#
def menu_get_active_menu_name():
  return menu_set_active_menu_name()



#
# Set the active path, which determines which page is loaded.
#
# @param path
#   A Drupal path - not a path alias.
#
# Note that this may not have the desired effect unless invoked very early
# in the page load, such as during hook_boot, or unless you call
# menu_execute_active_handler() to generate your page output.
#
def menu_set_active_item(path):
  p.GET['q'] = path



#
# Set (or get) the active trail for the current page - the path to root in the menu tree.
#
def menu_set_active_trail(new_trail = None):
  p.static(menu_set_active_trail, 'trail')
  if (new_trail != None):
    static_menusetactivetrail_trail = new_trail
  elif (static_menusetactivetrail_trail == None):
    menu_set_active_trail.trail = []
    menu_set_active_trail.trail.append( {'title': t('Home'), 'href': '<front>', 'localized_options': {}, 'type': 0})
    item = menu_get_item()
    # Check whether the current item is a local task (displayed as a tab).
    if (item['tab_parent']):
      # The title of a local task is used for the tab, never the page title.
      # Thus, replace it with the item corresponding to the root path to get
      # the relevant href and title.  For example, the menu item corresponding
      # to 'admin' is used when on the 'By module' tab at 'admin/by-module'.
      parts = p.explode('/', item['tab_root'])
      args = arg()
      # Replace wildcards in the root path using the current path.
      for index,part in parts.items():
        if (part == '%'):
          parts[index] = args[index]
      # Retrieve the menu item using the root path after wildcard replacement.
      root_item = menu_get_item(p.implode('/', parts))
      if (root_item and root_item['access']):
        item = root_item
    tree = menu_tree_page_data(menu_get_active_menu_name())
    key,curr = each(tree)
    while (curr):
      # Terminate the loop when we find the current path in the active trail.
      if (curr['link']['href'] == item['href']):
        menu_set_active_trail.trail.append( curr['link'] )
        curr = False
      else:
        # Move to the child link if it's in the active trail.
        if (curr['below'] and curr['link']['in_active_trail']):
          menu_set_active_trail.trail.append( curr['link'] )
          tree = curr['below']
        key,curr = each(tree)
    # Make sure the current page is in the trail (needed for the page title),
    # but exclude tabs and the front page.
    last = p.count(menu_set_active_trail.trail) - 1
    if (menu_set_active_trail.trail[last]['href'] != item['href'] and not \
        drupy_bool(item['type'] & MENU_IS_LOCAL_TASK) and not drupal_is_front_page()):
      menu_set_active_trail.trail.append( item )
  return menu_set_active_trail.trail



#
# Get the active trail for the current page - the path to root in the menu tree.
#
def menu_get_active_trail():
  return menu_set_active_trail()



#
# Get the breadcrumb for the current page, as determined by the active trail.
#
def menu_get_active_breadcrumb():
  breadcrumb = {}
  # No breadcrumb for the front page.
  if (drupal_is_front_page()):
    return breadcrumb
  item = menu_get_item()
  if (item and item['access']):
    active_trail = menu_get_active_trail()
    for parent in active_trail:
      breadcrumb.append( l(parent['title'], parent['href'], parent['localized_options']) )
    end = end(active_trail)
    # Don't show a link to the current page in the breadcrumb trail.
    if (item['href'] == end['href'] or (item['type'] == MENU_DEFAULT_LOCAL_TASK and end['href'] != '<front>')):
      p.array_pop(breadcrumb)
  return breadcrumb



#
# Get the title of the current page, as determined by the active trail.
#
def menu_get_active_title():
  active_trail = menu_get_active_trail()
  for item in p.array_reverse(active_trail):
    if (not drupy_bool(item['type'] & MENU_IS_LOCAL_TASK)):
      return item['title']



#
# Get a menu link by its mlid, access checked and link translated for rendering.
#
# This function should never be called from within node_load() or any other
# function used as a menu object load function since an infinite recursion may
# occur.
#
# @param mlid
#   The mlid of the menu item.
# @return
#   A menu link, with item['access'] filled and link translated for
#   rendering.
#
def menu_link_load(mlid):
  item = db_fetch_array(db_query("SELECT m.*, ml.* FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path WHERE ml.mlid = %d", mlid))
  if (p.is_numeric(mlid) and item):
    _menu_link_translate(item)
    return item
  return False



#
# Clears the cached cached data for a single named menu.
#
def menu_cache_clear(menu_name = 'navigation'):
  p.static(menu_cache_clear, 'cache_cleared', {})
  if (not p.isset(menu_cache_clear.cache_cleared, menu_name) or \
      p.empty(menu_cache_clear.cache_cleared[menu_name])):
    cache_clear_all('links:' +  menu_name  + ':', 'cache_menu', True)
    menu_cache_clear.cache_cleared[menu_name] = 1
  elif (menu_cache_clear.cache_cleared[menu_name] == 1):
    register_shutdown_function('cache_clear_all', 'links:' +  menu_name  + ':', 'cache_menu', True)
    menu_cache_clear.cache_cleared[menu_name] = 2



#
# Clears all cached menu data.  This should be called any time broad changes
# might have been made to the router items or menu links.
#
def menu_cache_clear_all():
  cache_clear_all('*', 'cache_menu', True)



#
# (Re)populate the database tables used by various menu functions.
#
# This function will clear and populate the {menu_router} table, add entries
# to {menu_links} for new router items, then remove stale items from
# {menu_links}. If called from update.php or install.php, it will also
# schedule a call to itself on the first real page load from
# menu_execute_active_handler(), because the maintenance page environment
# is different and leaves stale data in the menu tables.
#
def menu_rebuild():
  variable_del('menu_rebuild_needed')
  menu_cache_clear_all()
  menu = menu_router_build(True)
  _menu_navigation_links_rebuild(menu)
  # Clear the page and block caches.
  _menu_clear_page_cache()
  if (p.defined('MAINTENANCE_MODE')):
    variable_set('menu_rebuild_needed', True)



#
# Collect, alter and store the menu definitions.
#
def menu_router_build(reset = False):
  p.static(menu_router_build, 'menu')
  if (menu_router_build.menu == None or reset):
    cache = cache_get('router:', 'cache_menu')
    if (not reset and cache and p.isset(cache, 'data')):
      menu_router_build.menu = cache.data
    else:
      db_query('DELETE FROM {menu_router}')
      # We need to manually call each module so that we can know which module
      # a given item came from.
      callbacks = []
      for module in module_implements('menu', None, True):
        router_items = (module+'_menu')()
        if (router_items != None and p.is_array(router_items)):
          for path in p.array_keys(router_items):
            router_items[path]['module'] = module
          callbacks = p.array_merge(callbacks, router_items)
      # Alter the menu as defined in modules, keys are like user/%user.
      drupal_alter('menu', callbacks)
      menu_router_build.menu = _menu_router_build(callbacks)
      cache_set('router:', menu_router_build.menu, 'cache_menu')
  return menu_router_build.menu



#
# Builds a link from a router item.
#
def _menu_link_build(item):
  if (item['type'] == MENU_CALLBACK):
    item['hidden'] = -1
  elif (item['type'] == MENU_SUGGESTED_ITEM):
    item['hidden'] = 1
  # Note, we set this as 'system', so that we can be sure to distinguish all
  # the menu links generated automatically from entries in {menu_router}.
  item['module'] = 'system'
  item += {
    'menu_name' : 'navigation',
    'link_title' : item['title'],
    'link_path' : item['path'],
    'hidden' : 0,
    'options' : ({} if p.empty(item['description']) else {'attributes' : {'title' : item['description']}}),
  }
  return item



#
# Helper function to build menu links for the items in the menu router.
#
def _menu_navigation_links_rebuild(menu):
  # Add normal and suggested items as links.
  menu_links = {}
  for path,item in menu.items():
    if (item['_visible']):
      item = _menu_link_build(item)
      menu_links[path] = item
      sort[path] = item['_number_parts']
  if (menu_links):
    # Make sure no child comes before its parent.
    array_multisort(sort, SORT_NUMERIC, menu_links)
    for item in menu_links:
      existing_item = db_fetch_array(db_query("SELECT mlid, menu_name, plid, customized, has_children, updated FROM {menu_links} WHERE link_path = '%s' AND module = '%s'", item['link_path'], 'system'))
      if (existing_item):
        item['mlid'] = existing_item['mlid']
        item['menu_name'] = existing_item['menu_name']
        item['plid'] = existing_item['plid']
        item['has_children'] = existing_item['has_children']
        item['updated'] = existing_item['updated']
      if (not existing_item or not existing_item['customized']):
        menu_link_save(item)
  placeholders = db_placeholders(menu, 'varchar')
  paths = p.array_keys(menu)
  # Updated and customized items whose router paths are gone need new ones.
  result = db_query("SELECT ml.link_path, ml.mlid, ml.router_path, ml.updated FROM {menu_links} ml WHERE ml.updated = 1 OR (router_path NOT IN (placeholders) AND external = 0 AND customized = 1)", paths)
  while True:
    item = db_fetch_array(result)
    if not item:
      break
    router_path = _menu_find_router_path(menu, item['link_path'])
    if (not p.empty(router_path) and (router_path != item['router_path'] or item['updated'])):
      # If the router path and the link path matches, it's surely a working
      # item, so we clear the updated flag.
      updated = item['updated'] and router_path != item['link_path']
      db_query("UPDATE {menu_links} SET router_path = '%s', updated = %d WHERE mlid = %d", router_path, updated, item['mlid'])
  # Find any item whose router path does not exist any more.
  result = db_query("SELECT * FROM {menu_links} WHERE router_path NOT IN (placeholders) AND external = 0 AND updated = 0 AND customized = 0 ORDER BY depth DESC", paths)
  # Remove all such items. Starting from those with the greatest depth will
  # minimize the amount of re-parenting done by menu_link_delete().
  item = db_fetch_array(result)
  while True:
    if not item:
      break
    _menu_delete_item(item, True)



#
# Delete one or several menu links.
#
# @param mlid
#   A valid menu link mlid or None. If None, path is used.
# @param path
#   The path to the menu items to be deleted. mlid must be None.
#
def menu_link_delete(mlid, path = None):
  if (not p.empty(mlid)):
    _menu_delete_item(db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", mlid)))
  else:
    result = db_query("SELECT * FROM {menu_links} WHERE link_path = '%s'", path)
    while True:
      link = db_fetch_array(result)
      if not link:
        break
      _menu_delete_item(link)



#
# Helper function for menu_link_delete; deletes a single menu link.
#
# @param item
#   Item to be deleted.
# @param force
#   Forces deletion. Internal use only, setting to True is discouraged.
#
def _menu_delete_item(item, force = False):
  if (item and (item['module'] != 'system' or item['updated'] or force)):
    # Children get re-attached to the item's parent.
    if (item['has_children']):
      result = db_query("SELECT mlid FROM {menu_links} WHERE plid = %d", item['mlid'])
      while True:
        m = db_fetch_array(result)
        if not m:
          break
        child = menu_link_load(m['mlid'])
        child['plid'] = item['plid']
        menu_link_save(child)
    db_query('DELETE FROM {menu_links} WHERE mlid = %d', item['mlid'])
    # Update the has_children status of the parent.
    _menu_update_parental_status(item)
    menu_cache_clear(item['menu_name'])
    _menu_clear_page_cache()



#
# Save a menu link.
#
# @param item
#   An array representing a menu link item. The only mandatory keys are
#   link_path and link_title. Possible keys are:
#   - menu_name   default is navigation
#   - weight      default is 0
#   - expanded    whether the item is expanded.
#   - options     An array of options, @see l for more.
#   - mlid        Set to an existing value, or 0 or None to insert a new link.
#   - plid        The mlid of the parent.
#   - router_path The path of the relevant router item.
#
def menu_link_save(item):
  p.Reference.check(item)
  menu = menu_router_build()
  drupal_alter('menu_link', item.val, menu)
  # This is the easiest way to handle the unique internal path '<front>',
  # since a path marked as external does not need to match a router path.
  item.val['_external'] = menu_path_is_external(item.val['link_path'])  or item.val['link_path'] == '<front>'
  # Load defaults.
  item.val += {
    'menu_name': 'navigation',
    'weight': 0,
    'link_title': '',
    'hidden': 0,
    'has_children': 0,
    'expanded': 0,
    'options': array(),
    'module': 'menu',
    'customized': 0,
    'updated': 0,
  }
  existing_item = False
  if (p.isset(item.val, 'mlid')):
    existing_item = db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", item.val['mlid']))
  if (p.isset(item.val, 'plid')):
    parent = db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", item.val['plid']))
  else:
    # Find the parent - it must be unique.
    parent_path = item.val['link_path']
    where = "WHERE link_path = '%s'"
    # Only links derived from router items should have module == 'system', and
    # we want to find the parent even if it's in a different menu.
    if (item.val['module'] == 'system'):
      where += " AND module = '%s'"
      arg2 = 'system'
    else:
      # If not derived from a router item.val, we respect the specified menu name.
      where += " AND menu_name = '%s'"
      arg2 = item.val['menu_name']
    while True:
      parent = False
      parent_path = p.substr(parent_path, 0, strrpos(parent_path, '/'))
      result = db_query("SELECT COUNT(*) FROM {menu_links} " +  where, parent_path, arg2)
      # Only valid if we get a unique result.
      if (db_result(result) == 1):
        parent = db_fetch_array(db_query("SELECT * FROM {menu_links} " +  where, parent_path, arg2))
      if not (parent == False and parent_path):
        break
  if (parent != False):
    item.val['menu_name'] = parent['menu_name']
  menu_name = item.val['menu_name']
  # Menu callbacks need to be in the links table for breadcrumbs, but can't
  # be parents if they are generated directly from a router item.val.
  if (p.empty(parent['mlid']) or parent['hidden'] < 0):
    item.val['plid'] =  0
  else:
    item.val['plid'] = parent['mlid']
  if (not existing_item):
    db_query( \
      "INSERT INTO {menu_links} ( " + \
      "menu_name, plid, link_path, " + \
      "hidden, external, has_children, " + \
      "expanded, weight, " + \
      "module, link_title, options, " + \
      "customized, updated) VALUES ( " + \
      "'%s', %d, '%s', " + \
      "%d, %d, %d, " + \
      "%d, %d,'%s', '%s', '%s', %d, %d)",
      item.val['menu_name'], item.val['plid'], item.val['link_path'],
      item.val['hidden'], item.val['_external'], item.val['has_children'],
      item.val['expanded'], item.val['weight'],
      item.val['module'],  item.val['link_title'], p.serialize(item.val['options']),
      item.val['customized'], item.val['updated'])
    item.val['mlid'] = db_last_insert_id('menu_links', 'mlid')
  if (not item.val['plid']):
    item.val['p1'] = item.val['mlid']
    for i in range(2, MENU_MAX_DEPTH + 1):
      item.val["pi"] = 0
    item.val['depth'] = 1
  else:
    # Cannot add beyond the maximum depth.
    if (item.val['has_children'] and existing_item):
      limit = MENU_MAX_DEPTH - menu_link_children_relative_depth(existing_item) - 1
    else:
      limit = MENU_MAX_DEPTH - 1
    if (parent['depth'] > limit):
      return False
    item.val['depth'] = parent['depth'] + 1
    _menu_link_parents_set(item.val, parent)
  # Need to check both plid and menu_name, since plid can be 0 in any menu.
  if (existing_item and (item.val['plid'] != existing_item['plid'] or menu_name != existing_item['menu_name'])):
    _menu_link_move_children(item.val, existing_item)
  # Find the callback. During the menu update we store empty paths to be
  # fixed later, so we skip this.
  if (not p.isset(_SESSION, 'system_update_6021') and (p.empty(item.val['router_path'])  or \
      not existing_item or (existing_item['link_path'] != item.val['link_path']))):
    if (item.val['_external']):
      item.val['router_path'] = ''
    else:
      # Find the router path which will serve this path.
      item.val['parts'] = p.explode('/', item.val['link_path'], MENU_MAX_PARTS)
      item.val['router_path'] = _menu_find_router_path(menu, item.val['link_path'])
  db_query( \
    "UPDATE {menu_links} SET menu_name = '%s', plid = %d, link_path = '%s', " + \
    "router_path = '%s', hidden = %d, external = %d, has_children = %d, " + \
    "expanded = %d, weight = %d, depth = %d, " + \
    "p1 = %d, p2 = %d, p3 = %d, p4 = %d, p5 = %d, p6 = %d, p7 = %d, p8 = %d, p9 = %d, " + \
    "module = '%s', link_title = '%s', options = '%s', customized = %d WHERE mlid = %d",
    item.val['menu_name'], item.val['plid'], item.val['link_path'],
    item.val['router_path'], item.val['hidden'], item.val['_external'], item.val['has_children'],
    item.val['expanded'], item.val['weight'],  item.val['depth'],
    item.val['p1'], item.val['p2'], item.val['p3'], item.val['p4'], item.val['p5'], item.val['p6'], item.val['p7'], item.val['p8'], item.val['p9'],
    item.val['module'],  item.val['link_title'], p.serialize(item.val['options']), item.val['customized'], item.val['mlid'])
  # Check the has_children status of the parent.
  _menu_update_parental_status(item.val)
  menu_cache_clear(menu_name)
  if (existing_item and menu_name != existing_item['menu_name']):
    menu_cache_clear(existing_item['menu_name'])
  _menu_clear_page_cache()
  return item.val['mlid']



#
# Helper function to clear the page and block caches at most twice per page load.
#
def _menu_clear_page_cache():
  p.static(_menu_clear_page_cache, 'cache_cleared', 0)
  # Clear the page and block caches, but at most twice, including at
  #  the end of the page load when there are multple links saved or deleted.
  if (_menu_clear_page_cache.cache_cleared == 0):
    cache_clear_all()
    # Keep track of which menus have expanded items.
    _menu_set_expanded_menus()
    _menu_clear_page_cache.cache_cleared = 1
  elif (_menu_clear_page_cache.cache_cleared == 1):
    register_shutdown_function('cache_clear_all')
    # Keep track of which menus have expanded items.
    register_shutdown_function('_menu_set_expanded_menus')
    _menu_clear_page_cache.cache_cleared = 2



#
# Helper function to update a list of menus with expanded items
#
def _menu_set_expanded_menus():
  names = []
  result = db_query("SELECT menu_name FROM {menu_links} WHERE expanded != 0 GROUP BY menu_name")
  while True:
    n = db_fetch_array(result)
    if not n:
      break
    names.append( n['menu_name'] )
  variable_set('menu_expanded', names)



#
# Find the router path which will serve this path.
#
# @param menu
#  The full built menu.
# @param link_path
#  The path for we are looking up its router path.
# @return
#  A path from menu keys or empty if link_path points to a nonexisting
#  place.
#
def _menu_find_router_path(menu, link_path):
  parts = p.explode('/', link_path, MENU_MAX_PARTS)
  router_path = link_path
  if (not p.isset(menu, router_path)):
    ancestors = menu_get_ancestors(parts)
    ancestors.append('')
    for key,router_path in ancestors.items():
      if (p.isset(menu, router_path)):
        break
  return router_path



#
# Insert, update or delete an uncustomized menu link related to a module.
#
# @param module
#   The name of the module.
# @param op
#   Operation to perform: insert, update or delete.
# @param link_path
#   The path this link points to.
# @param link_title
#   Title of the link to insert or new title to update the link to.
#   Unused for delete.
# @return
#   The insert op returns the mlid of the new item. Others op return None.
#
def menu_link_maintain(module, op, link_path, link_title):
  if op == 'insert':
    menu_link = {
      'link_title': link_title,
      'link_path': link_path,
      'module': module,
    }
    return menu_link_save(menu_link)
  elif op == 'update':
    db_query("UPDATE {menu_links} SET link_title = '%s' WHERE link_path = '%s' AND customized = 0 AND module = '%s'", link_title, link_path, module)
    menu_cache_clear()
  elif op == 'delete':
    menu_link_delete(None, link_path)



#
# Find the depth of an item's children relative to its depth.
#
# For example, if the item has a depth of 2, and the maximum of any child in
# the menu link tree is 5, the relative depth is 3.
#
# @param item
#   An array representing a menu link item.
# @return
#   The relative depth, or zero.
#
#
def menu_link_children_relative_depth(item):
  i = 1
  match = ''
  args.append( item['menu_name'] )
  p = 'p1'
  while True:
    if not (i <= MENU_MAX_DEPTH and item[p]):
      break
    match += " AND p = %d"
    args.append( item[p] )
    p = 'p' +  ++i
  max_depth = db_result(db_query_range("SELECT depth FROM {menu_links} WHERE menu_name = '%s'" +  match  + " ORDER BY depth DESC", args, 0, 1))
  return ((max_depth - item['depth']) if (max_depth > item['depth']) else 0)



#
# Update the children of a menu link that's being moved.
#
# The menu name, parents (p1 - p6), and depth are updated for all children of
# the link, and the has_children status of the previous parent is updated.
#
def _menu_link_move_children(item, existing_item):
  args.append( item['menu_name'] )
  set.append( "menu_name = '%s'" )
  i = 1
  while True:
    if not (i <= item['depth']):
      break
    p = 'p' + i
    i += 1
    set.append("p = %d")
    args.append( item[p] )
  j = existing_item['depth'] + 1
  while True:
    if not (i <= MENU_MAX_DEPTH and j <= MENU_MAX_DEPTH):
      break
    set.append( 'p' +  i  + ' = p' + j )
    i += 1
    j += 1
  while True:
    if not (i <= MENU_MAX_DEPTH):
      break
    set.append( 'p' +  i  + ' = 0')
    i += 1
  shift = item['depth'] - existing_item['depth']
  if (shift < 0):
    args.append( -shift )
    set.append( 'depth = depth - %d' )
  elif (shift > 0):
    # The order of set must be reversed so the new values don't overwrite the
    # old ones before they can be used because "Single-table UPDATE
    # assignments are generally evaluated from left to right"
    # see: http://dev.mysql.com/doc/refman/5.0/en/update.html
    set = p.array_reverse(set)
    args = p.array_reverse(args)
    args.append( shift )
    set.append( 'depth = depth + %d' )
  where.append( "menu_name = '%s'" )
  args.append( existing_item['menu_name'] )
  p = 'p1'
  i = 1
  while True:
    if not (i <= MENU_MAX_DEPTH and existing_item[p]):
      break
    where.append( "p = %d" )
    args.append( existing_item[p] )
    i += 1
    p = 'p' + i
  db_query("UPDATE {menu_links} SET " +  p.implode(', ', set)  + " WHERE " . p.implode(' AND ', where), args)
  # Check the has_children status of the parent, while excluding this item.
  _menu_update_parental_status(existing_item, True)


#
# Check and update the has_children status for the parent of a link.
#
def _menu_update_parental_status(item, exclude = False):
  # If plid == 0, there is nothing to update.
  if (item['plid']):
    # We may want to exclude the passed link as a possible child.
    where = (" AND mlid != %d" if exclude else '')
    # Check if at least one visible child exists in the table.
    parent_has_children = drupy_bool(db_result(db_query_range("SELECT mlid FROM {menu_links} WHERE menu_name = '%s' AND plid = %d AND hidden = 0" +  where, item['menu_name'], item['plid'], item['mlid'], 0, 1)))
    db_query("UPDATE {menu_links} SET has_children = %d WHERE mlid = %d", parent_has_children, item['plid'])



#
# Helper function that sets the p1..p9 values for a menu link being saved.
#
def _menu_link_parents_set(item, parent):
  p.Reference.check(item)
  i = 1
  while (i < item.val['depth']):
    p = 'p' + i
    i += 1
    item.val[p] = parent[p]
  p = 'p' +  i
  i += 1
  # The parent (p1 - p9) corresponding to the depth always equals the mlid.
  item.val[p] = item.val['mlid']
  while (i <= MENU_MAX_DEPTH):
    p = 'p' + i
    i += 1
    item.val[p] = 0


#
# Helper function to build the router table based on the data from hook_menu.
#
def _menu_router_build(callbacks):
  # First pass: separate callbacks from paths, making paths ready for
  # matching. Calculate fitness, and fill some default values.
  menu = []
  for path,item in callbacks.items():
    load_functions = []
    to_arg_functions = []
    fit = 0
    move = False
    parts = p.explode('/', path, MENU_MAX_PARTS)
    number_parts = p.count(parts)
    # We store the highest index of parts here to save some work in the fit
    # calculation loop.
    slashes = number_parts - 1
    # Extract load and to_arg functions.
    for k,part in parts.items():
      match = False
      if (p.preg_match('/^%([a-z_]*)$/', part, matches)):
        if (p.empty(matches[1])):
          match = True
          load_functions[k] = None
        else:
          if (drupal_function_exists(matches[1] +  '_to_arg')):
            to_arg_functions[k] = matches[1] +  '_to_arg'
            load_functions[k] = None
            match = True
          if (drupal_function_exists(matches[1] +  '_load')):
            function = matches[1] +  '_load'
            # Create an array of arguments that will be passed to the _load
            # function when this menu path is checked, if 'load arguments'
            # exists.
            load_functions[k] = ({function : item['load arguments']} if p.isset(item, 'load arguments') else function)
            match = True
      if (match):
        parts[k] = '%'
      else:
        fit |=  1 << (slashes - k)
    if (fit):
      move = True
    else:
      # If there is no %, it fits maximally.
      fit = (1 << number_parts) - 1
    masks[fit] = 1
    item['load_functions'] = ('' if p.empty(load_functions) else p.serialize(load_functions))
    item['to_arg_functions'] = ('' if p.empty(to_arg_functions) else p.serialize(to_arg_functions))
    item += {
      'title': '',
      'weight': 0,
      'type': MENU_NORMAL_ITEM,
      '_number_parts': number_parts,
      '_parts': parts,
      '_fit': fit,
    }
    item += {
      '_visible' : drupy_bool((item['type'] & MENU_VISIBLE_IN_BREADCRUMB)),
      '_tab' : drupy_bool((item['type'] & MENU_IS_LOCAL_TASK)),
    }
    if (move):
      new_path = p.implode('/', item['_parts'])
      menu[new_path] = item
      sort[new_path] = number_parts
    else:
      menu[path] = item
      sort[path] = number_parts
  array_multisort(sort, SORT_NUMERIC, menu)
  # Apply inheritance rules.
  for path,v in menu.items():
    item = menu[path]
    if (not item['_tab']):
      # Non-tab items.
      item['tab_parent'] = ''
      item['tab_root'] = path
    for i in range(item['_number_parts'] - 1, 0, -1):
      parent_path = p.implode('/', p.array_slice(item['_parts'], 0, i))
      if (p.isset(menu, parent_path)):
        parent = menu[parent_path]
        if (not p.isset(item, 'tab_parent')):
          # Parent stores the parent of the path.
          item['tab_parent'] = parent_path
        if (not p.isset(item, 'tab_root') and not parent['_tab']):
          item['tab_root'] = parent_path
        # If an access callback is not found for a default local task we use
        # the callback from the parent, since we expect them to be identical.
        # In all other cases, the access parameters must be specified.
        if ((item['type'] == MENU_DEFAULT_LOCAL_TASK) and not p.isset(item, 'access callback') and \
            p.isset(parent, 'access callback')):
          item['access callback'] = parent['access callback']
          if (not p.isset(item, 'access arguments') and p.isset(parent, 'access arguments')):
            item['access arguments'] = parent['access arguments']
        # Same for page callbacks.
        if (not p.isset(item, 'page callback') and p.isset(parent, 'page callback')):
          item['page callback'] = parent['page callback']
          if (not p.isset(item, 'page arguments') and p.isset(parent, 'page arguments')):
            item['page arguments'] = parent['page arguments']
    if (not p.isset(item, 'access callback') and p.isset(item, 'access arguments')):
      # Default callback.
      item['access callback'] = 'user_access'
    if (not p.isset(item, 'access callback') or p.empty(item['page callback'])):
      item['access callback'] = 0
    if (is_bool(item['access callback'])):
      item['access callback'] = intval(item['access callback'])
    item += {
      'access arguments': {},
      'access callback': '',
      'page arguments': {},
      'page callback': '',
      'block callback': '',
      'title arguments': {},
      'title callback': 't',
      'description': '',
      'position': '',
      'tab_parent': '',
      'tab_root': path,
      'path': path
    }
    title_arguments = (p.serialize(item['title arguments']) if item['title arguments'] else  '')
    db_query( \
      "INSERT INTO {menu_router} " + \
      "(path, load_functions, to_arg_functions, access_callback, " + \
      "access_arguments, page_callback, page_arguments, fit, " + \
      "number_parts, tab_parent, tab_root, " + \
      "title, title_callback, title_arguments, " + \
      "type, block_callback, description, position, weight) " + \
      "VALUES ('%s', '%s', '%s', '%s', " + \
      "'%s', '%s', '%s', %d, " + \
      "%d, '%s', '%s', " + \
      "'%s', '%s', '%s', " + \
      "%d, '%s', '%s', '%s', %d)",
      path, item['load_functions'], item['to_arg_functions'], item['access callback'],
      p.serialize(item['access arguments']), item['page callback'], p.serialize(item['page arguments']), item['_fit'],
      item['_number_parts'], item['tab_parent'], item['tab_root'],
      item['title'], item['title callback'], title_arguments,
      item['type'], item['block callback'], item['description'], item['position'], item['weight'])
  # Sort the masks so they are in order of descending fit, and store them.
  masks = p.array_keys(masks)
  rsort(masks)
  variable_set('menu_masks', masks)
  return menu



#
# Returns True if a path is external (e.g. http://example.com).
#
def menu_path_is_external(path):
  colonpos = p.strpos(path, ':')
  return (colonpos != False and not p.preg_match('not [/?#]not ', p.substr(path, 0, colonpos)) and \
    filter_xss_bad_protocol(path, False) == check_plain(path))



#
# Checks whether the site is off-line for maintenance.
#
# This function will log the current user out and redirect to front page
# if the current user has no 'administer site configuration' permission.
#
# @return
#   False if the site is not off-line or its the login page or the user has
#     'administer site configuration' permission.
#   True for anonymous users not on the login page if the site is off-line.
#
def _menu_site_is_offline():
  # Check if site is set to off-line mode.
  if (variable_get('site_offline', 0)):
    # Check if the user has administration privileges.
    if (user_access('administer site configuration')):
      # Ensure that the off-line message is displayed only once [allowing for
      # page redirects], and specifically suppress its display on the site
      # maintenance page.
      if (drupal_get_normal_path(p.GET['q']) != 'admin/settings/site-maintenance'):
        drupal_set_message(t('Operating in off-line mode.'), 'status', False)
    else:
      # Anonymous users get a False at the login prompt, True otherwise.
      if (user_is_anonymous()):
        return p.GET['q'] != 'user' and p.GET['q'] != 'user/login'
      # Logged in users are unprivileged here, so they are logged out.
      p.require_once( drupal_get_path('module', 'user') +  '/user.pages.inc' )
      user_logout()
  return False


#
# Validates the path of a menu link being created or edited.
#
# @return
#   True if it is a valid path AND the current user has access permission,
#   False otherwise.
#
def menu_valid_path(form_item):
  global menu_admin
  item = {}
  path = form_item['link_path']
  # We indicate that a menu administrator is running the menu access check.
  menu_admin = True
  if (path == '<front>' or menu_path_is_external(path)):
    item = {'access' : True}
  elif (p.preg_match('/\/\%/', path)):
    # Path is dynamic (ie 'user/%'), so check directly against menu_router table.
    item = db_fetch_array(db_query("SELECT * FROM {menu_router} where path = '%s' ", path))
    if (item):
      item['link_path']  = form_item['link_path']
      item['link_title'] = form_item['link_title']
      item['external']   = False
      item['options'] = ''
      _menu_link_translate(item)
  else:
    item = menu_get_item(path)
  menu_admin = False
  return item and item['access']


#
# @} End of "defgroup menu".
#
