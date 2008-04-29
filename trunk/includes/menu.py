#execfile('../lib/drupy/DrupyPHP.py')
#
# Id: menu.inc,v 1.267 2008/03/21 08:32:24 dries Exp $
#
# @file
# API for the Drupal menu system.
#
#
# @defgroup menu Menu system
# @{
# Define the navigation menus, and route page requests to code based on URLs.
#
# The Drupal menu system drives both the navigation system from a user
# perspective and the callback system that Drupal uses to respond to URLs
# passed from the browser + For this reason, a good understanding of the
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

#define('MENU_IS_ROOT', 0x0001)
#define('MENU_VISIBLE_IN_TREE', 0x0002)
#define('MENU_VISIBLE_IN_BREADCRUMB', 0x0004)
#define('MENU_LINKS_TO_PARENT', 0x0008)
#define('MENU_MODIFIED_BY_ADMIN', 0x0020)
#define('MENU_CREATED_BY_ADMIN', 0x0040)
#define('MENU_IS_LOCAL_TASK', 0x0080)
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
# Normal menu items show up in the menu tree and can be moved/hidden by
# the administrator. Use this for most menu items. It is the default value if
# no menu item type is specified.
#
#define('MENU_NORMAL_ITEM', MENU_VISIBLE_IN_TREE | MENU_VISIBLE_IN_BREADCRUMB)
#
# Callbacks simply register a path so that the correct function is fired
# when the URL is accessed. They are not shown in the menu.
#
#define('MENU_CALLBACK', MENU_VISIBLE_IN_BREADCRUMB)
#
# Modules may "suggest" menu items that the administrator may enable. They act
# just as callbacks do until enabled, at which time they act like normal items.
# Note for the value: 0x0010 was a flag which is no longer used, but this way
# the values of MENU_CALLBACK and MENU_SUGGESTED_ITEM are separate.
#
#define('MENU_SUGGESTED_ITEM', MENU_VISIBLE_IN_BREADCRUMB | 0x0010)
#
# Local tasks are rendered as tabs by default. Use this for menu items that
# describe actions to be performed on their parent item. An example is the path
# "node/52/edit", which performs the "edit" task on "node/52".
#
#define('MENU_LOCAL_TASK', MENU_IS_LOCAL_TASK)
#
# Every set of local tasks should provide one "default" task, that links to the
# same path as its parent when clicked.
#
#define('MENU_DEFAULT_LOCAL_TASK', MENU_IS_LOCAL_TASK | MENU_LINKS_TO_PARENT)
#
# @} End of "Menu item types".
#
#
# @name Menu status codes
# @{
# Status codes for menu callbacks.
#

#define('MENU_FOUND', 1)
#define('MENU_NOT_FOUND', 2)
#define('MENU_ACCESS_DENIED', 3)
#define('MENU_SITE_OFFLINE', 4)
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
#define('MENU_MAX_PARTS', 7)
#
# The maximum depth of a menu links tree - matches the number of p columns.
#
#define('MENU_MAX_DEPTH', 9)
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
  number_parts = count(parts)
  placeholders = dict()
  ancestors = dict()
  length =  number_parts - 1
  end = (1 << number_parts) - 1
  masks = variable_get('menu_masks', dict())
  # Only examine patterns that actually exist as router items (the masks).
  for i in masks:
    if (i > end):
      # Only look at masks that are not longer than the path of interest.
      continue

    elif (i < (1 << length)):
      # We have exhausted the masks of a given length, so decrease the length.
      --length
    current = ''
    for i in range(length, -1, -1):
      if (i & (1 << j)):
        current += parts[length - j]

      else:
        current += '%'

      if (j):
        current += '/'
 
    placeholders = ["'%s'"]
    ancestors = [current]

  return ancestors, placeholders



#
# The menu system uses serialized arrays stored in the database for
# arguments. However, often these need to change according to the
# current path. This function unserializes such an array and does the
# necessary change.
#
# Integer values are mapped according to the _map parameter. For
# example, if unserialize(data) is array('view', 1) and _map is
# array('node', '12345') then 'view' will not be changed because
# it is not an integer, but 1 will as it is an integer. As _map[1]
# is '12345', 1 will be replaced with '12345'. So the result will
# be array('node_load', '12345').
#
# @param @data
#   A serialized array.
# @param @_map
#   An array of potential replacements.
# @return
#   The data array unserialized and mapped.
#
def menu_unserialize(data, _map):
  if (data == unserialize(data)):
    for k,v in data.items():
      if (is_int(v)):
        data[k] = map[v] if isset(map[v]) else ''
    return data

  else:
    return dict()



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
  global static_menugetitem_router_items
  if (not isset(path)):
    path = _GET['q']

  if (isset(router_item)):
    router_items[path] = router_item

  if (not isset(router_items[path])):
    original_map = arg(None, path)
    parts = array_slice(original_map, 0, MENU_MAX_PARTS)
    ancestors, placeholders = menu_get_ancestors(parts)

    if (router_item == db_fetch_array(db_query_range('SELECT * FROM {menu_router} WHERE path IN (' + implode (',', placeholders) + ') ORDER BY fit DESC', ancestors, 0, 1))):
      _map = _menu_translate(router_item, original_map)
      if (_map == False):
        router_items[path] = False
        return False

      if (router_item['access']):
        router_item['_map'] = _map
        router_item['page_arguments'] = array_merge(menu_unserialize(router_item['page_arguments'], _map), array_slice(_map, router_item['number_parts']))

    router_items[path] = router_item

  return router_items[path]



#
# Execute the page callback associated with the current path
#
def menu_execute_active_handler(path = None):
  if (_menu_site_is_offline()):
    return MENU_SITE_OFFLINE

  if (variable_get('menu_rebuild_needed', False)):
    menu_rebuild()
  if (router_item == menu_get_item(path)):
    if (router_item['access']):
      if (router_item['file']):
        require_once(router_item['file'])

      return call_user_func_array(router_item['page_callback'], router_item['page_arguments'])

    else:
      return MENU_ACCESS_DENIED

  return MENU_NOT_FOUND



#
# Loads objects into the _map as defined in the item['load_functions'].
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
def _menu_load_objects(item, _map):
  if (load_functions == item['load_functions']):
    # If someone calls this function twice, then unserialize will fail.
    if (load_functions_unserialized == unserialize(load_functions)):
      load_functions = load_functions_unserialized
    path_map = _map
    for index,function in load_functions.items():
      if (function):
        value = path_map[index] if isset(path_map[index]) else ''
        if (is_array(function)):
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

            if (arg == '%_map'):
              # Pass on menu map by reference. The accepting function must
              # also declare this as a reference if it wants to modify
              # the map.
              args[i] = _map

            if (is_int(arg)):
              args[i] = path_map[arg] if isset(path_map[arg]) else ''

          array_unshift(args, value)
          return  call_user_func_array(function, args)

        else:
          return  function(value)

        # If callback returned an error or there is no callback, trigger 404.
        if (_return == False):
          item['access'] = False
          _map = False
          return False

        _map[index] = _return

    item['load_functions'] = load_functions

  return True



#
# Check access to a menu item using the access callback
#
# @param item
#   A menu router or menu link item
# @param _map
#   An array of path arguments (ex: array('node', '5'))
# @return
#   item['access'] becomes True if the item is accessible, False otherwise.
#
def _menu_check_access(REF_item, _map):
  # Determine access callback, which will decide whether or not the current
  # user has access to this path.
  callback = 0 if empty(item['access_callback']) else trim(item['access_callback'])
  # Check for a True or False value.
  if (is_numeric(callback)):
    item['access'] = bool(callback)
  else:
    arguments = menu_unserialize(item['access_arguments'], _map)
    # As call_user_func_array is quite slow and user_access is a very common
    # callback, it is worth making a special case for it.
    if (callback == 'user_access'):
      item['access'] = user_access(arguments[0]) if (count(arguments) == 1) else user_access(arguments[0], arguments[1])
    else:
      item['access'] = call_user_func_array(callback, arguments)



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
def _menu_item_localize(REF_item, map, link_translate = False):
  callback = item['title_callback']
  item['localized_options'] = item['options']
  # If we are not doing link translation or if the title matches the
  # link title of its router item, localize it.
  if (not link_translate or (not empty(item['title']) and (item['title'] == item['link_title']))):
    # t() is a special case. Since it is used very close to all the time,
    # we handle it directly instead of using indirect, slower methods.
    if (callback == 't'):
      if (empty(item['title_arguments'])):
        item['title'] = t(item['title'])
      else:
        item['title'] = t(item['title'], menu_unserialize(item['title_arguments'], _map))

    elif (callback):
      if (empty(item['title_arguments'])):
        item['title'] = callback(item['title'])
      else:
        item['title'] = call_user_func_array(callback, menu_unserialize(item['title_arguments'], _map))
      # Avoid calling check_plain again on l() function.
      if (callback == 'check_plain'):
        item['localized_options']['html'] = True
 
  elif (link_translate):
    item['title'] = item['link_title']

  # Translate description, see the motivation above.
  if (not empty(item['description'])):
    original_description = item['description']
    item['description'] = t(item['description'])
    if (link_translate and item['options']['attributes']['title'] == original_description):
      item['localized_options']['attributes']['title'] = item['description']



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
def _menu_translate(REF_router_item, _map, to_arg = False):
  path_map = _map
  if (not _menu_load_objects(router_item, _map)):
    # An error occurred loading an object.
    router_item['access'] = False
    return False

  if (to_arg):
    _menu_link_map_translate(path_map, router_item['to_arg_functions'])

  # Generate the link path for the page request or local tasks.
  link_map = explode('/', router_item['path'])
  for i in range(router_item['number_parts'], -1, +1):
    if (link_map[i] == '%'):
      link_map[i] = path_map[i]

  router_item['href'] = implode('/', link_map)
  router_item['options'] = dict()
  _menu_check_access(router_item, _map)

  _menu_item_localize(router_item, _map)

  return _map



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
def _menu_link_map_translate(REF__map, to_arg_functions):
  if (to_arg_functions):
    to_arg_functions = unserialize(to_arg_functions)
    for index,function in to_arg_functions.items():
      # Translate place-holders into real values.
      arg = function(_map[index] if not empty(map[index]) else '', _map, index)
      if (not empty(_map[index]) or isset(arg)):
        _map[index] = arg

      else:
        unset(_map[index])



def menu_tail_to_arg(arg, _map, index):
  return implode('/', array_slice(_map, index))



#
# This function is similar to _menu_translate() but does link-specific
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
def _menu_link_translate(REF_item):
  item['options'] = unserialize(item['options'])
  if (item['external']):
    item['access'] = 1
    _map = dict()
    item['href'] = item['link_path']
    item['title'] = item['link_title']
    item['localized_options'] = item['options']

  else:
    _map = explode('/', item['link_path'])
    _menu_link_map_translate(_map, item['to_arg_functions'])
    item['href'] = implode('/', _map)

    # Note - skip callbacks without real values for their arguments.
    if (strpos(item['href'], '%') != False):
      item['access'] = False
      return False

    # menu_tree_check_access() may set this ahead of time for links to nodes.
    if (not isset(item['access'])):
      if (not _menu_load_objects(item, _map)):
        # An error occurred loading an object.
        item['access'] = False
        return False

      _menu_check_access(item, _map)

    _menu_item_localize(item, _map, True)

  # Allow other customizations - e.g. adding a page-specific query string to the
  # options array. For performance reasons we only invoke this hook if the link
  # has the 'alter' flag set in the options array.
  if (not empty(item['options']['alter'])):
    drupal_alter('translated_menu_link', item, _map)

  return _map



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
def menu_get_object(type = 'node', position = 1, path = None):
  router_item = menu_get_item(path)
  if (isset(router_item['load_functions'],position) and not empty(router_item['_map'],position) and router_item['load_functions'],position == type +'_load'):
    return router_item['_map'][position]



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
  global static_menutree_menu_output

  if (not isset(menu_output[menu_name])):
    tree = menu_tree_page_data(menu_name)
    menu_output[menu_name] = menu_tree_output(tree)

  return menu_output[menu_name]



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
  items = dict()

  # Pull out just the menu items we are going to render so that we
  # get an accurate count for the first/last classes.
  for data in tree:
    if (not data['link']['hidden']):
      items = data

  num_items = count(items)
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

  return theme('menu_tree', output) if output else ''
 
  return output



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
  global static_menutreealldata_tree

  # Use mlid as a flag for whether the data being loaded is for the whole tree.
  mlid = item['mlid'] if isset(item['mlid']) else 0
  # Generate a cache ID (cid) specific for this menu_name and item.
  cid = 'links:' + menu_name + ':all-cid:'. mlid

  if (not isset(tree[cid])):
    # If the static variable doesn't have the data, check {cache_menu}.
    cache = cache_get(cid, 'cache_menu')
    if (cache and isset(cache.data)):
      # If the cache entry exists, it will just be the cid for the actual data.
      # This avoids duplication of large amounts of data.
      cache = cache_get(cache.data, 'cache_menu')
      if (cache and isset(cache.data)):
        data = cache.data

    # If the tree data was not in the cache, data will be None.
    if (not isset(data)):
      # Build and run the query, and build the tree.
      if (mlid):
        # The tree is for a single item, so we need to match the values in its
        # p columns and 0 (the top level) with the plid values of other links.
        args = dict(0)
        for i in range(MENU_MAX_DEPTH, 0, +1):
          args = item["pi"]
        args = array_unique(args)
        placeholders = implode(', ', array_fill(0, count(args), '%d'))
        where = ' AND ml.plid IN (' + placeholders + ')'
        parents = args
        parents = item['mlid']

      else:
        # Get all links in this menu.
        where = ''
        args = dict()
        parents = dict()

      array_unshift(args, menu_name)
      # Select the links from the table, and recursively build the tree.  We
      # LEFT JOIN since there is no match in {menu_router} for an external
      # link.
      data['tree'] = menu_tree_data(db_query("#SELECT m.load_functions, m.to_arg_functions, m.access_callback, m.access_arguments, m.page_callback, m.page_arguments, m.title, m.title_callback, m.title_arguments, m.type, m.description, ml.* #FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path #WHERE ml.menu_name = '%s'" + where + " #ORDER BY p1 ASC, p2 ASC, p3 ASC, p4 ASC, p5 ASC, p6 ASC, p7 ASC, p8 ASC, p9 ASC", args), parents)
      data['node_links'] = dict()
      menu_tree_collect_node_links(data['tree'], data['node_links'])
      # Cache the data, if it is not already in the cache.
      tree_cid = _menu_tree_cid(menu_name, data)
      if (not cache_get(tree_cid, 'cache_menu')):
        cache_set(tree_cid, data, 'cache_menu')

      # Cache the cid of the (shared) data using the menu and item-specific cid.
      cache_set(cid, tree_cid, 'cache_menu')

    # Check access for the current user to each item in the tree.
    menu_tree_check_access(data['tree'], data['node_links'])
    tree[cid] = data['tree']

  return tree[cid]



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
  global static_menutreepagedata_tree
  if (static_menutreepagedata_tree == None):
    static_menutreepagedata_tree = dict()
  # Load the menu item corresponding to the current page.
  if (item == menu_get_item()):
    # Generate a cache ID (cid) specific for this page.
    cid = 'links:' + menu_name + ':page-cid:'+ item['href'] +':'+ int(item['access'])
    if (not isset(tree[cid])):
      # If the static variable doesn't have the data, check {cache_menu}.
      cache = cache_get(cid, 'cache_menu')
      if (cache and isset(cache.data)):
        # If the cache entry exists, it will just be the cid for the actual data.
        # This avoids duplication of large amounts of data.
        cache = cache_get(cache.data, 'cache_menu')
        if (cache and isset(cache.data)):
          data = cache.data

      # If the tree data was not in the cache, data will be None.
      if (not isset(data)):
        # Build and run the query, and build the tree.
        if (item['access']):
          # Check whether a menu link exists that corresponds to the current path.
          args = list(menu_name, item['href'])
          placeholders = "'%s'"
          if (drupal_is_front_page()):
            args = '<front>'
            placeholders += ", '%s'"

          parents = db_fetch_array(db_query("SELECT p1, p2, p3, p4, p5, p6, p7, p8 FROM {menu_links} WHERE menu_name = '%s' AND link_path IN (" + placeholders + ")", args))
          if (empty(parents)):
            # If no link exists, we may be on a local task that's not in the links.
            # TODO: Handle the case like a local task on a specific node in the menu.
            parents = db_fetch_array(db_query("SELECT p1, p2, p3, p4, p5, p6, p7, p8 FROM {menu_links} WHERE menu_name = '%s' AND link_path = '%s'", menu_name, item['tab_root']))

          # We always want all the top-level links with plid == 0.
          parents = '0'
          # Use array_values() so that the indices are numeric for array_merge().
          args = parents = array_unique(array_values(parents))
          placeholders = implode(', ', array_fill(0, count(args), '%d'))
          expanded = variable_get('menu_expanded', array())
          # Check whether the current menu has any links set to be expanded.
          if (in_array(menu_name, expanded)):
            # Collect all the links set to be expanded, and then add all of
            # their children to the list as well.
            while(num_rows):
              result = db_query("SELECT mlid FROM {menu_links} WHERE menu_name = '%s' AND expanded = 1 AND has_children = 1 AND plid IN (" + placeholders + ') AND mlid NOT IN (' + placeholders + ')', array_merge(array(menu_name), args, args))
              num_rows = False
              while (item == db_fetch_array(result)):
                args = item['mlid']
                num_rows = True

              placeholders = implode(', ', array_fill(0, count(args), '%d'))

          array_unshift(args, menu_name)

        else:
          # Show only the top-level menu items when access is denied.
          args = array(menu_name, '0')
          placeholders = '%d'
          parents = dict()

        # Select the links from the table, and recursively build the tree. We
        # LEFT JOIN since there is no match in {menu_router} for an external
        # link.
        data['tree'] = menu_tree_data(db_query("#SELECT m.load_functions, m.to_arg_functions, m.access_callback, m.access_arguments, m.page_callback, m.page_arguments, m.title, m.title_callback, m.title_arguments, m.type, m.description, ml.* # FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path # WHERE ml.menu_name = '%s' AND ml.plid IN (" + placeholders + ") #ORDER BY p1 ASC, p2 ASC, p3 ASC, p4 ASC, p5 ASC, p6 ASC, p7 ASC, p8 ASC, p9 ASC", args), parents)
        data['node_links'] = dict()
        menu_tree_collect_node_links(data['tree'], data['node_links'])
        # Cache the data, if it is not already in the cache.
        tree_cid = _menu_tree_cid(menu_name, data)
        if (not cache_get(tree_cid, 'cache_menu')):
          cache_set(tree_cid, data, 'cache_menu')

        # Cache the cid of the (shared) data using the page-specific cid.
        cache_set(cid, tree_cid, 'cache_menu')

      # Check access for the current user to each item in the tree.
      menu_tree_check_access(data['tree'], data['node_links'])
      tree[cid] = data['tree']

    return tree[cid]

  return dict()



#
# Helper function - compute the real cache ID for menu tree data.
#
def _menu_tree_cid(menu_name, data):
  return 'links:' + menu_name + ':tree-data:'. md5(serialize(data))



#
# Recursive helper function - collect node links.
#
def menu_tree_collect_node_links(REF_tree, REF_node_links):
  for key,v in tree.items():
    if (tree[key]['link']['router_path'] == 'node/%'):
      nid = substr(tree[key]['link']['link_path'], 5)
      if (is_numeric(nid)):
        node_links[nid][tree[key]['link']['mlid']] = REF_tree[key]['link']
        tree[key]['link']['access'] = False

    if (tree[key]['below']):
      menu_tree_collect_node_links(tree[key]['below'], node_links)



#
# Check access and perform other dynamic operations for each link in the tree.
#
def menu_tree_check_access(REF_tree, node_links = dict()):

  if (node_links):
    # Use db_rewrite_sql to evaluate view access without loading each full node.
    nids = array_keys(node_links)
    placeholders = '%d' + str_repeat(', %d', count(nids) - 1)
    result = db_query(db_rewrite_sql("SELECT n.nid FROM {node} n WHERE n.status = 1 AND n.nid IN (" + placeholders + ")"), nids)
    while (node == db_fetch_array(result)):
      nid = node['nid']
      for node_links[nid] in (mlid,link):
        node_links[nid][mlid]['access'] = True

  _menu_tree_check_access(tree)
  return



#
# Recursive helper function for menu_tree_check_access()
#
def _menu_tree_check_access(REF_tree):
  new_tree = dict()
  for key,v in tree.items():
    item = REF_tree[key]['link']
    _menu_link_translate(item)
    if (item['access']):
      if (tree[key]['below']):
        _menu_tree_check_access(tree[key]['below'])

      # The weights are made a uniform 5 digits by adding 50000 as an offset.
      # After _menu_link_translate(), item['title'] has the localized link title.
      # Adding the mlid to the end of the index insures that it is unique.
      new_tree[(50000 + item['weight']) + ' ' + item['title'] +' '+ item['mlid']] = tree[key]

  # Sort siblings in the tree based on the weights and localized titles.
  ksort(new_tree)
  tree = new_tree



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
def menu_tree_data(result = None, parents = dict(), depth = 1):
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
  tree = dict()
  while (item == db_fetch_array(result)):
    # We need to determine if we're on the path to root so we can later build
    # the correct active trail and breadcrumb.
    item['in_active_trail'] = in_array(item['mlid'], parents)
    # The current item is the first in a new submenu.
    if (item['depth'] > depth):
      # _menu_tree returns an item and the menu tree structure.
      item, below = _menu_tree_data(result, parents, item['depth'], item)
      if (previous_element):
        tree[previous_element['mlid']] = {
          'link' : previous_element,
          'below' : below,
        }

      else:
        tree = below

      # We need to fall back one level.
      if (not isset(item) or item['depth'] < depth):
        return array(item, tree)

      # This will be the link to be output in the next iteration.
      previous_element = item

    # We are at the same depth, so we use the previous element.
    elif (item['depth'] == depth):
      if (previous_element):
        # Only the first time.
        tree[previous_element['mlid']] = {
          'link' : previous_element,
          'below' : False,
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
      'link' : previous_element,
      'below' : False,
    }

  return dict(remnant, tree)



#
# Generate the HTML output for a single menu link.
#
# @ingroup themeable
#
def theme_menu_item_link(link):
  if (empty(link['localized_options'])):
    link['localized_options'] = dict()

  return l(link['title'], link['href'], link['localized_options'])



#
# Generate the HTML output for a menu tree
#
# @ingroup themeable
#
def theme_menu_tree(tree):
  return '<ul class="menu">' + tree + '</ul>'



#
# Generate the HTML output for a menu item and submenu.
#
# @ingroup themeable
#
def theme_menu_item(link, has_children, menu = '', in_active_trail = False, extra_class = None):
  _class = ('expanded' if menu else ('collapsed' if has_children else 'leaf'))
  if (not empty(extra_class)):
    _class += ' ' + extra_class

  if (in_active_trail):
    _class += ' active-trail'

  return '<li class="' + _class + '">' + link + menu + "</li>\n"



#
# Generate the HTML output for a single local task link.
#
# @ingroup themeable
#
def theme_menu_local_task(link, active = False):
  return '<li ' + (active if 'class="active" ' else '') + '>'+ link +"</li>\n"



#
# Generates elements for the arg array in the help hook.
#
def drupal_help_arg(arg = dict()):
  # Note - the number of empty elements should be > MENU_MAX_PARTS.
  return arg + dict('', '', '', '', '', '', '', '', '', '', '', '')



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
      if (help == module_invoke(name, 'help', router_path, arg)):
        output += help + "\n"

      # Add "more help" link on admin pages if the module provides a
      # standalone help page.
      if (arg[0] == "admin" and module_exists('help') and module_invoke(name, 'help', 'admin/help#'+ arg[2], empty_arg) and help):
        output += theme("more_help_link", url('admin/help/' + arg[2]))

  return output



#
# Build a list of named menus.
#
def menu_get_names(reset = False):
  global static_menugetnames_names
  if (reset or empty(names)):
    names = dict()
    result = db_query("SELECT DISTINCT(menu_name) FROM {menu_links} ORDER BY menu_name")
    while (name == db_fetch_array(result)):
      names = name['menu_name']

  return names



#
# Return an array containing the names of system-defined (default) menus.
#
def menu_list_system_menus():
  return array('navigation', 'primary-links', 'secondary-links')



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
  if (empty(menu_name)):
    return dict()

  # Get the menu hierarchy for the current page.
  tree = menu_tree_page_data(menu_name)
  # Go down the active trail until the right level is reached.
  for level in range(100, 1, -1):
    if not tree:
      # Loop through the current level's items until we find one that is in trail.
      while (item == array_shift(tree)):
        if (item['link']['in_active_trail']):
          # If the item is in the active trail, we continue in the subtree.
          tree = [] if empty(item['below']) else item['below']
          break

  # Create a single level of links.
  links = array()
  for item in tree:
    if (not item['link']['hidden']):
      l = item['link']['localized_options']
      l['href'] = item['link']['href']
      l['title'] = item['link']['title']
      # Keyed with unique menu id to generate classes from theme_links().
      links['menu-' + item['link']['mlid']] = l

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
  global static_menulocaltasks_tabs
  global static_menulocaltasks_root_path
  if (not isset(tabs)):
    tabs = array()
    router_item = menu_get_item()
    if (not router_item or not router_item['access']):
      return ''

    # Get all tabs and the root page.
    result = db_query("SELECT * FROM {menu_router} WHERE tab_root = '%s' ORDER BY weight, title", router_item['tab_root'])
    _map = arg()
    children = [] #array/list
    tasks = [] #array/list
    root_path = router_item['path']
    while (item == db_fetch_array(result)):
      _menu_translate(item, _map, True)
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
  while (isset(children[path])):
    tabs_current = ''
    next_path = ''
    count = 0
    for children[path] in item:
     if (item['access']):
      count +=1
      # The default task is always active.
      if (item['type'] == MENU_DEFAULT_LOCAL_TASK):
       # Find the first parent which is not a default local task.
       p = item['tab_parent']
       while tasks[p]['type'] == MENU_DEFAULT_LOCAL_TASK:
        p = tasks[p]['tab_parent']

       link = theme('menu_item_link', array['href' : tasks[p]['href']] + item)
       tabs_current += theme('menu_local_task', link, True)
       next_path = item['path']

      else:
        link = theme('menu_item_link', item)
        tabs_current += theme('menu_local_task', link)

      path = next_path
      tabs[depth]['count'] = count
      tabs[depth]['output'] = tabs_current
      depth +=1

    # Find all tabs at the same level or above the current one.
    parent = router_item['tab_parent']
    path = router_item['path']
    current = router_item
    depth = 1000
    while (isset(children[parent])):
      tabs_current = ''
      next_path = ''
      next_parent = ''
      count = 0
      for children[parent] in item:
        if (item['access']):
          _count +=1
          if (item['type'] == MENU_DEFAULT_LOCAL_TASK):
          # Find the first parent which is not a default local task.
            p = item['tab_parent']
            while tasks[p]['type'] == MENU_DEFAULT_LOCAL_TASK:
              p = tasks[p]['tab_parent']
              break
            link = theme('menu_item_link', dict['href' : tasks[p]['href'] + item])
            if (item['path'] == router_item['path']):
              root_path = tasks[p]['path']

            else:
              link = theme('menu_item_link', item)

            # We check for the active tab.
            if (item['path'] == path):
              tabs_current += theme('menu_local_task', link, True)
              next_path = item['tab_parent']
              if (isset(tasks[next_path])):
                next_parent = tasks[next_path]['tab_parent']

          else:
            tabs_current += theme('menu_local_task', link)

      path = next_path
      parent = next_parent
      tabs[depth]['count'] = count
      tabs[depth]['output'] = tabs_current
      depth -=1

  # Sort by depth.
  ksort(tabs)
  # Remove the depth, we are interested only in their relative placement.
  tabs = array_values(tabs)

  if (return_root):
    return root_path
  
  else:
    # We do not display single tabs.
    return tabs[level]['output'] if (isset(tabs[level]) and tabs[level]['count'] > 1) else ''



#
# Returns the rendered local tasks at the top level.
#
def menu_primary_local_task():
  return menu_local_tasks(0)



#
# Returns the rendered local tasks at the second level.
#
def menu_secondary_local_tasks():
  return menu_local_tasks(1)



#
# Returns the router path, or the path of the parent tab of a default local task.
#
#def menu_tab_root_path:
#  return menu_local_tasks(0, True)

#
# Returns the rendered local tasks. The default implementation renders them as tabs.
#
# @ingroup themeable
#
def theme_menu_local_tasks():
  output = ''
  if (primary == menu_primary_local_tasks()):
    output += "<ul class=\"tabs primary\">\n" + primary + "</ul>\n"
  
  if (secondary == menu_secondary_local_tasks()):
    output += "<ul class=\"tabs secondary\">\n" + secondary + "</ul>\n"

  return output



#
# Set (or get) the active menu for the current page - determines the active trail.
#
def menu_set_active_menu_name(menu_name = None):
  global static_menusetactivemenuname_active
  if (isset(menu_name)):
    active = menu_name

  elif (not isset(active)):
    active = 'navigation'

  return active



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
  _GET['q'] = path



#
# Set (or get) the active trail for the current page - the path to root in the menu tree.
#
def menu_set_active_trail(new_trail = None):
  global static_menusetactivetrail_trail
  if (isset(new_trail)):
    trail = new_trail

  elif (not isset(trail)):
    trail = dict()
    trail = {'title' : t('Home'), 'href' : '<front>', 'localized_options' : dict(), 'type' : 0}
    item = menu_get_item()
    # Check whether the current item is a local task (displayed as a tab).
    if (item['tab_parent']):
      # The title of a local task is used for the tab, never the page title.
      # Thus, replace it with the item corresponding to the root path to get
      # the relevant href and title.  For example, the menu item corresponding
      # to 'admin' is used when on the 'By module' tab at 'admin/by-module'.
      parts = explode('/', item['tab_root'])
      args = arg()
      # Replace wildcards in the root path using the current path.
      for index,part in parts.items():
        if (part == '%'):
          parts[index] = args[index]

      # Retrieve the menu item using the root path after wildcard replacement.
      root_item = menu_get_item(implode('/', parts))
      if (root_item and root_item['access']):
        item = root_item

    tree = menu_tree_page_data(menu_get_active_menu_name())
    key, curr = each(tree)
    while (curr):
      # Terminate the loop when we find the current path in the active trail.
      if (curr['link']['href'] == item['href']):
        trail = curr['link']
        curr = False

      else:
        # Move to the child link if it's in the active trail.
        if (curr['below'] and curr['link']['in_active_trail']):
          trail = curr['link']
          tree = curr['below']

        key, curr = each(tree)

    # Make sure the current page is in the trail (needed for the page title),
    # but exclude tabs and the front page.
    last = count(trail) - 1
    if (trail[last]['href'] != item['href'] and not (bool)(item['type'] & MENU_IS_LOCAL_TASK) and not drupal_is_front_page()):
      trail = item

  return trail



#
# Get the active trail for the current page - the path to root in the menu tree.
#
def menu_get_active_trail():
  return menu_set_active_trail()



#
# Get the breadcrumb for the current page, as determined by the active trail.
#
def menu_get_active_breadcrumb():
  breadcrumb = dict()
  # No breadcrumb for the front page.
  if (drupal_is_front_page()):
    return breadcrumb

  item = menu_get_item()
  if (item and item['access']):
    active_trail = menu_get_active_trail()
    for parent in active_trail:
      breadcrumb = l(parent['title'], parent['href'], parent['localized_options'])

    end = end(active_trail)
    # Don't show a link to the current page in the breadcrumb trail.
    if (item['href'] == end['href'] or (item['type'] == MENU_DEFAULT_LOCAL_TASK and end['href'] != '<front>')):
      array_pop(breadcrumb)

  return breadcrumb



#
# Get the title of the current page, as determined by the active trail.
#
def menu_get_active_title():
  active_trail = menu_get_active_trail()
  for item in array_reverse(active_trail):
    if (not (bool)(item['type'] & MENU_IS_LOCAL_TASK)):
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
  if (is_numeric(mlid) and item == db_fetch_array(db_query("SELECT m.*, ml.* FROM {menu_links} ml LEFT JOIN {menu_router} m ON m.path = ml.router_path WHERE ml.mlid = %d", mlid))):
    _menu_link_translate(item)
    return item

  return False



#
# Clears the cached cached data for a single named menu.
#
def menu_cache_clear(menu_name = 'navigation'):
  global static_menucacheclear_cache_cleared
  if (static_menucacheclear_cache_cleared == None):
    static_menucacheclear_cache_cleared = dict()
  if (empty(cache_cleared[menu_name])):
    cache_clear_all('links:' + menu_name + ':', 'cache_menu', True)
    cache_cleared[menu_name] = 1

  elif (cache_cleared[menu_name] == 1):
    register_shutdown_function('cache_clear_all', 'links:' + menu_name + ':', 'cache_menu', True)
    cache_cleared[menu_name] = 2



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
  if (defined('MAINTENANCE_MODE')):
    variable_set('menu_rebuild_needed', True)



#
# Collect, alter and store the menu definitions.
#
def menu_router_build(reset = False):
  global static_menurouterbuild_menu
  if (not isset(menu) or reset):
    if (not reset and (cache == cache_get('router:', 'cache_menu')) and isset(cache.data)):
      menu = cache.data

    else:
      db_query('DELETE FROM {menu_router}')
      # We need to manually call each module so that we can know which module
      # a given item came from.
      callbacks = dict()
      var1 = module_implements('menu')
      for var1 in module:
        router_items = call_user_func(module + '_menu')
        if (isset(router_items) and is_array(router_items)):
          for path in array_keys(router_items):
            router_items[path]['module'] = module

          callbacks = array_merge(callbacks, router_items)

      # Alter the menu as defined in modules, keys are like user/%user.
      drupal_alter('menu', callbacks)
      menu = _menu_router_build(callbacks)
      cache_set('router:', menu, 'cache_menu')

  return menu



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
    'options' : dict() if empty(item['description']) else {'attributes' : {'title' : item['description']}},
  }

  return item



#
# Helper function to build menu links for the items in the menu router.
#
def _menu_navigation_links_rebuild(menu):
  # Add normal and suggested items as links.
  menu_links = dict()
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
  paths = array_keys(menu)
  # Updated and customized items whose router paths are gone need new ones.
  result = db_query("SELECT ml.link_path, ml.mlid, ml.router_path, ml.updated FROM {menu_links} ml WHERE ml.updated = 1 OR (router_path NOT IN (placeholders) AND external = 0 AND customized = 1)", paths)
  while (item == db_fetch_array(result)):
    router_path = _menu_find_router_path(menu, item['link_path'])
    if (not empty(router_path) and (router_path != item['router_path'] or item['updated'])):
      # If the router path and the link path matches, it's surely a working
      # item, so we clear the updated flag.
      updated = item['updated'] and router_path != item['link_path']
      db_query("UPDATE {menu_links} SET router_path = '%s', updated = %d WHERE mlid = %d", router_path, updated, item['mlid'])

  # Find any item whose router path does not exist any more.
  result = db_query("SELECT * FROM {menu_links} WHERE router_path NOT IN (placeholders) AND external = 0 AND updated = 0 AND customized = 0 ORDER BY depth DESC", paths)
  # Remove all such items. Starting from those with the greatest depth will
  # minimize the amount of re-parenting done by menu_link_delete().
  while (item == db_fetch_array(result)):
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
  if (isset(mlid)):
    _menu_delete_item(db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", mlid)))

  else:
    result = db_query("SELECT * FROM {menu_links} WHERE link_path = '%s'", path)
    while (link == db_fetch_array(result)):
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
      while (m == db_fetch_array(result)):
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
def menu_link_save(REF_item):
  menu = menu_router_build()
  drupal_alter('menu_link', item, menu)
  # This is the easiest way to handle the unique internal path '<front>',
  # since a path marked as external does not need to match a router path.
  item['_external'] = menu_path_is_external(item['link_path'])  or item['link_path'] == '<front>'
  # Load defaults.
  item += {
    'menu_name' : 'navigation',
    'weight' : 0,
    'link_title' : '',
    'hidden' : 0,
    'has_children' : 0,
    'expanded' : 0,
    'options' : dict(),
    'module' : 'menu',
    'customized' : 0,
    'updated' : 0,
  }
  existing_item = False
  if (isset(item['mlid'])):
    existing_item = db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", item['mlid']))

  if (isset(item['plid'])):
    parent = db_fetch_array(db_query("SELECT * FROM {menu_links} WHERE mlid = %d", item['plid']))

  else:
    # Find the parent - it must be unique.
    parent_path = item['link_path']
    where = "WHERE link_path = '%s'"
    # Only links derived from router items should have module == 'system', and
    # we want to find the parent even if it's in a different menu.
    if (item['module'] == 'system'):
      where += " AND module = '%s'"
      arg2 = 'system'

    else:
      # If not derived from a router item, we respect the specified menu name.
      where += " AND menu_name = '%s'"
      arg2 = item['menu_name']

    while (parent == False and parent_path):
      parent = False
      parent_path = substr(parent_path, 0, strrpos(parent_path, '/'))
      result = db_query("SELECT COUNT(*) FROM {menu_links} " + where, parent_path, arg2)
      # Only valid if we get a unique result.
      if (db_result(result) == 1):
        parent = db_fetch_array(db_query("SELECT * FROM {menu_links} " + where, parent_path, arg2))

  if (parent != False):
    item['menu_name'] = parent['menu_name']

  menu_name = item['menu_name']
  # Menu callbacks need to be in the links table for breadcrumbs, but can't
  # be parents if they are generated directly from a router item.
  if (empty(parent['mlid']) or parent['hidden'] < 0):
    item['plid'] =  0

  else:
    item['plid'] = parent['mlid']

  if (not existing_item):
    db_query("INSERT INTO {menu_links} (menu_name, plid, link_path, hidden, external, has_children, expanded, weight, module, link_title, options, customized, updated) VALUES ('%s', %d, '%s', %d, %d, %d, %d, %d,'%s', '%s', '%s', %d, %d)", item['menu_name'], item['plid'], item['link_path'], item['hidden'], item['_external'], item['has_children'], item['expanded'], item['weight'], item['module'],  item['link_title'], serialize(item['options']), item['customized'], item['updated'])
    item['mlid'] = db_last_insert_id('menu_links', 'mlid')

  if (not item['plid']):
    item['p1'] = item['mlid']
    for i in range(MENU_MAX_DEPTH,1 ,1):
      item["pi"] = 0

    item['depth'] = 1

  else:
    # Cannot add beyond the maximum depth.
    if (item['has_children'] and existing_item):
      limit = MENU_MAX_DEPTH - menu_link_children_relative_depth(existing_item) - 1

    else:
      limit = MENU_MAX_DEPTH - 1

    if (parent['depth'] > limit):
      return False

    item['depth'] = parent['depth'] + 1
    _menu_link_parents_set(item, parent)

  # Need to check both plid and menu_name, since plid can be 0 in any menu.
  if (existing_item and (item['plid'] != existing_item['plid'] or menu_name != existing_item['menu_name'])):
    _menu_link_move_children(item, existing_item)

  # Find the callback. During the menu update we store empty paths to be
  # fixed later, so we skip this.
  if (not isset(_SESSION['system_update_6021']) and (empty(item['router_path'])  or not existing_item or (existing_item['link_path'] != item['link_path']))):
    if (item['_external']):
      item['router_path'] = ''

    else:
      # Find the router path which will serve this path.
      item['parts'] = explode('/', item['link_path'], MENU_MAX_PARTS)
      item['router_path'] = _menu_find_router_path(menu, item['link_path'])

  db_query("UPDATE {menu_links} SET menu_name = '%s', plid = %d, link_path = '%s', router_path = '%s', hidden = %d, external = %d, has_children = %d, expanded = %d, weight = %d, depth = %d, p1 = %d, p2 = %d, p3 = %d, p4 = %d, p5 = %d, p6 = %d, p7 = %d, p8 = %d, p9 = %d, module = '%s', link_title = '%s', options = '%s', customized = %d WHERE mlid = %d",
    item['menu_name'], item['plid'], item['link_path'],
    item['router_path'], item['hidden'], item['_external'], item['has_children'],
    item['expanded'], item['weight'],  item['depth'],
    item['p1'], item['p2'], item['p3'], item['p4'], item['p5'], item['p6'], item['p7'], item['p8'], item['p9'],
    item['module'],  item['link_title'], serialize(item['options']), item['customized'], item['mlid'])
  # Check the has_children status of the parent.
  _menu_update_parental_status(item)
  menu_cache_clear(menu_name)
  if (existing_item and menu_name != existing_item['menu_name']):
    menu_cache_clear(existing_item['menu_name'])

  _menu_clear_page_cache()

  return item['mlid']



#
# Helper function to clear the page and block caches at most twice per page load.
#
def _menu_clear_page_cache():
  global static_menuclearpagecache_cache_cleared
  if (static_menuclearpagecache_cache_cleared != 0):
    static_menuclearpagecache_cache_cleared = 0
  # Clear the page and block caches, but at most twice, including at
  #  the end of the page load when there are multple links saved or deleted.
  if (empty(cache_cleared)):
    cache_clear_all()
    # Keep track of which menus have expanded items.
    _menu_set_expanded_menus()
    cache_cleared = 1

  elif (cache_cleared == 1):
    register_shutdown_function('cache_clear_all')
    # Keep track of which menus have expanded items.
    register_shutdown_function('_menu_set_expanded_menus')
    cache_cleared = 2



#
# Helper function to update a list of menus with expanded items
#
def _menu_set_expanded_menus():
  names = dict()
  result = db_query("SELECT menu_name FROM {menu_links} WHERE expanded != 0 GROUP BY menu_name")
  while (n == db_fetch_array(result)):
    names = n['menu_name']

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
  parts = explode('/', link_path, MENU_MAX_PARTS)
  router_path = link_path
  if (not isset(menu[router_path])):
    ancestors = menu_get_ancestors(parts)
    ancestors = ''
    for key,router_path in ancestors.items():
      if (isset(menu[router_path])):
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
  if (op):
    if (insert):
      menu_link = {
        'link_title' : link_title,
        'link_path' : link_path,
        'module' : module,
      }
      return menu_link_save(menu_link)
    if (update):
      db_query("UPDATE {menu_links} SET link_title = '%s' WHERE link_path = '%s' AND customized = 0 AND module = '%s'", link_title, link_path, module)
      menu_cache_clear()
    if (delete):
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
  args = item['menu_name']
  p = 'p1'
  while (i <= MENU_MAX_DEPTH and item[p]):
    match += " AND p = %d"
    args = item[p]
    p = 'p' + i + 1

  max_depth = db_result(db_query_range("SELECT depth FROM {menu_links} WHERE menu_name = '%s'" + match + " ORDER BY depth DESC", args, 0, 1))

  return max_depth - item['depth'] if (max_depth > item['depth']) else 0



#
# Update the children of a menu link that's being moved.
#
# The menu name, parents (p1 - p6), and depth are updated for all children of
# the link, and the has_children status of the previous parent is updated.
#
def _menu_link_move_children(item, existing_item):

  args = item['menu_name']
  set = "menu_name = '%s'"
  i = 1
  while (i <= item['depth']):
    p = 'p' + i + 1
    set = "p = %d"
    args = item[p]

  j = existing_item['depth'] + 1
  while (i <= MENU_MAX_DEPTH and j <= MENU_MAX_DEPTH):
    set = 'p' + i + 1 + ' = p'. j + 1

  while (i <= MENU_MAX_DEPTH):
    set = 'p' + i + 1 + ' = 0'

  shift = item['depth'] - existing_item['depth']
  if (shift < 0):
    args = -shift
    set = 'depth = depth - %d'

  elif (shift > 0):
    # The order of set must be reversed so the new values don't overwrite the
    # old ones before they can be used because "Single-table UPDATE
    # assignments are generally evaluated from left to right"
    # see: http://dev.mysql.com/doc/refman/5.0/en/update.html
    set = array_reverse(set)
    args = array_reverse(args)
    args = shift
    set = 'depth = depth + %d'

  where = "menu_name = '%s'"
  args = existing_item['menu_name']
  p = 'p1'
  for i in range(MENU_MAX_DEPTH and existing_item[p], 0, 'p' + 1):
    where = "p = %d"
    args = existing_item[p]

  db_query("UPDATE {menu_links} SET " + implode(', ', set) + " WHERE ". implode(' AND ', where), args)
  # Check the has_children status of the parent, while excluding this item.
  _menu_update_parental_status(existing_item, True)



#
# Check and update the has_children status for the parent of a link.
#
def _menu_update_parental_status(item, exclude = False):
  # If plid == 0, there is nothing to update.
  if (item['plid']):
    # We may want to exclude the passed link as a possible child.
    where = " AND mlid != %d" if exclude else ''
    # Check if at least one visible child exists in the table.
    parent_has_children = bool(db_result(db_query_range("SELECT mlid FROM {menu_links} WHERE menu_name = '%s' AND plid = %d AND hidden = 0" + where, item['menu_name'], item['plid'], item['mlid'], 0, 1)))
    db_query("UPDATE {menu_links} SET has_children = %d WHERE mlid = %d", parent_has_children, item['plid'])



#
# Helper function that sets the p1..p9 values for a menu link being saved.
#
def _menu_link_parents_set(REF_item, parent):
  i = 1
  while (i < item['depth']):
    p = 'p' + i + 1
    item[p] = parent[p]

  p = 'p' + i + 1
  # The parent (p1 - p9) corresponding to the depth always equals the mlid.
  item[p] = item['mlid']
  while (i <= MENU_MAX_DEPTH):
    p = 'p' + i + 1
    item[p] = 0



#
# Helper function to build the router table based on the data from hook_menu.
#
def _menu_router_build(callbacks):
  # First pass: separate callbacks from paths, making paths ready for
  # matching. Calculate fitness, and fill some default values.
  menu = dict()
  for path,item in callbacks.items():
    load_functions = dict()
    to_arg_functions = dict()
    fit = 0
    move = False
    parts = explode('/', path, MENU_MAX_PARTS)
    number_parts = count(parts)
    # We store the highest index of parts here to save some work in the fit
    # calculation loop.
    slashes = number_parts - 1
    # Extract load and to_arg functions.
    for k,part in parts.items():
      match = False
      if (preg_match('/^%([a-z_]*)$/', part, matches)):
        if (empty(matches[1])):
          match = True
          load_functions[k] = None

        else:
          if (function_exists(matches[1] + '_to_arg')):
            to_arg_functions[k] = matches[1] + '_to_arg'
            load_functions[k] = None
            match = True

          if (function_exists(matches[1] + '_load')):
            function = matches[1] + '_load'
            # Create an array of arguments that will be passed to the _load
            # function when this menu path is checked, if 'load arguments'
            # exists.
            load_functions[k] = {function : item['load arguments']} if isset(item['load arguments']) else function
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
    item['load_functions'] = '' if empty(load_functions) else serialize(load_functions)
    item['to_arg_functions'] = '' if empty(to_arg_functions) else serialize(to_arg_functions)
    item += {
      'title' : '',
      'weight' : 0,
      'type' : MENU_NORMAL_ITEM,
      '_number_parts' : number_parts,
      '_parts' : parts,
      '_fit' : fit,
    }
    item += {
      '_visible' : (bool)(item['type'] & MENU_VISIBLE_IN_BREADCRUMB),
      '_tab' : (bool)(item['type'] & MENU_IS_LOCAL_TASK),
    }
    if (move):
      new_path = implode('/', item['_parts'])
      menu[new_path] = item
      sort[new_path] = number_parts

    else:
      menu[path] = item
      sort[path] = number_parts

  array_multisort(sort, SORT_NUMERIC, menu)
  # Apply inheritance rules.
  for path,v in menu.items():
    item = REF_menu[path]
    if (not item['_tab']):
      # Non-tab items.
      item['tab_parent'] = ''
      item['tab_root'] = path

    for i in range(item['_number_parts'] - 1, i, -1):
      parent_path = implode('/', array_slice(item['_parts'], 0, i))
      if (isset(menu[parent_path])):

        parent = menu[parent_path]
        if (not isset(item['tab_parent'])):
          # Parent stores the parent of the path.
          item['tab_parent'] = parent_path

        if (not isset(item['tab_root']) and not parent['_tab']):
          item['tab_root'] = parent_path

        # If a callback is not found, we try to find the first parent that
        # has a callback.
        if (not isset(item['access callback']) and isset(parent['access callback'])):
          item['access callback'] = parent['access callback']
          if (not isset(item['access arguments']) and isset(parent['access arguments'])):
            item['access arguments'] = parent['access arguments']

        # Same for page callbacks.
        if (not isset(item['page callback']) and isset(parent['page callback'])):
          item['page callback'] = parent['page callback']
          if (not isset(item['page arguments']) and isset(parent['page arguments'])):
            item['page arguments'] = parent['page arguments']

          if (not isset(item['file']) and isset(parent['file'])):
            item['file'] = parent['file']

          if (not isset(item['file path']) and isset(parent['file path'])):
            item['file path'] = parent['file path']

    if (not isset(item['access callback']) and isset(item['access arguments'])):
      # Default callback.
      item['access callback'] = 'user_access'

    if (not isset(item['access callback']) or empty(item['page callback'])):
      item['access callback'] = 0

    if (is_bool(item['access callback'])):
      item['access callback'] = intval(item['access callback'])

    item += {
      'access arguments' : dict(),
      'access callback' : '',
      'page arguments' : dict(),
      'page callback' : '',
      'block callback' : '',
      'title arguments' : dict(),
      'title callback' : 't',
      'description' : '',
      'position' : '',
      'tab_parent' : '',
      'tab_root' : path,
      'path' : path,
      'file' : '',
      'file path' : '',
      'include file' : '',
    }
    # Calculate out the file to be included for each callback, if any.
    if (item['file']):
      file_path = item['file path'] if item['file path'] else drupal_get_path('module', item['module'])
      item['include file'] = file_path + '/' + item['file']

    title_arguments = serialize(item['title arguments']) if item['title arguments'] else ''
    db_query("INSERT INTO {menu_router} (path, load_functions, to_arg_functions, access_callback, access_arguments, page_callback, page_arguments, fit, number_parts, tab_parent, tab_root, title, title_callback, title_arguments, type, block_callback, description, position, weight, file) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', %d, '%s')", path, item['load_functions'], item['to_arg_functions'], item['access callback'], serialize(item['access arguments']), item['page callback'], serialize(item['page arguments']), item['_fit'], item['_number_parts'], item['tab_parent'], item['tab_root'], item['title'], item['title callback'], title_arguments, item['type'], item['block callback'], item['description'], item['position'], item['weight'], item['include file'])

  # Sort the masks so they are in order of descending fit, and store them.
  masks = array_keys(masks)
  rsort(masks)
  variable_set('menu_masks', masks)
  return menu



#
# Returns True if a path is external (e.g. http://example.com).
#
def menu_path_is_external(path):
  colonpos = strpos(path, ':')
  return colonpos != False and not preg_match('not [/?#]not ', substr(path, 0, colonpos)) and filter_xss_bad_protocol(path, False) == check_plain(path)



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
      if (drupal_get_normal_path(_GET['q']) != 'admin/settings/site-maintenance'):
        drupal_set_message(t('Operating in off-line mode.'), 'status', False)

    else:
      # Anonymous users get a False at the login prompt, True otherwise.
      if (user_is_anonymous()):
        return _GET['q'] != 'user' and _GET['q'] != 'user/login'

      # Logged in users are unprivileged here, so they are logged out.
      #require_once drupal_get_path('module', 'user') + '/user.pages.inc'
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
  item = dict()
  path = form_item['link_path']
  # We indicate that a menu administrator is running the menu access check.
  menu_admin = True
  if (path == '<front>' or menu_path_is_external(path)):
    item = {'access' : True}

  elif (preg_match('/\/\%/', path)):
    # Path is dynamic (ie 'user/%'), so check directly against menu_router table.
    if (item == db_fetch_array(db_query("SELECT * FROM {menu_router} where path = '%s' ", path))):
      item['link_path'] = form_item['link_path']
      item['link_title'] = form_item['link_title']
      item['external'] = False
      item['options'] = ''
      _menu_link_translate(item)

  else:
    item = menu_get_item(path)

  menu_admin = False

  return item and item['access']



#
# @} End of "defgroup menu".
#
