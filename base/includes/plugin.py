#!/usr/bin/env python

# $Id: plugin.inc,v 1.120 2008/05/13 17:38:42 dries Exp $

"""
  API for loading and interacting with Drupal plugins.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/module.inc
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

from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyImport
import bootstrap as inc_bootstrap
import database as inc_database
import cache as inc_cache
#import install as inc_install

def plugin_load_all():
  """
   Load all the plugins that have been enabled in the system table.
  """
  for plugin_ in plugin_list(True, False):
    inc_bootstrap.drupal_load('plugin', plugin_)


def plugin_iterate(function, argument = ''):
  """
   Call a function repeatedly with each plugin in turn as an argument.
  """
  for name in plugin_list():
    p.call_user_func(function, name, argument)


def plugin_list(refresh = False, bootstrap = True, sort = False, fixed_list = None):
  """
   Collect a list of all loaded plugins. During the bootstrap, return only
   vital plugins. See bootstrap.inc
  
   @param refresh
     Whether to force the plugin list to be regenerated (such as after the
     administrator has changed the system settings).
   @param bootstrap
     Whether to return the reduced set of plugins loaded in "bootstrap mode"
     for cached pages. See bootstrap.inc.
   @param sort
     By default, plugins are ordered by weight and filename, settings this option
     to True, plugin list will be ordered by plugin name.
   @param fixed_list
     (Optional) Override the plugin list with the given plugins. Stays until the
     next call with refresh = True.
   @return
     An associative array whose keys and values are the names of all loaded
     plugins.
  """
  php.static(plugin_list, 'list_', {})
  php.static(plugin_list, 'sorted_list')
  if (refresh or fixed_list):
    plugin_list.sorted_list = None
    plugin_list.list_ = {}
    if (fixed_list):
      for name,plugin in fixed_list.items():
        inc_bootstrap.drupal_get_filename('plugin', name, plugin['filename'])
        plugin_list.list_[name] = name
    else:
      if (bootstrap):
        result = inc_database.db_query("SELECT name, filename FROM {system} WHERE type = 'plugin' AND status = 1 AND bootstrap = 1 ORDER BY weight ASC, filename ASC")
      else:
        result = inc_database.db_query("SELECT name, filename FROM {system} WHERE type = 'plugin' AND status = 1 ORDER BY weight ASC, filename ASC")
      while True:
        plugin_ = inc_database.db_fetch_object(result)
        if (plugin_ == None or plugin_ == False):
          break
        if (DrupyImport.exists(plugin_.filename)):
          inc_bootstrap.drupal_get_filename('plugin', plugin_.name, plugin_.filename)
          plugin_list.list_[plugin_.name] = plugin_.name
  if (sort):
    if (plugin_list.sorted_list == None):
      plugin_list.sorted_list = plugin_list.list_
      p.ksort(plugin_list.sorted_list)
    return plugin_list.sorted_list
  return plugin_list.list_



def plugin_rebuild_cache():
  """
   Rebuild the database cache of plugin files.
  
   @return
     The array of filesystem objects used to rebuild the cache.
  """
  # Get current list of plugins
  files = drupal_system_listing('\.plugin$', 'plugins', 'name', 0)
  # Extract current files from database.
  system_get_files_database(files, 'plugin')
  ksort(files)
  # Set defaults for plugin info
  defaults = {
    'dependencies' : [],
    'dependents' : [],
    'description' : '',
    'version' : None,
    'php' : DRUPAL_MINIMUM_PHP,
  }
  for filename,file in files.items():
    # Look for the info file.
    file.info = drupal_parse_info_file(php.dirname(file.filename) +  '/'  + file.name + '.info')
    # Skip plugins that don't provide info.
    if (php.empty(file.info)):
      del(files[filename])
      continue
    # Merge in defaults and save.
    files[filename].info = file.info + defaults
    # Invoke hook_system_info_alter() to give installed plugins a chance to
    # modify the data in the .info files if necessary.
    drupal_alter('system_info', files[filename].info, files[filename])
    # Log the critical hooks implemented by this plugin.
    bootstrap = 0
    for hook in bootstrap_hooks():
      if (plugin_hook(file.name, hook)):
        bootstrap = 1
        break
    # Update the contents of the system table:
    if (php.isset(file, 'status') or (php.isset(file, 'old_filename') and file.old_filename != file.filename)):
      db_query("UPDATE {system} SET info = '%s', name = '%s', filename = '%s', bootstrap = %d WHERE filename = '%s'", php.serialize(files[filename].info), file.name, file.filename, bootstrap, file.old_filename)
    else:
      # This is a new plugin.
      files[filename].status = 0
      db_query("INSERT INTO {system} (name, info, type, filename, status, bootstrap) VALUES ('%s', '%s', '%s', '%s', %d, %d)", file.name, php.serialize(files[filename].info), 'plugin', file.filename, 0, bootstrap)
  files = _plugin_build_dependencies(files)
  return files



def _plugin_build_dependencies(files):
  """
   Find dependencies any level deep and fill in dependents information too.
  
   If plugin A depends on B which in turn depends on C then this function will
   add C to the list of plugins A depends on. This will be repeated until
   plugin A has a list of all plugins it depends on. If it depends on itself,
   called a circular dependency, that's marked by adding a nonexistent plugin,
   called -circular- to this list of plugins. Because this does not exist,
   it'll be impossible to switch plugin A on.
  
   Also we fill in a dependents array in file.info. Using the names above,
   the dependents array of plugin B lists A.
  
   @param files
     The array of filesystem objects used to rebuild the cache.
   @return
     The same array with dependencies and dependents added where applicable.
  """
  while True:
    new_dependency = False
    for filename,file in files.items():
      # We will modify this object (plugin A, see doxygen for plugin A, B, C).
      file = files[filename]
      if (php.isset(file.info, 'dependencies') and php.is_array(file.info, 'dependencies')):
        for dependency_name in file.info['dependencies']:
          # This is a nonexistent plugin.
          if (dependency_name == '-circular-' or not php.isset(files[dependency_name])):
            continue
          # dependency_name is plugin B (again, see doxygen).
          files[dependency_name].info['dependents'][filename] = filename
          dependency = files[dependency_name]
          if (php.isset(dependency.info['dependencies']) and php.is_array(dependency.info['dependencies'])):
            # Let's find possible C plugins.
            for candidate in dependency.info['dependencies']:
              if (array_search(candidate, file.info['dependencies']) == False):
                # Is this a circular dependency?
                if (candidate == filename):
                  # As a plugin name can not contain dashes, this makes
                  # impossible to switch on the plugin.
                  candidate = '-circular-'
                  # Do not display the message or add -circular- more than once.
                  if (array_search(candidate, file.info['dependencies']) != False):
                    continue
                  drupal_set_message(t('%plugin is part of a circular dependency + This is not supported and you will not be able to switch it on.', {'%plugin' : file.info['name']}), 'error')
                else:
                  # We added a new dependency to plugin A. The next loop will
                  # be able to use this as "B plugin" thus finding even
                  # deeper dependencies.
                  new_dependency = True
                file.info['dependencies'].append( candidate )
      # Don't forget to break the reference.
      del(file)
    if (not new_dependency):
      break
  return files



def plugin_exists(plugin_):
  """
   Determine whether a given plugin exists.
  
   @param plugin
     The name of the plugin (without the .plugin extension).
   @return
     True if the plugin is both installed and enabled.
  """
  list_ = plugin_list()
  return php.isset(list_, plugin_)


def plugin_load_install(plugin_):
  """
   Load a plugin's installation hooks.
  """
  # Make sure the installation API is available
  plugin_load_include('install', plugin_)



def plugin_load_include(type_, plugin_, name = None):
  """
   Load a plugin include file.
  
   @param type
     The include file's type (file extension).
   @param plugin
     The plugin to which the include file belongs.
   @param name
     Optionally, specify the file name. If not set, the plugin's name is used.
  """
  if (php.empty(name)):
    name = plugin_
  file = './' +  drupal_get_path('plugin', plugin)  + "/name.type"
  if (php.is_file(file)):
    php.require_once( file )
    return file
  else:
    return False



def plugin_load_all_includes(type_, name = None):
  """
   Load an include file for each of the plugins that have been enabled in
   the system table.
  """
  plugins = plugin_list()
  for plugin_ in plugins:
    plugin_load_include(type_, plugin_, name)



def plugin_enable(plugin_list_):
  """
   Enable a given list of plugins.
  
   @param plugin_list
     An array of plugin names.
  """
  invoke_plugins = []
  for plugin_ in plugin_list_:
    existing = db_fetch_object(db_query("SELECT status FROM {system} WHERE type = '%s' AND name = '%s'", 'plugin', plugin))
    if (existing.status == 0):
      plugin_load_install(plugin_)
      db_query("UPDATE {system} SET status = %d WHERE type = '%s' AND name = '%s'", 1, 'plugin', plugin_)
      drupal_load('plugin', plugin_)
      invoke_plugins.append( plugin )
  if (not php.empty(invoke_plugins)):
    # Refresh the plugin list to include the new enabled plugin.
    plugin_list(True, False)
    # Force to regenerate the stored list of hook implementations.
    drupal_rebuild_code_registry()
  for plugin_ in invoke_plugins:
    plugin_invoke(plugin_, 'enable')
    # Check if node_access table needs rebuilding.
    # We check for the existence of node_access_needs_rebuild() since
    # at install time, plugin_enable() could be called while node.plugin
    # is not enabled yet.
    if (drupal_function_exists('node_access_needs_rebuild') and not node_access_needs_rebuild() and plugin_hook(plugin_, 'node_grants')):
      node_access_needs_rebuild(True)



def plugin_disable(plugin_list_):
  """
   Disable a given set of plugins.
  
   @param plugin_list
     An array of plugin names.
  """
  invoke_plugins = []
  for plugin_ in plugin_list_:
    if (plugin_exists(plugin_)):
      # Check if node_access table needs rebuilding.
      if (not node_access_needs_rebuild() and plugin_hook(plugin_, 'node_grants')):
        node_access_needs_rebuild(True)
      plugin_load_install(plugin_)
      plugin_invoke(plugin_, 'disable')
      db_query("UPDATE {system} SET status = %d WHERE type = '%s' AND name = '%s'", 0, 'plugin', plugin_)
      invoke_plugins.append(plugin)
  if (not php.empty(invoke_plugins)):
    # Refresh the plugin list to exclude the disabled plugins.
    plugin_list(True, False)
    # Force to regenerate the stored list of hook implementations.
    drupal_rebuild_code_registry();
  # If there remains no more node_access plugin, rebuilding will be
  # straightforward, we can do it right now.
  if (node_access_needs_rebuild() and php.count(plugin_implements('node_grants')) == 0):
    node_access_rebuild()



#
# @defgroup hooks Hooks
# @{
#
# Allow plugins to interact with the Drupal core.
#  
# Drupal's plugin system is based on the concept of "hooks". A hook is a PHP
# function that is named foo_bar(), where "foo" is the name of the plugin (whose
# filename is thus foo.plugin) and "bar" is the name of the hook. Each hook has
# a defined set of parameters and a specified result type.
# 
# To extend Drupal, a plugin need simply implement a hook. When Drupal wishes to
# allow intervention from plugins, it determines which plugins implement a hook
# and call that hook in all enabled plugins that implement it.
# 
# The available hooks to implement are explained here in the Hooks section of
# the developer documentation. The string "hook" is used as a placeholder for
# the plugin name is the hook definitions. For example, if the plugin file is
# called example.plugin, then hook_help() as implemented by that plugin would be
# defined as example_help().
#


def plugin_hook(plugin_, hook):
  """
   Determine whether a plugin implements a hook.
  
   @param plugin
     The name of the plugin (without the .plugin extension).
   @param hook
     The name of the hook (e.g. "help" or "menu").
   @return
     True if the plugin is both installed and enabled, and the hook is
     implemented in that plugin.
  """
  function = hook;
  if (inc_bootstrap.MAINTENANCE_MODE is True):
    return php.function_exists(function, inc_bootstrap.loaded_plugins[plugin_]);
  else:
    return inc_bootstrap.drupal_function_exists(function, \
      inc_bootstrap.loaded_plugins[plugin_]);



def plugin_implements(hook, sort = False, refresh = False):
  """
   Determine which plugins are implementing a hook.
  
   @param hook
     The name of the hook (e.g. "help" or "menu").
   @param sort
     By default, plugins are ordered by weight and filename, settings this option
     to True, plugin list will be ordered by plugin name.
   @param refresh
     For internal use only: Whether to force the stored list of hook
     implementations to be regenerated (such as after enabling a new plugin,
     before processing hook_enable).
   @return
     An array with the names of the plugins which are implementing this hook.
  """
  php.static(plugin_implements, 'implementations', {})
  if (refresh):
    plugin_implements.implementations = {}
  elif (inc_bootstrap.MAINTENANCE_MODE is False and php.empty(plugin_implements.implementations)):
    cache = inc_cache.cache_get('hooks', 'cache_registry')
    if (cache):
      plugin_implements.implementations = cache.data;
    plugin_implements.implementations = inc_bootstrap.registry_get_hook_implementations_cache()
  if (not php.isset(plugin_implements.implementations, hook)):
    plugin_implements.implementations[hook] = []
    for plugin_ in plugin_list():
      if (plugin_hook(plugin_, hook)):
        plugin_implements.implementations[hook].append( plugin_ )
  inc_bootstrap.registry_cache_hook_implementations({'hook' : hook, 'plugins' : plugin_implements.implementations[hook]});
  # The explicit cast forces a copy to be made. This is needed because
  # implementations[hook] is only a reference to an element of
  # implementations and if there are nested foreaches (due to nested node
  # API calls, for example), they would both manipulate the same array's
  # references, which causes some plugins' hooks not to be called.
  # See also http://www.zend.com/zend/art/ref-count.php.
  return plugin_implements.implementations[hook]



def plugin_invoke(*args):
  """
   Invoke a hook in a particular plugin.
  
   @param plugin
     The name of the plugin (without the .plugin extension).
   @param hook
     The name of the hook to invoke.
   @param ...
     Arguments to pass to the hook implementation.
   @return
     The return value of the hook implementation.
  """
  args = list(args)
  plugin_ = args[0]
  hook = args[1]
  del(args[0], args[1])
  if (plugin_hook(plugin_, hook)):
    function = plugin_ + '_' + hook
    return php.call_user_func_array(function, args)



def plugin_invoke_all(*args):
  """
   Invoke a hook in all enabled plugins that implement it.
  
   @param hook
     The name of the hook to invoke.
   @param ...
     Arguments to pass to the hook.
   @return
     An array of return values of the hook implementations. If plugins return
     arrays from their implementations, those are merged into one array.
  """
  args = list(args)
  hook = args[0]
  del(args[0])
  return_ = []
  for plugin_ in plugin_implements(hook):
    if (inc_bootstrap.drupal_function_exists(hook, inc_bootstrap.loaded_plugins[plugin_])):
      function = DrupyImport.getFunction(inc_bootstrap.loaded_plugins[plugin_], hook)
      result = php.call_user_func_array(function, args);
      if (result is not None and php.is_array(result)):
        return_ = p.array_merge_recursive(return_, result);
      elif (result is not None):
        return_.append( result );
  return return_


#
# @} End of "defgroup hooks".
#

def drupal_required_plugins():
  """
   Array of plugins required by core.
  """
  return ('block', 'filter', 'node', 'system', 'user')




