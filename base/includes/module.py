#!/usr/bin/env python

# $Id: module.inc,v 1.120 2008/05/13 17:38:42 dries Exp $

"""
 @package Drupy
 @see http://drupy.net
 @note Drupy is a port of the Drupal project.
  The Drupal project can be found at http://drupal.org
 @file module.py (ported from Drupal's module.inc)
  API for loading and interacting with Drupal modules.
 @author Brendon Crawford
 @copyright 2008 Brendon Crawford
 @contact message144 at users dot sourceforge dot net
 @created 2008-01-10
 @version 0.1
 @license: 

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from lib.drupy import DrupyPHP as p
import bootstrap as inc_bootstrap
import database as inc_database
import cache as inc_cache
#import install as inc_install

def module_load_all():
  """
   Load all the modules that have been enabled in the system table.
  """
  for module_ in module_list(True, False):
    drupal_load('module', module_)


def module_iterate(function, argument = ''):
  """
   Call a function repeatedly with each module in turn as an argument.
  """
  for name in module_list():
    function(name, argument)


def module_list(refresh = False, bootstrap = True, sort = False, fixed_list = None):
  """
   Collect a list of all loaded modules. During the bootstrap, return only
   vital modules. See bootstrap.inc
  
   @param refresh
     Whether to force the module list to be regenerated (such as after the
     administrator has changed the system settings).
   @param bootstrap
     Whether to return the reduced set of modules loaded in "bootstrap mode"
     for cached pages. See bootstrap.inc.
   @param sort
     By default, modules are ordered by weight and filename, settings this option
     to True, module list will be ordered by module name.
   @param fixed_list
     (Optional) Override the module list with the given modules. Stays until the
     next call with refresh = True.
   @return
     An associative array whose keys and values are the names of all loaded
     modules.
  """
  p.static(module_list, 'list_', [])
  p.static(module_list, 'sorted_list')
  if (refresh or fixed_list):
    module_list.sorted_list = None
    module_list.list_ = []
    if (fixed_list):
      for name,module in fixed_list.items():
        inc_bootstrap.drupal_get_filename('module', name, module['filename'])
        module_list.list_[name] = name
    else:
      if (bootstrap):
        result = inc_database.db_query("SELECT name, filename FROM {system} WHERE type = 'module' AND status = 1 AND bootstrap = 1 ORDER BY weight ASC, filename ASC")
      else:
        result = inc_database.db_query("SELECT name, filename FROM {system} WHERE type = 'module' AND status = 1 ORDER BY weight ASC, filename ASC")
      while True:
        module_ = inc_database.db_fetch_object(result)
        if (module_ == None or module_ == False):
          break
        if (p.file_exists(module_.filename)):
          drupal_get_filename('module', module_.name, module_.filename)
          module_list.list_[module_.name] = module_.name
  if (sort):
    if (module_list.sorted_list == None):
      module_list.sorted_list = module_list.list_
      ksort(module_list.sorted_list)
    return module_list.sorted_list
  return module_list.list_



def module_rebuild_cache():
  """
   Rebuild the database cache of module files.
  
   @return
     The array of filesystem objects used to rebuild the cache.
  """
  # Get current list of modules
  files = drupal_system_listing('\.module$', 'modules', 'name', 0)
  # Extract current files from database.
  system_get_files_database(files, 'module')
  ksort(files)
  # Set defaults for module info
  defaults = {
    'dependencies' : [],
    'dependents' : [],
    'description' : '',
    'version' : None,
    'php' : DRUPAL_MINIMUM_PHP,
  }
  for filename,file in files.items():
    # Look for the info file.
    file.info = drupal_parse_info_file(p.dirname(file.filename) +  '/'  + file.name + '.info')
    # Skip modules that don't provide info.
    if (p.empty(file.info)):
      del(files[filename])
      continue
    # Merge in defaults and save.
    files[filename].info = file.info + defaults
    # Invoke hook_system_info_alter() to give installed modules a chance to
    # modify the data in the .info files if necessary.
    drupal_alter('system_info', files[filename].info, files[filename])
    # Log the critical hooks implemented by this module.
    bootstrap = 0
    for hook in bootstrap_hooks():
      if (module_hook(file.name, hook)):
        bootstrap = 1
        break
    # Update the contents of the system table:
    if (p.isset(file, 'status') or (p.isset(file, 'old_filename') and file.old_filename != file.filename)):
      db_query("UPDATE {system} SET info = '%s', name = '%s', filename = '%s', bootstrap = %d WHERE filename = '%s'", p.serialize(files[filename].info), file.name, file.filename, bootstrap, file.old_filename)
    else:
      # This is a new module.
      files[filename].status = 0
      db_query("INSERT INTO {system} (name, info, type, filename, status, bootstrap) VALUES ('%s', '%s', '%s', '%s', %d, %d)", file.name, p.serialize(files[filename].info), 'module', file.filename, 0, bootstrap)
  files = _module_build_dependencies(files)
  return files



def _module_build_dependencies(files):
  """
   Find dependencies any level deep and fill in dependents information too.
  
   If module A depends on B which in turn depends on C then this function will
   add C to the list of modules A depends on. This will be repeated until
   module A has a list of all modules it depends on. If it depends on itself,
   called a circular dependency, that's marked by adding a nonexistent module,
   called -circular- to this list of modules. Because this does not exist,
   it'll be impossible to switch module A on.
  
   Also we fill in a dependents array in file.info. Using the names above,
   the dependents array of module B lists A.
  
   @param files
     The array of filesystem objects used to rebuild the cache.
   @return
     The same array with dependencies and dependents added where applicable.
  """
  while True:
    new_dependency = False
    for filename,file in files.items():
      # We will modify this object (module A, see doxygen for module A, B, C).
      file = files[filename]
      if (p.isset(file.info, 'dependencies') and p.is_array(file.info, 'dependencies')):
        for dependency_name in file.info['dependencies']:
          # This is a nonexistent module.
          if (dependency_name == '-circular-' or not p.isset(files[dependency_name])):
            continue
          # dependency_name is module B (again, see doxygen).
          files[dependency_name].info['dependents'][filename] = filename
          dependency = files[dependency_name]
          if (p.isset(dependency.info['dependencies']) and p.is_array(dependency.info['dependencies'])):
            # Let's find possible C modules.
            for candidate in dependency.info['dependencies']:
              if (array_search(candidate, file.info['dependencies']) == False):
                # Is this a circular dependency?
                if (candidate == filename):
                  # As a module name can not contain dashes, this makes
                  # impossible to switch on the module.
                  candidate = '-circular-'
                  # Do not display the message or add -circular- more than once.
                  if (array_search(candidate, file.info['dependencies']) != False):
                    continue
                  drupal_set_message(t('%module is part of a circular dependency + This is not supported and you will not be able to switch it on.', {'%module' : file.info['name']}), 'error')
                else:
                  # We added a new dependency to module A. The next loop will
                  # be able to use this as "B module" thus finding even
                  # deeper dependencies.
                  new_dependency = True
                file.info['dependencies'].append( candidate )
      # Don't forget to break the reference.
      del(file)
    if (not new_dependency):
      break
  return files



def module_exists(module_):
  """
   Determine whether a given module exists.
  
   @param module
     The name of the module (without the .module extension).
   @return
     True if the module is both installed and enabled.
  """
  list_ = module_list()
  return p.isset(list_, module_)


def module_load_install(module_):
  """
   Load a module's installation hooks.
  """
  # Make sure the installation API is available
  module_load_include('install', module_)



def module_load_include(type_, module_, name = None):
  """
   Load a module include file.
  
   @param type
     The include file's type (file extension).
   @param module
     The module to which the include file belongs.
   @param name
     Optionally, specify the file name. If not set, the module's name is used.
  """
  if (p.empty(name)):
    name = module_
  file = './' +  drupal_get_path('module', module)  + "/name.type"
  if (p.is_file(file)):
    p.require_once( file )
    return file
  else:
    return False



def module_load_all_includes(type_, name = None):
  """
   Load an include file for each of the modules that have been enabled in
   the system table.
  """
  modules = module_list()
  for module_ in modules:
    module_load_include(type_, module_, name)



def module_enable(module_list_):
  """
   Enable a given list of modules.
  
   @param module_list
     An array of module names.
  """
  invoke_modules = []
  for module_ in module_list_:
    existing = db_fetch_object(db_query("SELECT status FROM {system} WHERE type = '%s' AND name = '%s'", 'module', module))
    if (existing.status == 0):
      module_load_install(module_)
      db_query("UPDATE {system} SET status = %d WHERE type = '%s' AND name = '%s'", 1, 'module', module_)
      drupal_load('module', module_)
      invoke_modules.append( module )
  if (not p.empty(invoke_modules)):
    # Refresh the module list to include the new enabled module.
    module_list(True, False)
    # Force to regenerate the stored list of hook implementations.
    drupal_rebuild_code_registry()
  for module_ in invoke_modules:
    module_invoke(module_, 'enable')
    # Check if node_access table needs rebuilding.
    # We check for the existence of node_access_needs_rebuild() since
    # at install time, module_enable() could be called while node.module
    # is not enabled yet.
    if (drupal_function_exists('node_access_needs_rebuild') and not node_access_needs_rebuild() and module_hook(module_, 'node_grants')):
      node_access_needs_rebuild(True)



def module_disable(module_list_):
  """
   Disable a given set of modules.
  
   @param module_list
     An array of module names.
  """
  invoke_modules = []
  for module_ in module_list_:
    if (module_exists(module_)):
      # Check if node_access table needs rebuilding.
      if (not node_access_needs_rebuild() and module_hook(module_, 'node_grants')):
        node_access_needs_rebuild(True)
      module_load_install(module_)
      module_invoke(module_, 'disable')
      db_query("UPDATE {system} SET status = %d WHERE type = '%s' AND name = '%s'", 0, 'module', module_)
      invoke_modules.append(module)
  if (not p.empty(invoke_modules)):
    # Refresh the module list to exclude the disabled modules.
    module_list(True, False)
    # Force to regenerate the stored list of hook implementations.
    drupal_rebuild_code_registry();
  # If there remains no more node_access module, rebuilding will be
  # straightforward, we can do it right now.
  if (node_access_needs_rebuild() and p.count(module_implements('node_grants')) == 0):
    node_access_rebuild()



#
# @defgroup hooks Hooks
# @{

def module_hook(module_, hook):
  """
   Allow modules to interact with the Drupal core.
  
   Drupal's module system is based on the concept of "hooks". A hook is a PHP
   function that is named foo_bar(), where "foo" is the name of the module (whose
   filename is thus foo.module) and "bar" is the name of the hook. Each hook has
   a defined set of parameters and a specified result type.
  
   To extend Drupal, a module need simply implement a hook. When Drupal wishes to
   allow intervention from modules, it determines which modules implement a hook
   and call that hook in all enabled modules that implement it.
  
   The available hooks to implement are explained here in the Hooks section of
   the developer documentation. The string "hook" is used as a placeholder for
   the module name is the hook definitions. For example, if the module file is
   called example.module, then hook_help() as implemented by that module would be
   defined as example_help().
  
  
   Determine whether a module implements a hook.
  
   @param module
     The name of the module (without the .module extension).
   @param hook
     The name of the hook (e.g. "help" or "menu").
   @return
     True if the module is both installed and enabled, and the hook is
     implemented in that module.
  """
  function = module_ + '_' + hook;
  if (p.defined('MAINTENANCE_MODE')):
    return p.function_exists(function);
  else:
     return inc_bootstrap.drupal_function_exists(function);



def module_implements(hook, sort = False, refresh = False):
  """
   Determine which modules are implementing a hook.
  
   @param hook
     The name of the hook (e.g. "help" or "menu").
   @param sort
     By default, modules are ordered by weight and filename, settings this option
     to True, module list will be ordered by module name.
   @param refresh
     For internal use only: Whether to force the stored list of hook
     implementations to be regenerated (such as after enabling a new module,
     before processing hook_enable).
   @return
     An array with the names of the modules which are implementing this hook.
  """
  p.static(module_implements, 'implementations', {})
  if (refresh):
    module_implements.implementations = {}
  elif (not p.defined('MAINTENANCE_MODE') and p.empty(module_implements.implementations)):
    cache = inc_cache.cache_get('hooks', 'cache_registry')
    if (cache):
      module_implements.implementations = cache.data;
    module_implements.implementations = inc_bootstrap.registry_get_hook_implementations_cache()
  if (not p.isset(module_implements.implementations, hook)):
    module_implements.implementations[hook] = []
    for module_ in module_list():
      if (module_hook(module_, hook)):
        module_implements.implementations[hook].append( module )
  inc_bootstrap.registry_cache_hook_implementations({'hook' : hook, 'modules' : module_implements.implementations[hook]});
  # The explicit cast forces a copy to be made. This is needed because
  # implementations[hook] is only a reference to an element of
  # implementations and if there are nested foreaches (due to nested node
  # API calls, for example), they would both manipulate the same array's
  # references, which causes some modules' hooks not to be called.
  # See also http://www.zend.com/zend/art/ref-count.php.
  return p.array_(module_implements.implementations[hook])



def module_invoke(*args):
  """
   Invoke a hook in a particular module.
  
   @param module
     The name of the module (without the .module extension).
   @param hook
     The name of the hook to invoke.
   @param ...
     Arguments to pass to the hook implementation.
   @return
     The return value of the hook implementation.
  """
  args = list(args)
  module_ = args[0]
  hook = args[1]
  del(args[0], args[1])
  if (module_hook(module_, hook)):
    function = module_ + '_' + hook
    return function( *args )



def module_invoke_all(*args):
  """
   Invoke a hook in all enabled modules that implement it.
  
   @param hook
     The name of the hook to invoke.
   @param ...
     Arguments to pass to the hook.
   @return
     An array of return values of the hook implementations. If modules return
     arrays from their implementations, those are merged into one array.
  """
  hook = args[0]
  del(args[0])
  return_ = []
  for module_ in module_implements(hook):
    function = module_ +  '_'  + hook
    result = function( *args)
    if (not p.empty(result) and p.is_array(result)):
      return_ = array_merge_recursive(return_, result)
    elif (not p.empty(result)):
      return_.append( result )
    if (drupal_function_exists(function)):
      result = function(*args);
      if (result != None and p.is_array(result)):
        return_ = array_merge_recursive(return_, result);
      elif (result != None):
        return_.append( result );
  return return_


#
# @} End of "defgroup hooks".
#

def drupal_required_modules():
  """
   Array of modules required by core.
  """
  return ('block', 'filter', 'node', 'system', 'user')




