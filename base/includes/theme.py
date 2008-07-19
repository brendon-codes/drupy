#!/usr/bin/env python
# $Id: theme.inc,v 1.428 2008/06/25 09:12:24 dries Exp $

"""
  The theme system, which controls the output of Drupal.
  The theme system allows for nearly all output of the Drupy system to be
  customized by user themes.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @see <a href="http://drupal.org/node/253">Drupal Theme system</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/theme.inc
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

from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyImport
import bootstrap as lib_bootstrap
import common as lib_common
import database as lib_database
import plugin as lib_plugin

#
# Markers used by theme_mark() and node_mark() to designate content.
# @see theme_mark(), node_mark()
#

#
# Mark content as read.
#
MARK_READ = 0

#
# Mark content as being new.
#
MARK_NEW = 1

#
# Mark content as being updated.
#
MARK_UPDATED = 2


#
# GLOBALS
#
theme_ = None
profile = None
custom_theme = None
processors = {}



def init_theme():
  """
   Initialize the theme system by loading the theme.
  """
  global custom_theme
  global theme_key
  global theme_
  # If theme is already set, assume the others are set, too, and do nothing
  if (theme_ is not None):
    return True;
  lib_bootstrap.drupal_bootstrap(lib_bootstrap.DRUPAL_BOOTSTRAP_DATABASE);
  themes = list_themes();
  # Only select the user selected theme if it is available in the
  # list of enabled themes.
  if (lib_bootstrap.user is not None and \
      isset(lib_bootstrap.user, 'theme') and \
      not php.empty(lib_bootstrap.user.theme) and \
      not php.empty(themes[lib_bootstrap.user.theme].status)):
    theme_ = lib_bootstrap.user.theme
  else:
    theme_ = lib_bootstrap.variable_get('theme_default', 'garland')
  # Allow plugins to override the present theme... only select custom theme
  # if it is available in the list of installed themes.
  theme_ = (custom_theme if (custom_theme and themes[custom_theme]) else \
    theme_);
  # Store the identifier for retrieving theme settings with.
  theme_key = theme_;
  # Find all our ancestor themes and put them in an array.
  base_theme = [];
  ancestor = theme_;
  while (ancestor and php.isset(themes[ancestor], 'base_theme')):
    new_base_theme = themes[themes[ancestor].base_theme];
    base_theme.append(new_base_theme);
    ancestor = themes[ancestor].base_theme;
  _init_theme(themes[theme_], php.array_reverse(base_theme));



def _init_theme(this_theme, base_theme = [], registry_callback = \
    '_theme_load_registry'):
  """
   Initialize the theme system given already loaded information. This
   function is useful to initialize a theme when no database is present.
  
   @param this_theme
     An object with the following information:
       filename
         The .info file for this theme. The 'path' to
         the theme will be in this file's directory. (Required)
       owner
         The path to the .theme file or the .engine file to load for
         the theme. (Required)
       stylesheet
         The primary stylesheet for the theme. (Optional)
       engine
         The name of theme engine to use. (Optional)
   @param base_theme
      An optional array of objects that represent the 'base theme' if the
      theme is meant to be derivative of another theme. It requires
      the same information as the theme object. It should be in
      'oldest first' order, meaning the top level of the chain will
      be first.
   @param registry_callback
     The callback to invoke to set the theme registry.
  """
  global theme_info, base_theme_info, theme_engine, theme_path;
  global engine
  theme_info = this_theme;
  base_theme_info = base_theme;
  theme_path = php.dirname(this_theme.filename);
  # Prepare stylesheets from this theme as well as all ancestor themes.
  # We work it this way so that we can have child themes override parent
  # theme stylesheets easily.
  final_stylesheets = {};
  # Grab stylesheets from base theme
  for base in base_theme:
    if (not php.empty(base.stylesheets)):
      for media,stylesheets in base.stylesheets.items():
        final_stylesheets[media] = {}
        for name,stylesheet in stylesheets.items():
          final_stylesheets[media][name] = stylesheet;
  # Add stylesheets used by this theme.
  if (not php.empty(this_theme.stylesheets)):
    for media,stylesheets in this_theme.stylesheets.items():
      final_stylesheets[media] = {}
      for name,stylesheet in stylesheets.items():
        final_stylesheets[media][name] = stylesheet;
  # And now add the stylesheets properly
  for media,stylesheets in final_stylesheets.items():
    for stylesheet in stylesheets:
      lib_common.drupal_add_css(stylesheet, 'theme', media);
  # Do basically the same as the above for scripts
  final_scripts = {};
  # Grab scripts from base theme
  for base in base_theme:
    if (not php.empty(base.scripts)):
      for name,script in base.scripts.items():
        final_scripts[name] = script;
  # Add scripts used by this theme.
  if (not php.empty(this_theme.scripts)):
    for name,script in this_theme.scripts.items():
      final_scripts[name] = script;
  # Add scripts used by this theme.
  for script in final_scripts:
    drupal_add_js(script, 'theme');
  theme_engine = None;
  # Initialize the theme.
  if (php.isset(this_theme, 'engine')):
    # Include the engine.
    processors[this_theme.engine] = DrupyImport.import_file(this_theme.owner)
    theme_engine = this_theme.engine;
    if (php.function_exists('hook_init', processors[this_theme.engine])):
      for base in base_theme:
        php.call_user_func('hook_init', base);
      this_hook = DrupyImport.getFunction(processors[this_theme.engine],
        'hook_init')
      php.call_user_func(this_hook, this_theme);
  else:
    # include non-engine theme files
    for base in base_theme:
      # Include the theme file or the engine.
      if (not php.empty(base.owner)):
        php.include_once( './'  + base.owner );
    # and our theme gets one too.
    if (not php.empty(this_theme.owner)):
      php.include_once( './' + this_theme.owner );
    if (drupal_function_exists(registry_callback)):
      registry_callback(this_theme, base_theme, theme_engine)



def get_registry(registry = None):
  """
   Retrieve the stored theme registry. If the theme registry is already
   in memory it will be returned; otherwise it will attempt to load the
   registry from cache. If this fails, it will construct the registry and
   cache it.
  """
  php.static(theme_get_registry, 'theme_registry')
  if (theme_get_registry.theme_registry != None):
    theme_get_registry.theme_registry = registry;
  return theme_get_registry.theme_registry;



def _theme_set_registry(registry):
  """
   Store the theme registry in memory.
  """
  # Pass through for setting of static variable.
  return theme_get_registry(registry);



def _theme_load_registry(theme_, base_theme = None, theme_engine = None):
  """
   Get the theme_registry cache from the database; if it doesn't exist, build
   it.
  
   @param theme
     The loaded theme object.
   @param base_theme
     An array of loaded theme objects representing the ancestor themes in
     oldest first order.
   @param theme_engine
     The name of the theme engine.
  """
  # Check the theme registry cache; if it exists, use it.
  cache = cache_get("theme_registry:t%s" % theme.name, 'cache');
  if (php.isset(cache, 'data')):
    registry = cache.data;
  else:
    # If not, build one and cache it.
    registry = _theme_build_registry(theme_, base_theme, theme_engine);
    _theme_save_registry(theme_, registry);
  _theme_set_registry(registry);



def _theme_save_registry(theme_, registry):
  """
   Write the theme_registry cache into the database.
  """
  cache_set("theme_registry:%s" % theme.name, registry);



def drupal_rebuild_theme_registry():
  """
   Force the system to rebuild the theme registry; this should be called
   when plugins are added to the system, or when a dynamic system needs
   to add more theme hooks.
  """
  cache_clear_all('theme_registry', 'cache', True);



def _theme_process_registry(cache, name, type_, theme_, path):
  """
   Process a single invocation of the theme hook. type will be one
   of 'plugin', 'theme_engine' or 'theme' and it tells us some
   important information.
  
   Because cache is a reference, the cache will be continually
   expanded upon; new entries will replace old entries in the
   array_merge, but we are careful to ensure some data is carried
   forward, such as the arguments a theme hook needs.
  
   An override flag can be set for preprocess functions. When detected the
   cached preprocessors for the hook will not be merged with the newly set.
   This can be useful to themes and theme engines by giving them more control
   over how and when the preprocess functions are run.
  """
  php.Reference.check(cache);
  function = name + '_theme';
  if (php.function_exists(function)):
    result = function(cache, type_, theme_, path);
    for hook,info in result.items():
      result[hook]['type'] = type_;
      result[hook]['theme path'] = path;
      # if function and file are left out, default to standard naming
      # conventions.
      if (not php.isset(info, 'template') and not \
          php.isset(info, 'function')):
        result[hook]['function'] = ('theme_' if (type_ == 'plugin') else \
          name + '_') + hook;
      # If a path is set in the info, use what was set. Otherwise use the
      # default path. This is mostly so system.plugin can declare theme
      # functions on behalf of core .include files.
      # All files are included to be safe. Conditionally included
      # files can prevent them from getting registered.
      if (php.isset(info, 'file') and not php.isset(info['path'])):
        result[hook]['file'] = path + '/' + info['file'];
        php.include_once(result[hook]['file']);
      elif (php.isset(info, 'file') and php.isset(info, 'path')):
        php.include_once(info['path'] + '/' + info['file']);
      if (php.isset(info, 'template') and not php.isset(info, 'path')):
        result[hook]['template'] = path + '/' + info['template'];
      # If 'arguments' have been defined previously, carry them forward.
      # This should happen if a theme overrides a Drupal defined theme
      # function, for example.
      if (not php.isset(info, 'arguments') and php.isset(cache, hook)):
        result[hook]['arguments'] = cache[hook]['arguments'];
      # Likewise with theme paths. These are used for
      # template naming suggestions.
      # Theme implementations can occur in multiple paths.
      # Suggestions should follow.
      if (not php.isset(info, 'theme paths') and php.isset(cache, hook)):
        result[hook]['theme paths'] = cache[hook]['theme paths'];
      # Check for sub-directories.
      result[hook]['theme paths'].append( info['path'] if \
        php.isset(info, 'path') else path );
      # Check for default _preprocess_ functions. Ensure arrayness.
      if (not php.isset(info, 'preprocess functions') or not \
          php.is_array(info['preprocess functions'])):
        info['preprocess functions'] = [];
        prefixes = [];
        if (type == 'plugin'):
          # Default preprocessor prefix.
          prefixes.append( 'template' );
          # Add all plugins so they can intervene with their own
          # preprocessors. This allows them
          # to provide preprocess functions even if they are not
          # the owner of the current hook.
          prefixes += plugin_list();
        elif (type_ == 'theme_engine'):
          # Theme engines get an extra set that come before the
          # normally named preprocessors.
          prefixes.append( name + '_engine' );
          # The theme engine also registers on behalf of the theme.
          # The theme or engine name can be used.
          prefixes.append( name );
          prefixes.append( theme_ );
        else:
          # This applies when the theme manually registers their own
          # preprocessors.
          prefixes.append( name );
        for prefix in prefixes:
          if (php.function_exists(prefix + '_preprocess')):
            info['preprocess functions'].append( prefix + '_preprocess' );
          if (php.function_exists(prefix + '_preprocess_' + hook)):
            info['preprocess functions'].append( prefix + \
              '_preprocess_' + hook );
      # Check for the override flag and prevent the cached preprocess
      # functions from being used.
      # This allows themes or theme engines to remove preprocessors
      # set earlier in the registry build.
      if (not php.empty(info['override preprocess functions'])):
        # Flag not needed inside the registry.
        del(result[hook]['override preprocess functions']);
      elif (php.isset(cache[hook], 'preprocess functions') and \
          php.is_array(cache[hook]['preprocess functions'])):
        info['preprocess functions'] = \
          php.array_merge(cache[hook]['preprocess functions'], \
          info['preprocess functions']);
      result[hook]['preprocess functions'] = info['preprocess functions'];
    # Merge the newly created theme hooks into the existing cache.
    php.array_merge(cache, result, True);



def _theme_build_registry(theme_, base_theme, theme_engine):
  """
   Rebuild the hook theme_registry cache.
  
   @param theme
     The loaded theme object.
   @param base_theme
     An array of loaded theme objects representing the ancestor themes in
     oldest first order.
   @param theme_engine
     The name of the theme engine.
  """
  cache = {};
  # First, process the theme hooks advertised by plugins. This will
  # serve as the basic registry.
  for plugin in plugin_implements('theme'):
    _theme_process_registry(cache, plugin, 'plugin', plugin, \
      drupal_get_path('plugin', plugin));
  # Process each base theme.
  for base in base_theme:
    # If the theme uses a theme engine, process its hooks.
    base_path = php.dirname(base.filename);
    if (theme_engine):
      _theme_process_registry(cache, theme_engine, 'base_theme_engine', \
        base.name, base_path);
    _theme_process_registry(cache, base.name, 'base_theme', base.name, \
      base_path);
  # And then the same thing, but for the theme.
  if (theme_engine):
    _theme_process_registry(cache, theme_engine, 'theme_engine', \
      theme.name, php.dirname(theme_.filename));
  # Finally, hooks provided by the theme itself.
  _theme_process_registry(cache, theme_.name, 'theme', theme_.name, \
    php.dirname(theme_.filename));
  # Let plugins alter the registry
  drupal_alter('theme_registry', cache);
  return cache;



def list_themes(refresh = False):
  """
   Provides a list of currently available themes.
  
   If the database is active then it will be retrieved from the database.
   Otherwise it will retrieve a new list.
  
   @param refresh
     Whether to reload the list of themes from the database.
   @return
     An array of the currently available themes.
  """
  php.static(list_themes, 'list_', {})
  if (refresh):
    list_themes.list_ = {};
  if (php.empty(list_themes.list_)):
    themes = [];
    # Extract from the database only when it is available.
    # Also check that the site is not in the middle of an install or update.
    if (lib_database.db_is_active() and not lib_bootstrap.MAINTENANCE_MODE):
      result = lib_database.db_query(\
        "SELECT * FROM {system} WHERE type = '%s'", 'theme');
      while True:
        this_theme = lib_database.db_fetch_object(result);
        if this_theme == False or this_theme is None:
          break;
        if (php.file_exists(this_theme.filename)):
          this_theme.info = php.unserialize(this_theme.info);
          #php.print_r( dir(theme_) )
          #php.flush()
          #exit(1)
          themes.append( this_theme );
    else:
      # Scan the installation when the database should not be read.
      themes = lib_plugin.plugins['system']._theme_data();
    for i_theme in themes:
      i_theme.stylesheets = {}
      i_theme.scripts = {}
      for media,stylesheets in i_theme.info['stylesheets'].items():
        i_theme.stylesheets[media] = {}
        for stylesheet,path in stylesheets.items():
          if (php.file_exists(path)):
            i_theme.stylesheets[media][stylesheet] = path;
      for script,path in i_theme.info['scripts'].items():
        if (php.file_exists(path)):
          i_theme.scripts[script] = path;
      if (php.isset(i_theme.info, 'engine')):
        i_theme.engine = i_theme.info['engine'];
      if (php.isset(i_theme.info, 'base theme')):
        i_theme.base_theme = i_theme.info['base theme'];
      # Status is normally retrieved from the database. Add zero values when
      # read from the installation directory to prevent notices.
      if (not php.isset(i_theme, 'status')):
        i_theme.status = 0;
      list_themes.list_[i_theme.name] = i_theme;
  return list_themes.list_;


def theme(*args):
  
  """
   Generate the themed output.
  
   All requests for theme hooks must go through this function. It examines
   the request and routes it to the appropriate theme function. The theme
   registry is checked to determine which implementation to use, which may
   be a function or a template.
  
   If the implementation is a function, it is executed and its return value
   passed along.
  
   If the implementation is a template, the arguments are converted to a
   variables array. This array is then modified by the plugin implementing
   the hook, theme engine (if applicable) and the theme. The following
   functions may be used to modify the variables array. They are processed in
   this order when available:
  
   - template_preprocess(&variables)
     This sets a default set of variables for all template implementations.
  
   - template_preprocess_HOOK(&variables)
     This is the first preprocessor called specific to the hook; it should be
     implemented by the plugin that registers it.
  
   - MODULE_preprocess(&variables)
     This will be called for all templates; it should only be used if there
     is a real need. It's purpose is similar to template_preprocess().
  
   - MODULE_preprocess_HOOK(&variables)
     This is for plugins that want to alter or provide extra variables for
     theming hooks not registered to itself. For example, if a plugin named
     "foo" wanted to alter the submitted variable for the hook "node" a
     preprocess function of foo_preprocess_node() can be created to intercept
     and alter the variable.
  
   - ENGINE_engine_preprocess(&variables)
     This function should only be implemented by theme engines and exists
     so that it can set necessary variables for all hooks.
  
   - ENGINE_engine_preprocess_HOOK(&variables)
     This is the same as the previous function, but it is called for a single
     theming hook.
  
   - ENGINE_preprocess(&variables)
     This is meant to be used by themes that utilize a theme engine. It is
     provided so that the preprocessor is not locked into a specific theme.
     This makes it easy to share and transport code but theme authors must be
     careful to prevent fatal re-declaration errors when using sub-themes that
     have their own preprocessor named exactly the same as its base theme. In
     the default theme engine (PHPTemplate), sub-themes will load their own
     template.php file in addition to the one used for its parent theme. This
     increases the risk for these errors. A good practice is to use the engine
     name for the base theme and the theme name for the sub-themes to minimize
     this possibility.
  
   - ENGINE_preprocess_HOOK(&variables)
     The same applies from the previous function, but it is called for a
     specific hook.
  
   - THEME_preprocess(&variables)
     These functions are based upon the raw theme; they should primarily be
     used by themes that do not use an engine or by sub-themes. It serves the
     same purpose as ENGINE_preprocess().
  
   - THEME_preprocess_HOOK(&variables)
     The same applies from the previous function, but it is called for a
     specific hook.
  
   There are two special variables that these hooks can set:
     'template_file' and 'template_files'. These will be merged together
     to form a list of 'suggested' alternate template files to use, in
     reverse order of priority. template_file will always be a higher
     priority than items in template_files. theme() will then look for these
     files, one at a time, and use the first one
     that exists.
   @param hook
     The name of the theme function to call. May be an array, in which
     case the first hook that actually has an implementation registered
     will be used. This can be used to choose 'fallback' theme implementations,
     so that if the specific theme hook isn't implemented anywhere, a more
     generic one will be used. This can allow themes to create specific theme
     implementations for named objects.
   @param ...
     Additional arguments to pass along to the theme function.
   @return
     An HTML string that generates the themed output.
  """
  global theme_path;
  global theme_engine;
  php.static(theme, 'hooks')
  hook = php.array_shift(args);
  if (theme.hooks == None):
    init_theme();
    theme.hooks = theme_get_registry();
  if (php.is_array(hook)):
    for candidate in hook:
      if (php.isset(hooks, candidate)):
        break;
    hook = candidate;
  if (not php.isset(theme.hooks, hook)):
    return;
  info = theme.hooks[hook];
  temp = theme_path;
  # point path_to_theme() to the currently used theme path:
  theme_path = info['theme path'];
  # Include a file if the theme function or preprocess function is 
  # held elsewhere.
  if (not php.empty(info['file'])):
    include_file = info['file'];
    if (php.isset(info, 'path')):
      include_file = info['path'] + '/' + include_file;
    php.include_once(include_file);
  if (php.isset(info, 'function')):
    # The theme call is a function.
    output = info['function'](*args);
  else:
    # The theme call is a template.
    variables = {
      'template_files' : []
    };
    if (not php.empty(info['arguments'])):
      count = 0;
      for name,default in info['arguments'].items():
        variables[name] = (args[count] if php.isset(args, count) else default);
        count += 1;
    # default render function and extension.
    render_function = 'theme_render_template';
    extension = '.tpl.py';
    # Run through the theme engine variables, if necessary
    if (theme_engine != None):
      # If theme or theme engine is implementing this, it may have
      # a different extension and a different renderer.
      if (info['type'] != 'plugin'):
        if (php.function_exists(theme_engine + '_render_template')):
          render_function = theme_engine + '_render_template';
        extension_function = theme_engine + '_extension';
        if (php.function_exists(extension_function)):
          extension = extension_function();
    if (php.isset(info, 'preprocess functions') and \
        php.is_array(info['preprocess functions'])):
      # This construct ensures that we can keep a reference through
      # call_user_func_array.
      variables_ = php.Reference(variables);
      args = (variables_, hook);
      for preprocess_function in info['preprocess functions']:
        if (drupal_function_exists(preprocess_function)):
          preprocess_function( *args );
    # Get suggestions for alternate templates out of the variables
    # that were set. This lets us dynamically choose a template
    # from a list. The order is FILO, so this array is ordered from
    # least appropriate first to most appropriate last.
    suggestions = {};
    if (php.isset(variables_, 'template_files')):
      suggestions = variables_['template_files'];
    if (php.isset(variables_, 'template_file')):
      suggestions.append( variables_['template_file'] );
    if (suggestions):
      template_file = drupal_discover_template(info['theme paths'], \
        suggestions, extension);
    if (php.empty(template_file)):
      template_file = info['template'] + extension;
      if (php.isset(info, 'path')):
        template_file = info['path'] + '/' + template_file;
    output = render_function(template_file, variables);
  # restore path_to_theme()
  theme_path = temp;
  return output;



def drupal_discover_template(paths, suggestions, extension = '.tpl.php'):
  """
   Choose which template file to actually render. These are all suggested
   templates from themes and plugins. Theming implementations can occur on
   multiple levels. All paths are checked to account for this.
  """
  global theme_engine;
  # Loop through all paths and suggestions in FIFO order.
  suggestions = php.array_reverse(suggestions);
  paths = php.array_reverse(paths);
  for suggesiton in suggestions:
    if (not php.empty(suggestion)):
      for path in paths:
        file = path + '/' + suggestion + extension;
        if (php.file_exists(file)):
          return file;



def path_to_theme():
  """
   Return the path to the currently selected theme.
  """
  global theme_path;
  if (theme_path == None):
    init_theme();
  return theme_path;



def drupal_find_theme_functions(cache, prefixes):
  """
   Find overridden theme functions. Called by themes and/or theme engines to
   easily discover theme functions.
  
   @param cache
     The existing cache of theme hooks to test against.
   @param prefixes
     An array of prefixes to test, in reverse order of importance.
  
   @return templates
     The functions found, suitable for returning from hook_theme;
  """
  templates = [];
  functions = get_defined_functions();
  for hook,info in cache.items():
    for prefix in prefixes:
      if (not php.empty(info['pattern'])):
        matches = preg_grep('/^' + prefix + '_' + info['pattern'] + '/', \
          functions['user']);
        if (matches > 1):
          for match in matches:
            new_hook = php.str_replace(prefix + '_', '', match);
            templates[new_hook] = {
              'function' : match,
              'arguments' : info['arguments'],
            };
      if (php.function_exists(prefix + '_' + hook)):
        templates[hook] = {
          'function' : prefix + '_' + hook,
        };
  return templates;


def drupal_find_theme_templates(cache, extension, path):
  """
   Find overridden theme templates. Called by themes and/or theme engines to
   easily discover templates.
  
   @param cache
     The existing cache of theme hooks to test against.
   @param extension
     The extension that these templates will have.
   @param path
     The path to search.
  """
  global theme_;
  templates = [];
  # Collect paths to all sub-themes grouped by base themes+ These will be
  # used for filtering+ This allows base themes to have sub-themes in its
  # folder hierarchy without affecting the base themes template discovery+
  # theme_paths = array();
  for theme_info in list_themes():
    if (not php.empty(theme_info.base_theme)):
      theme_paths[theme_info.base_theme][theme_info.name] = \
        php.dirname(theme_info.filename);
  for basetheme,subthemes in theme_paths.items():
    for subtheme,subtheme_path in subthemes.items():
      if (php.isset(theme_paths, subtheme)):
        theme_paths[basetheme] = php.array_merge(theme_paths[basetheme], \
          theme_paths[subtheme]);
  subtheme_paths = (theme_paths[theme] if \
    php.isset(theme_paths, theme) else []);
  # Escape the periods in the extension+ regex = 
  # php.str_replace('.', '\.', extension) +'$';
  # Because drupal_system_listing works the way it does, we check for real
  # templates separately from checking for patterns+ files = 
  # drupal_system_listing(regex, path, 'name', 0);
  for template,file in files.items():
    # Ignore sub-theme templates for the current theme+ if 
    # (php.strpos(file.filename,
    # php.str_replace(subtheme_paths, '', file.filename)) !== 0):
    continue;
    # Chop off the remaining extensions if there are any+ template already
    # has the rightmost extension removed, but there might still be more,
    # such as with +tpl.php, which still has +tpl in template at this point
    pos = php.strpos(template, '.')
    if (pos != False):
      template = php.substr(template, 0, pos);
    # Transform - in filenames to _ to match function naming scheme
    # for the purposes of searching+ hook = php.strtr(template, '-', '_');
    if (php.isset(cache, hook)):
      templates[hook] = {
        'template' : template,
        'path' : php.dirname(file.filename),
      };
  patterns = php.array_keys(files);
  for hook,info in cache.items():
    if (not php.empty(info, 'pattern')):
      # Transform _ in pattern to - to match file naming scheme
      # for the purposes of searching+
      pattern = php.strtr(info['pattern'], '_', '-');
      matches = preg_grep('/^'+ pattern +'/', patterns);
      if (matches):
        for match in matches:
          file = php.substr(match, 0, php.strpos(match, '.'));
          # Put the underscores back in for the hook name and
          # register this pattern+
          templates[php.strtr(file, '-', '_')] = {
            'template' : file,
            'path' : php.dirname(files[match].filename),
            'arguments' : info['arguments'],
          };
  return templates;


def get_settings(key = None):
  """
   Retrieve an associative array containing the settings for a theme+ *
   The final settings are arrived at by merging the default settings,
   the site-wide settings, and the settings defined for the specific theme+ *
   If no key was specified, only the site-wide theme defaults are retrieved+ *
   The default values for each of settings are also defined in this function+
   To add new settings, add their default values here, and then add
   form elements
   to system_theme_settings() in system.plugin+ *
   @param key
    The template/style value for a given theme+ *
   @return
     An associative array containing theme settings
  """
  defaults = {
    'mission'                       :  '',
    'default_logo'                  :  1,
    'logo_path'                     :  '',
    'default_favicon'               :  1,
    'favicon_path'                  :  '',
    'main_menu'                     :  1,
    'secondary_menu'                :  1,
    'toggle_logo'                   :  1,
    'toggle_favicon'                :  1,
    'toggle_name'                   :  1,
    'toggle_search'                 :  1,
    'toggle_slogan'                 :  0,
    'toggle_mission'                :  1,
    'toggle_node_user_picture'      :  0,
    'toggle_comment_user_picture'   :  0,
    'toggle_main_menu'              :  1,
    'toggle_secondary_menu'         :  1
  };
  if (plugin_exists('node')):
    for type,name in node_get_types().items():
      defaults['toggle_node_info_'+ type] = 1;
  settings = php.array_merge(defaults, variable_get('theme_settings', array()))
  if (key != None):
    settings = php.array_merge(settings, \
      variable_get(php.str_replace('/', '_', 'theme_'+ key +'_settings'), []))
  # Only offer search box if search.plugin is enabled
  if (not plugin_exists('search') or not user_access('search content')):
    settings['toggle_search'] = 0;
  return settings;



def get_setting(setting_name, refresh = False):
  """
   Retrieve a setting for the current theme+
   This function is designed for use from within themes & engines
   to determine theme settings made in the admin interface+ *
   Caches values for speed (use refresh = True to refresh cache)
  
   @param setting_name
    The name of the setting to be retrieved+ *
   @param refresh
    Whether to reload the cache of settings+ *
   @return
     The value of the requested setting, None if the setting does not exist
  """
  global theme_key;
  php.static(theme_get_setting, 'settings')
  if (theme_get_setting.settings == None or refresh):
    theme_get_setting.settings = theme_get_settings(theme_key);
    themes = list_themes();
    theme_object = themes[theme_key];
    if (theme_get_setting.settings['mission'] == ''):
      theme_get_setting.settings['mission'] = variable_get('site_mission', '');
    if (not theme_get_setting.settings['toggle_mission']):
      theme_get_setting.settings['mission'] = '';
    if (theme_get_setting.settings['toggle_logo']):
      if (theme_get_setting.settings['default_logo']):
        theme_get_setting.settings['logo'] = base_path() + \
          php.dirname(theme_object.filename) +'/logo.png';
      elif (theme_get_setting.settings['logo_path']):
        theme_get_setting.settings['logo'] = base_path() + \
          theme_get_setting.settings['logo_path'];
    if (theme_get_setting.settings['toggle_favicon']):
      if (theme_get_setting.settings['default_favicon']):
        favicon = (php.dirname(theme_object.filename) +'/favicon.ico');
        if (php.file_exists(favicon)):
          theme_get_setting.settings['favicon'] = base_path() + favicon;
        else:
          theme_get_setting.settings['favicon'] = base_path() + \
            'misc/favicon.ico';
      elif (theme_get_setting.settings['favicon_path']):
        theme_get_setting.settings['favicon'] = base_path() + \
          theme_get_setting.settings['favicon_path'];
      else:
        theme_get_setting.settings['toggle_favicon'] = False;
  return (theme_get_setting.settings[setting_name] if \
    php.isset(theme_get_setting.settings, setting_name) else None);



def render_template(file, variables):
  """
   Render a system default template, which is essentially a PHP template+ *
   @param file
     The filename of the template to render
   @param variables
     A keyed array of variables that will appear in the output+ *
   @return
     The output generated by the template
  """
  extract(variables, EXTR_SKIP);  # Extract the variables to a local namespace
  ob_start();                     # Start output buffering
  php.include( "./file" );               # Include the file
  contents = ob_get_contents();   # Get the contents of the buffer
  ob_end_clean();                 # End buffering and discard
  return contents;                # Return the contents



#
# @defgroup themeable Default theme implementations
# @{
#

def placeholder(text):
  """
   Functions and templates that present output to the user, and can be
   implemented by themes
  
   Drupal's presentation layer is a pluggable system known as the theme
   layer+ Each theme can take control over most of Drupal's output, and
   has complete control over the CSS
  
   Inside Drupal, the theme layer is utilized by the use of the theme()
   function, which is passed the name of a component (the theme hook)
   and several arguments+ For example, theme('table', php.header, rows);
   Additionally, the theme() function can take an array of theme
   hooks, which can be used to provide 'fallback' implementations to
   allow for more specific control of output+ For example, the function:
   theme(array('table__foo', 'table'), php.header, rows) would look to see if
   'table__foo' is registered anywhere; if it is not, it would 'fall back'
   to the generic 'table' implementation+ This can be used to attach specific
   theme functions to named objects, allowing the themer more control over
   specific types of output
  
   As of Drupal 6, every theme hook is required to be registered by the
   plugin that owns it, so that Drupal can tell what to do with it and
   to make it simple for themes to identify and override the behavior
   for these calls
   
   The theme hooks are registered via hook_theme(), which returns an
   array of arrays with information about the hook+ It describes the
   arguments the function or template will need, and provides
   defaults for the template in case they are not filled in+ If the default
   implementation is a function, by convention it is named theme_HOOK()
   
   Each plugin should provide a default implementation for theme_hooks that
   it registers
   
   This implementation may be either a function or a template;
   if it is a function it must be specified via hook_theme()+ By convention,
   default implementations of theme hooks are named theme_HOOK+ Default
   template implementations are stored in the plugin directory+ *
   Drupal's default template renderer is a simple PHP parsing engine that
   includes the template and stores the output+ Drupal's theme engines
   can provide alternate template engines, such as XTemplate, Smarty and
   PHPTal+ The most common template engine is PHPTemplate (included with
   Drupal and implemented in phptemplate.engine, which uses Drupal's default
   template renderer
  
   In order to create theme-specific implementations of these hooks,
   themes can implement their own version of theme hooks, either as functions
   or templates+ These implementations will be used instead of the default
   implementation+ If using a pure +theme without an engine, the +theme is
   required to implement its own version of hook_theme() to tell Drupal what
   it is implementing; themes utilizing an engine will have their well-named
   theming functions automatically registered for them+ While this can vary
   based upon the theme engine, the standard set by phptemplate is that theme
   functions should be named either phptemplate_HOOK or THEMENAME_HOOK+ For
   example, for Drupal's default theme (Garland) to implement the 'table' hook,
   the phptemplate.engine would find phptemplate_table() or garland_table()
  
   The ENGINE_HOOK() syntax is preferred, as this can be used by sub-themes
   (which are themes that share code but use different stylesheets)
   The theme system is described and defined in theme.inc+ *
   @see theme()
   @see hook_theme()
  
   Formats text for emphasized display in a placeholder inside a sentence
   Used automatically by t()+ *
   @param text
     The text to format (plain-text)
   @return
     The formatted text (html)
  """
  return '<em>'+ check_plain(text) +'</em>';




def status_messages(display = None):
  """
   Return a themed set of status and/or error messages
   The messages are grouped by type
   
   @param display
     (optional) Set to 'status' or 'error' to display only messages
     of that type+ *
   @return
     A string containing the messages+
  """
  output = '';
  for type,messages in drupal_get_messages(display).items():
    output += "<div class=\"messages type\">\n";
    if (php.count(messages) > 1):
      output += " <ul>\n";
      for message in messages:
        output += '  <li>'+ message +"</li>\n";
      output += " </ul>\n";
    else:
      output += messages[0];
    output += "</div>\n";
  return output;



def links(links, attributes = {'class' : 'links'}):
  """
   Return a themed set of links+ *
   @param links
     A keyed array of links to be themed+ * @param attributes
     A keyed array of attributes
   @return
     A string containing an unordered list of links+
  """
  output = '';
  if (php.count(links) > 0):
    output = '<ul'+ drupal_attributes(attributes) +'>';
    num_links = php.count(links);
    i = 1;
    for key,link in links.items():
      class_ = key;
      # Add first, last and active classes to the list of links to help out themers+
      if (i == 1):
        class_ += ' first';
      if (i == num_links):
        class_ += ' last';
      if (php.isset(link['href']) and (link['href'] == php.GET['q'] or \
          (link['href'] == '<front>' and drupal_is_front_page()))):
        class_ += ' active';
      output += '<li class="'+ class_ +'">';
      if (php.isset(link['href'])):
        # Pass in link as options, they share the same keys
        output += l(link['title'], link['href'], link);
      elif (not php.empty(link, 'title')):
        # Some links are actually not links, but we wrap these in
        # <span> for adding title and class attributes
        if (php.empty(link, 'html')):
          link['title'] = check_plain(link['title']);
        span_attributes = '';
        if (php.isset(link, 'attributes')):
          span_attributes = drupal_attributes(link['attributes']);
        output += '<span'+ span_attributes +'>'+ link['title'] +'</span>';
      i += 1;
      output += "</li>\n";
    output += '</ul>';
  return output;



def image(path, alt = '', title = '', attributes = None, getsize = True):
  """
   Return a themed image+ *
   @param path
     Either the path of the image file (relative to base_path())
     or a full URL
   @param alt
     The alternative text for text-based browsers
   @param title
     The title text is displayed when the image is hovered in some
     popular browsers
   @param attributes
     Associative array of attributes to be placed in the img tag
   @param getsize
     If set to True, the image's dimension are fetched and added as
     width/height attributes
   @return A string containing the image tag+
  """
  imageSize = php.getimagesize(path);
  if (not getsize or (php.is_file(path) and (imageSize != False))):
    width, height, type, image_attributes = imageSize; 
    attributes = drupal_attributes(attributes);
    url =  path if (url(path) == path) else (base_path() + path);
    return '<img src="'+ check_url(url) +'" alt="'+ check_plain(alt) + \
      '" title="'+ check_plain(title) +'" '+ (image_attributes if \
      not php.empty(image_attributes) else '') + attributes +' />';



def breadcrumb(breadcrumb):
  """
   Return a themed breadcrumb trail+ *
   @param breadcrumb
     An array containing the breadcrumb links
   @return a string containing the breadcrumb output
  """
  if (not php.empty(breadcrumb)):
    return '<div class="breadcrumb">'+ \
      php.implode(' &raquo; ', breadcrumb) +'</div>';



def help_():
  """
   Return a themed help message+ *
   @return a string containing the helptext for the current page+
  """
  help = menu_get_active_help()
  if (help != False):
    return '<div class="help">'+ help +'</div>';



def submenu(links):
  """
   Return a themed submenu, typically displayed under the tabs+ *
   @param links
     An array of links+
  """
  return '<div class="submenu">'+ php.implode(' | ', links) +'</div>';


def table(header_, rows, attributes = {}, caption = None, colgroups = {}):
  """
   Return a themed table.
  
   @param php.header
     An array containing the table headers. Each element of the array can be
     either a localized string or an associative array with the following keys:
     - "data": The localized title of the table column.
     - "field": The database field represented in the table column (required if
       user is to be able to sort on this column).
     - "sort": A default sort order for this column ("asc" or "desc").
     - Any HTML attributes, such as "colspan", to apply to the
       column php.header cell.
   @param rows
     An array of table rows. Every row is an array of cells, or an associative
     array with the following keys:
     - "data": an array of cells
     - Any HTML attributes, such as "class", to apply to the table row.
  
     Each cell can be either a string or an associative
     array with the following keys:
     - "data": The string to display in the table cell.
     - "php.header": Indicates this cell is a php.header.
     - Any HTML attributes, such as "colspan", to apply to the table cell.
  
     Here's an example for rows:
     @verbatim
     rows = array(
       // Simple row
       array(
         'Cell 1', 'Cell 2', 'Cell 3'
       ),
       // Row with attributes on the row and some of its cells.
       array(
         'data' : array('Cell 1', array('data' : 'Cell 2', 'colspan' : 2)), \
           'class' : 'funky'
       )
     )
     @endverbatim
  
   @param attributes
     An array of HTML attributes to apply to the table tag.
   @param caption
     A localized string to use for the <caption> tag.
   @param colgroups
     An array of column groups. Each element of the array can be either:
     - An array of columns, each of which is an associative array of 
         HTML attributes
       applied to the COL element.
     - An array of attributes applied to the COLGROUP element, which 
       must include a
       "data" attribute. To add attributes to COL elements, set the "data"
       attribute
       with an array of columns, each of which is an associative array of
       HTML attributes.
     Here's an example for colgroup:
     @verbatim
     colgroup = array(
       // COLGROUP with one COL element.
       array(
         array(
           'class' : 'funky', // Attribute for the COL element.
         ),
       ),
       // Colgroup with attributes and inner COL elements.
       array(
         'data' : array(
           array(
             'class' : 'funky', // Attribute for the COL element.
           ),
         ),
         'class' : 'jazzy', // Attribute for the COLGROUP element.
       ),
     )
     @endverbatim
     These optional tags are used to group and set properties on columns
     within a table. For example, one may easily group three columns and
     apply same background style to all.
   @return
     An HTML string representing the table.
  """
  # Add sticky headers, if applicable.
  if (php.count(header_)):
    drupal_add_js('misc/tableheader.js')
    # Add 'sticky-enabled' class to the table to identify it for JS.
    # This is needed to target tables constructed by this function.
    attributes['class'] = ('sticky-enabled' if \
      php.empty(attributes['class']) else \
      (attributes['class'] +  ' sticky-enabled'))
  output = '<table' +  drupal_attributes(attributes)  + ">\n"
  if (php.isset(caption)):
    output += '<caption>' +  caption  + "</caption>\n"
  # Format the table columns:
  if (php.count(colgroups)):
    for number,colgroup in colgroups.items():
      attributes = {}
      # Check if we're dealing with a simple or complex column
      if (php.isset(colgroup, 'data')):
        for key,value in colgroup.items():
          if (key == 'data'):
            cols = value
          else:
            attributes[key] = value
      else:
        cols = colgroup
      # Build colgroup
      if (php.is_array(cols) and php.count(cols)):
        output += ' <colgroup' +  drupal_attributes(attributes)  + '>'
        i = 0
        for col in cols:
          output += ' <col' +  drupal_attributes(col)  + ' />'
        output += " </colgroup>\n"
      else:
        output += ' <colgroup' +  drupal_attributes(attributes)  + " />\n"
  # Format the table php.header:
  if (php.count(header_) > 0):
    ts = tablesort_init(header_);
    # HTML requires that the thead tag has tr tags in it follwed by tbody
    # tags+
    #Using ternary operator to check and see if we have any rows+
    output += (' <thead><tr>' if (php.count(rows) > 1) else ' <tr>');
    for cell in header_:
      cell = tablesort_header(cell, header_, ts);
      output += _theme_table_cell(cell, True);
    # Using ternary operator to close the tags based on
    # whether or not there are rows
    output += (" </tr></thead>\n" if (php.count(rows) > 0) else "</tr>\n");
  else:
    ts = [];
  # Format the table rows:
  if (php.count(rows) > 0):
    output += "<tbody>\n";
    flip = {'even' : 'odd', 'odd' : 'even'};
    class_ = 'even';
    for number,row in rows.items():
      attributes = [];
      # Check if we're dealing with a simple or complex row
      if (php.isset(row, 'data')):
        for key,value in row.items():
          if (key == 'data'):
            cells = value;
          else:
            attributes[key] = value;
      else:
        cells = row;
      if (php.count(cells) > 0):
        # Add odd/even class
        class_ = flip[class_];
        if (php.isset(attributes, 'class')):
          attributes['class'] += ' '+ class_;
        else:
          attributes['class'] = class_;
        # Build row
        output += ' <tr'+ drupal_attributes(attributes) +'>';
        i = 0;
        for cell in cells:
          cell = tablesort_cell(cell, header_, ts, i);
          i += 1;
          output += _theme_table_cell(cell);
        output += " </tr>\n";
    output += "</tbody>\n";
  output += "</table>\n";
  return output;




def table_select_header_cell():
  """
   Returns a php.header cell for tables that have a select all functionality+
  """
  drupal_add_js('misc/tableselect.js');
  return {'class' : 'select-all'};


def tablesort_indicator(style):
  """
   Return a themed sort icon+ *
   @param style
     Set to either asc or desc+
   This sets which icon to show+
    @return
     A themed sort icon+
  """
  if (style == "asc"):
    return theme('image', 'misc/arrow-asc.png', t('sort icon'), \
      t('sort ascending'));
  else:
    return theme('image', 'misc/arrow-desc.png', t('sort icon'), \
      t('sort descending'));



def box(title, content, region = 'main'):
  """
   Return a themed box+ *
   @param title
     The subject of the box+
   @param content
     The content of the box+
   @param region
     The region in which the box is displayed+
   @return
     A string containing the box output+
  """
  output = '<h2 class="title">'+ title +'</h2><div>'+ content +'</div>';
  return output;


def mark(type = MARK_NEW):
  """
   Return a themed marker, useful for marking new or updated
   content+ *
   @param type
     Number representing the marker type to display
   @see MARK_NEW, MARK_UPDATED, MARK_READ
   @return
     A string containing the marker+
  """
  if (lib_bootstrap.user.uid > 0):
    if (type == MARK_NEW):
      return ' <span class="marker">'+ t('new') +'</span>';
    elif (type == MARK_UPDATED):
      return ' <span class="marker">'+ t('updated') +'</span>';



def item_list(items = [], title = None, type = 'ul', attributes = []):
  """
   Return a themed list of items+ *
   @param items
     An array of items to be displayed in the list+ If an item is a string,
     then it is used as is+ If an item is an array, then the "data" element of
     the array is used as the contents of the list item+ If an item is an array
     with a "children" element, those children are displayed in a nested list+ 
     All other elements are treated as attributes of the list item element+
   @param title
     The title of the list+
   @param attributes
     The attributes applied to the list element+
   @param type
     The type of list to return (e.g+ "ul", "ol")
   @return
     A string containing the list output+
  """
  output = '<div class="item-list">';
  if (title != None):
    output += '<h3>'+ title +'</h3>';
  if (not php.empty(items)):
    output += "<type"+ drupal_attributes(attributes) +'>';
    num_items = php.count(items);
    for i,item in items.items():
      attributes = {};
      children = {};
      if (php.is_array(item)):
        for key,value in item.items():
          if (key == 'data'):
            data = value;
          elif (key == 'children'):
            children = value;
          else:
            attributes[key] = value;
      else:
        data = item;
      if (php.count(children) > 0):
        # Render nested list
        data += theme_item_list(children, None, type, attributes); 
      if (i == 0):
        attributes['class'] = ('first' if \
          php.empty(attributes['class']) else (attributes['class'] +' first'));
      if (i == num_items - 1):
        attributes['class'] = ('last' if \
          php.empty(attributes['class']) else (attributes['class'] +' last'));
      output += '<li'+ drupal_attributes(attributes) +'>'+ data +"</li>\n";
    output += "</type>";
  output += '</div>';
  return output;



def more_help_link(url):
  """
   Returns code that emits the 'more help'-link+
  """
  return '<div class="more-help-link">' +  t('<a href="@link">More help</a>', \
    {'@link' : check_url(url)}) + '</div>';



def xml_icon(url):
  """
   Return code that emits an XML icon+ *
   For most use cases, this function has been superseded by theme_feed_icon()
   @see theme_feed_icon()
   @param url
     The url of the feed
  """
  image = theme('image', 'misc/xml.png', t('XML feed'), t('XML feed'));
  if (image):
    return '<a href="'+ check_url(url) +'" class="xml-icon">'+ image +'</a>';


def feed_icon(url, title):
  """
   Return code that emits an feed icon+ *
   @param url
     The url of the feed+ * @param title
     A descriptive title of the feed+
  """
  image = theme('image', 'misc/feed.png', t('Syndicate content'), title)
  if (image):
    return '<a href="'+ check_url(url) +'" class="feed-icon">'+ image +'</a>';


def more_link(url, title):
  """
   Returns code that emits the 'more' link used on blocks+ *
   @param url
     The url of the main page
   @param title
     A descriptive verb for the link, like 'Read more'
  """
  return '<div class="more-link">'+ \
    t('<a href="@link" title="@title">more</a>', \
    {'@link' : check_url(url), '@title' : title}) +'</div>';



def closure(main_ = 0):
  """
   Execute hook_footer() which is run at the end of the page right before the
   close of the body tag+ *
   @param main (optional)
     Whether the current page is the front page of the site+ * @return
     A string containing the results of the hook_footer() calls+
  """
  footer = plugin_invoke_all('footer', main_);
  return php.implode("\n", footer) + drupal_get_js('footer');



def blocks(region):
  """
   Return a set of blocks available for the current user+ *
   @param region
     Which set of blocks to retrieve+ * @return
     A string containing the themed blocks for this region+
  """
  output = '';
  list = block_list(region);
  if (list):
    for key,block in list.items():
      # key == <i>plugin</i>_<i>delta</i>
      output += theme('block', block);
  # Add any content assigned to this region through drupal_set_content() calls+
  output += drupal_get_content(region);
  return output;



def username(object_):
  """
   Format a username+ *
   @param object
     The user object to format, usually returned from user_load()+ * @return
     A string containing an HTML link to the user's page if the passed object
     suggests that this is a site user+
   Otherwise, only the username is returned
  """
  nameSet = (php.isset(object_, 'name') and not php.empty(object_.name));
  if (object_.uid > 0 and nameSet):
    # Shorten the name when it is too long or it will break many tables+
    if (drupal_strlen(object_.name) > 20):
      name = drupal_substr(object_.name, 0, 15) +'...';
    else:
      name = object_.name;
    if (user_access('access user profiles')):
      output = l(name, 'user/' + object_.uid, {'attributes' : \
        {'title' : t('View user profile.')}})
    else:
      output = check_plain(name);
  elif (nameSet):
    # Sometimes plugins display content composed by people who are
    # not registered members of the site (e.g+ mailing list or news
    # aggregator plugins)+ This clause enables plugins to display
    # the True author of the content+
    if (php.isset(object_, 'homepage') and not php.empty(object_.homepage)):
      output = l(object_.name, object_.homepage, {'attributes' : \
        {'rel' : 'nofollow'}});
    else:
      output = check_plain(object_.name);
    output += ' ('+ t('not verified') +')';
  else:
    output = variable_get('anonymous', t('Anonymous'));
  return output;



def progress_bar(percent, message):
  """
   Return a themed progress bar+ *
   @param percent
     The percentage of the progress+
   @param message
     A string containing information to be displayed+
   @return
     A themed HTML string representing the progress bar
  """
  output = '<div id="progress" class="progress">';
  output += '<div class="bar"><div class="filled" style="width: '+ \
    percent +'%"></div></div>';
  output += '<div class="percentage">'+ percent +'%</div>';
  output += '<div class="message">'+ message +'</div>';
  output += '</div>';
  return output;



def indentation(size = 1):
  """
   Create a standard indentation div+ Used for drag and drop tables+ *
   @param size
     Optional+ The number of indentations to create+
   @return
     A string containing indentations+
  """
  output = '';
  for n in range(0, size):
    output += '<div class="indentation">&nbsp;</div>';
  return output;


#
# @} End of "defgroup themeable"+ */
#


def _table_cell(cell, header_ = False):
  attributes = '';
  if (php.is_array(cell)):
    data = (cell['data'] if php.isset(cell, 'data') else '');
    header_ |= php.isset(cell, 'header');
    del(cell['data']);
    del(cell['header']);
    attributes = drupal_attributes(cell);
  else:
    data = cell;
  if (header_):
    output = "<th %(attributes)s>%(data)s</th>" % { 'data' : data, \
     'attributes' : attributes };
  else:
    output = "<td %(attributes)s>%(data)s</td>" % { 'data' : data, \
     'attributes' : attributes };
  return output;



def template_preprocess(variables_, hook):
  """
   Adds a default set of helper variables for preprocess functions and
   templates+ This comes in before any other preprocess function which makes
   it possible to be used in default theme implementations (non-overriden
   theme functions)+
  """
  php.static(template_preprocess, 'count', {})
  php.Reference.check(variables_);
  # Track run count for each hook to provide zebra striping+
  # See "template_preprocess_block()" which provides the same
  # feature specific to blocks+
  template_preprocess.count[hook] = \
    (template_preprocess.count[hook] \
      if (php.isset(template_preprocess.count, hook) and \
        is_int(template_preprocess.count[hook])) else 1);
  variables_['zebra'] = ('odd' if \
    ((template_preprocess.count[hook] % 2) > 1) else 'even');
  template_preprocess.count[hook] += 1;
  variables_['id'] = template_preprocess.count[hook];
  # Tell all templates where they are located+
  variables['directory'] = path_to_theme();
  # Set default variables that depend on the database+
  variables['is_admin']            = False;
  variables_['is_front']            = False;
  variables_['logged_in']           = False;
  variables_['db_is_active'] = db_is_active() ;
  if (variables_['db_is_active'] and not php.defined('MAINTENANCE_MODE')):
    # Check for administrators+
    if (user_access('access administration pages')):
      variables_['is_admin'] = True;
    # Flag front page status+
    variables['is_front'] = drupal_is_front_page();
    # Tell all templates by which kind of user they're viewed+
    variables['logged_in'] = (lib_bootstrap.user.uid > 0);
    # Provide user object to all templates
    variables_['user'] = lib_bootstrap.user;



def template_preprocess_page(variables_):
  """
   Process variables for page.tpl.php
  
   Most themes utilize their own copy of page.tpl.php+ The default is located
   inside "plugins/system/page.tpl.php"+ Look in there for the full list of
   variables+ *
   Uses the arg() function to generate a series of page template suggestions
   based on the current path+ *
   Any changes to variables in this preprocessor should also be changed inside
   template_preprocess_maintenance_page() to keep all them consistent+ *
   The variables array contains the following arguments:
   - content
   - show_blocks
  
   @see page.tpl.php
  """
  global theme_;
  global language;
  php.Reference.check(variables_);
  # Add favicon
  if (theme_get_setting('toggle_favicon')):
    drupal_set_html_head('<link rel="shortcut icon" href="'+ \
      check_url(theme_get_setting('favicon')) +'" type="image/x-icon" />');
  # Populate all block regions+
  regions = system_region_list(theme);
  # Load all region content assigned via blocks+
  for region in php.array_keys(regions):
    # Prevent left and right regions from rendering blocks when
    # 'show_blocks' == False+
    if (not (not variables_['show_blocks'] and \
        (region == 'left' or region == 'right'))):
      blocks = theme('blocks', region);
    else:
      blocks = '';
    # Assign region to a region variable+
    if (php.isset(variables, region)):
      variables_[region] += blocks
    else:
      variables_[region] = blocks;
  # Set up layout variable+
  variables['layout'] = 'none';
  if (not php.empty(variables_['left'])):
    variables_['layout'] = 'left';
  if (not php.empty(variables_['right'])):
    variables['layout'] = ('both' if \
      (variables['layout'] == 'left') else 'right');
  # Set mission when viewing the frontpage+
  if (drupal_is_front_page()):
    mission = filter_xss_admin(theme_get_setting('mission'));
  else:
    mission = None;
  # Construct page title
  if (drupal_get_title()):
    head_title = [strip_tags(drupal_get_title()), \
      variable_get('site_name', 'Drupal')];
  else:
    head_title = [variable_get('site_name', 'Drupal')];
    if (variable_get('site_slogan', '')):
      head_title.append( variable_get('site_slogan', '') );
  variables_['head_title']        = php.implode(' | ', head_title);
  variables_['base_path']         = base_path();
  variables_['front_page']        = url();
  variables_['breadcrumb']        = theme('breadcrumb', \
    drupal_get_breadcrumb());
  variables_['feed_icons']        = drupal_get_feeds();
  variables_['footer_message']    = \
    filter_xss_admin(variable_get('site_footer', False));
  variables_['head']              = drupal_get_html_head();
  variables_['help']              = theme('help');
  variables_['language']          = language;
  variables_['language'].dir      = ('rtl' if \
    (php.isset(language, 'direction') and \
     not php.empty(language.direction)) else 'ltr');
  variables_['logo']              = theme_get_setting('logo');
  variables_['messages']          = (theme('status_messages') if \
    variables['show_messages'] else '');
  variables_['mission']           = (mission if (mission != None) else '');
  variables_['main_menu']         = (lib_menu.menu_main_menu() if \
    theme_get_setting('toggle_main_menu') else []);
  variables_['secondary_menu']    = (lib_menu.menu_secondary_menu() if \
    theme_get_setting('toggle_secondary_menu') else []);
  variables_['search_box']        = \
    (drupal_get_form('search_theme_form') if \
    theme_get_setting('toggle_search') else '');
  variables_['site_name']         = \
    (variable_get('site_name', 'Drupal') if \
    theme_get_setting('toggle_name') else '');
  variables_['site_slogan']       = \
    (variable_get('site_slogan', '') if \
    theme_get_setting('toggle_slogan') else '');
  variables_['css']               = drupal_add_css();
  variables_['styles']            = drupal_get_css();
  variables_['scripts']           = drupal_get_js();
  variables_['tabs']              = theme('menu_local_tasks');
  variables_['title']             = drupal_get_title();
  # Closure should be filled last+
  variables_['closure']           = theme('closure');
  node = lib_menu.menu_get_object();
  if (node):
    variables_['node'] = node;
  # Compile a list of classes that are going to be applied to the body element+
  # This allows advanced theming based on context
  # (home page, node of certain type, etc.)+
  body_classes = [];
  # Add a class that tells us whether we're on the front page or not+
  body_classes.append( ('front' if \
    variables_['is_front'] else 'not-front') );
  # Add a class that tells us whether
  # the page is viewed by an authenticated user or not+
  body_classes.append( ('logged-in' if \
    variables_['logged_in'] else 'not-logged-in') );
  # Add arg(0) to make it possible to theme
  # the page depending on the current page
  # type (e.g+ node, admin, user, etc.)
  # To avoid illegal characters in the class,
  # we're removing everything disallowed
  # We are not using 'a-z' as that might leave
  # in certain international characters (e.g+ German umlauts)+
  body_classes.append(\
    php.preg_replace('not [^abcdefghijklmnopqrstuvwxyz0-9-_]+not s', '', \
    'page-'+ form_clean_id(drupal_strtolower(arg(0)))) );
  # If on an individual node page, add the node type+
  if (php.isset(variables_, 'node') and variables_['node'].type):
    body_classes.append( 'node-type-'+ \
      form_clean_id(variables_['node'].type) );
  # Add information about the number of sidebars+
  if (variables_['layout'] == 'both'):
    body_classes.append( 'two-sidebars' );
  elif (variables_['layout'] == 'none'):
    body_classes.append( 'no-sidebars' );
  else:
    body_classes.append( 'one-sidebar sidebar-'+ variables_['layout'] );
  # Implode with spaces+
  variables_['body_classes'] = php.implode(' ', body_classes);
  # Build a list of suggested template files in order of specificity+ One
  # suggestion is made for every element of the current path, though
  # numeric elements are not carried to subsequent suggestions+ For example,
  # http://www.example.com/node/1/edit would result in the following
  # suggestions:
  #
  # page-node-edit.tpl.php
  # page-node-1.tpl.php
  # page-node.tpl.php
  # page.tpl.php
  i = 0;
  suggestion = 'page';
  suggestions = [];
  while True:
    arg_ = arg(i);
    if (arg_ == False or arg_ == None):
      break;
    else:
      i += 1;
    suggestions.append( suggestion +'-'+ arg_ );
    if (not php.is_numeric(arg_)):
      suggestion += '-'+ arg_;
  if (drupal_is_front_page()):
    suggestions.append( 'page-front' );
  if (not php.empty(suggestions)):
    variables_['template_files'] = suggestions;




def template_preprocess_node(variables_):
  """
   Process variables for node.tpl.php
  
   Most themes utilize their own copy of node.tpl.php+ The default is located
   inside "plugins/node/node.tpl.php"+ Look in there for the full list of
   variables+ *
   The variables array contains the following arguments:
   - node
   - teaser
   - page
  
   @see node.tpl.php
  """
  php.Reference.check(variables);
  node = variables_['node'];
  if (plugin_exists('taxonomy')):
    variables_['taxonomy'] = taxonomy_link('taxonomy terms', node);
  else:
    variables_['taxonomy'] = {};
  if (variables_['teaser'] and node.teaser):
    variables_['content'] = node.teaser;
  elif (php.isset(node, 'body')):
    variables_['content'] = node.body;
  else:
    variables_['content'] = '';
  variables_['date']      = format_date(node.created);
  variables_['links']     = (theme('links', node.links, \
    {'class' : 'links inline'}) if (not php.empty(node.links)) else '');
  variables_['name']      = theme('username', node);
  variables_['node_url']  = url('node/'+ node.nid);
  variables_['terms']     = theme('links', variables_['taxonomy'], \
    {'class' : 'links inline'});
  variables_['title']     = check_plain(node.title);
  # Flatten the node object's member fields+
  variables_ = php.array_merge(drupy_array(node), variables_);
  # Display info only on certain node types+
  if (theme_get_setting('toggle_node_info_'+ node.type_)):
    variables_['submitted'] = theme('node_submitted', node);
    variables_['picture'] = (theme('user_picture', node) if \
      theme_get_setting('toggle_node_user_picture') else '');
  else:
    variables_['submitted'] = '';
    variables_['picture'] = '';
  # Clean up name so there are no underscores+
  variables_['template_files'].append( 'node-' + \
    php.str_replace('_', '-', node.type_) )
  variables_['template_files'].append( 'node-' + node.nid )




def template_preprocess_block(variables_):
  """
   Process variables for block.tpl.php
  
   Prepare the values passed to the theme_block function to be passed
   into a pluggable template engine+ Uses block properties to generate a
   series of template file suggestions+ If none are found, the default
   block.tpl.php is used+ *
   Most themes utilize their own copy of block.tpl.php+ The default is located
   inside "plugins/system/block.tpl.php"+ Look in there for the full list of
   variables+ *
   The variables array contains the following arguments:
   - block
  
   @see block.tpl.php
  """
  php.static(template_preprocess_block, 'block_counter', {})
  php.Reference.check(variables_);
  # All blocks get an independent counter for each region+
  if (not php.isset(template_preprocess_block.block_counter, \
      variables_['block'].region)):
    template_preprocess_block.block_counter[variables_['block'].region] = 1
  # Same with zebra striping+
  variables_['block_zebra'] = ('odd' if \
    ((template_preprocess_block.block_counter[variables_['block'].region] \
    % 2) > 0) else 'even');
  variables_['block_id'] = \
    template_preprocess_block.block_counter[variables_['block'].region];
  template_preprocess_block.block_counter[variables_['block'].region] += 1;
  variables_['template_files'].append( \
    'block-'+ variables_['block'].region );
  variables_['template_files'].append( \
    'block-'+ variables_['block'].plugin );
  variables_['template_files'].append( \
    'block-'+ variables_['block'].plugin +'-'+ \
    variables_['block'].delta );



