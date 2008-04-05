##############################
#
# THIS FILE IS NOT COMPLETE
#
##############################

# Id: theme.inc,v 1.418 2008/03/25 14:10:01 dries Exp $
#
# @file
# The theme system, which controls the output of Drupal.
#
# The theme system allows for nearly all output of the Drupal system to be
# customized by user themes.
#

from lib.drupy import DrupyHelper


static('static_themegetregistry_themeregistry');
static('static_listthemes_list');
static('static_theme_hooks');
static('static_themegetsetting_settings');
static('static_template_preprocess_count');
static('static_templatepreprocessblock_blockcounter');


# @see <a href="http://drupal.org/node/253">Theme system</a>
# @see themeable
#
#
# @name Content markers
# @{
# Markers used by theme_mark() and node_mark() to designate content.
# @see theme_mark(), node_mark()
#
define('MARK_READ',    0);
define('MARK_NEW',     1);
define('MARK_UPDATED', 2);
#
# @} End of "Content markers".
#
#
# Initialize the theme system by loading the theme.
#
def init_theme():
  global _theme, user, custom_theme, theme_key;
  # If theme is already set, assume the others are set, too, and do nothing
  if (_theme != None):
    return True;
  drupal_bootstrap(DRUPAL_BOOTSTRAP_DATABASE);
  themes = list_themes();
  # Only select the user selected theme if it is available in the
  # list of enabled themes.
  _theme = (user.theme if (not empty(user.theme) and not empty(themes[user.theme].status)) else variable_get('theme_default', 'garland'));
  # Allow modules to override the present theme... only select custom theme
  # if it is available in the list of installed themes.
  _theme = (custom_theme if (custom_theme and themes[custom_theme]) else _theme);
  # Store the identifier for retrieving theme settings with.
  theme_key = _theme;
  # Find all our ancestor themes and put them in an array.
  base_theme = [];
  ancestor = _theme;
  while (ancestor and isset(themes[ancestor].base_theme)):
    new_base_theme = themes[themes[ancestor].base_theme];
    base_theme.append(new_base_theme);
    ancestor = themes[ancestor].base_theme;
  _init_theme(themes[_theme], array_reverse(base_theme));



#
# Initialize the theme system given already loaded information. This
# function is useful to initialize a theme when no database is present.
#
# @param theme
#   An object with the following information:
#     filename
#       The .info file for this theme. The 'path' to
#       the theme will be in this file's directory. (Required)
#     owner
#       The path to the .theme file or the .engine file to load for
#       the theme. (Required)
#     stylesheet
#       The primary stylesheet for the theme. (Optional)
#     engine
#       The name of theme engine to use. (Optional)
# @param base_theme
#    An optional array of objects that represent the 'base theme' if the
#    theme is meant to be derivative of another theme. It requires
#    the same information as the theme object. It should be in
#    'oldest first' order, meaning the top level of the chain will
#    be first.
# @param registry_callback
#   The callback to invoke to set the theme registry.
#
def _init_theme(_theme, base_theme = [], registry_callback = '_theme_load_registry'):
  global theme_info, base_theme_info, theme_engine, theme_path;
  theme_info = _theme;
  base_theme_info = base_theme;
  theme_path = dirname(theme.filename);
  # Prepare stylesheets from this theme as well as all ancestor themes.
  # We work it this way so that we can have child themes override parent
  # theme stylesheets easily.
  final_stylesheets = {};
  # Grab stylesheets from base theme
  for base in base_theme:
    if (not empty(base.stylesheets)):
      for media,stylesheets in base.stylesheets.items():
        for name,stylesheet in stylesheets.items():
          final_stylesheets[media][name] = stylesheet;
  # Add stylesheets used by this theme.
  if (not empty(theme.stylesheets)):
    for media,stylesheets in theme.stylesheets.items():
      for name,stylesheet in stylesheets.items():
        final_stylesheets[media][name] = stylesheet;
  # And now add the stylesheets properly
  for media,stylesheets in final_stylesheets.items():
    for stylesheet in stylesheets:
      drupal_add_css(stylesheet, 'theme', media);
  # Do basically the same as the above for scripts
  final_scripts = {};
  # Grab scripts from base theme
  for base in base_theme:
    if (not empty(base.scripts)):
      for name,script in base.scripts.items():
        final_scripts[name] = script;
  # Add scripts used by this theme.
  if (not empty(_theme.scripts)):
    for name,script in _theme.scripts.items():
      final_scripts[name] = script;
  # Add scripts used by this theme.
  for script in final_scripts:
    drupal_add_js(script, 'theme');
  theme_engine = None;
  # Initialize the theme.
  if (isset(_theme, 'engine')):
    # Include the engine.
    include_once( './' + _theme.owner );
    theme_engine = theme.engine;
    if (function_exists(theme_engine + '_init')):
      for base in base_theme:
        call_user_func(theme_engine + '_init', base);
      call_user_func(theme_engine + '_init', theme);
  else:
    # include non-engine theme files
    for base in base_theme:
      # Include the theme file or the engine.
      if (not empty(base.owner)):
        include_once( './'  + base.owner );
    # and our theme gets one too.
    if (not empty(theme.owner)):
      include_once( './' + theme.owner );
  registry_callback(theme, base_theme, theme_engine);



#
# Retrieve the stored theme registry. If the theme registry is already
# in memory it will be returned; otherwise it will attempt to load the
# registry from cache. If this fails, it will construct the registry and
# cache it.
#
def theme_get_registry(registry = None):
  global static_themegetregistry_themeregistry;
  if (static_themegetregistry_themeregistry != None):
    static_themegetregistry_themeregistry = registry;
  return static_themegetregistry_themeregistry;



#
# Store the theme registry in memory.
#
def _theme_set_registry(registry):
  # Pass through for setting of static variable.
  return theme_get_registry(registry);



#
# Get the theme_registry cache from the database; if it doesn't exist, build
# it.
#
# @param theme
#   The loaded theme object.
# @param base_theme
#   An array of loaded theme objects representing the ancestor themes in
#   oldest first order.
# @param theme_engine
#   The name of the theme engine.
#
def _theme_load_registry(_theme, base_theme = None, theme_engine = None):
  # Check the theme registry cache; if it exists, use it.
  cache = cache_get("theme_registry:t%s" % theme.name, 'cache');
  if (isset(cache, 'data')):
    registry = cache.data;
  else:
    # If not, build one and cache it.
    registry = _theme_build_registry(_theme, base_theme, theme_engine);
    _theme_save_registry(_theme, registry);
  _theme_set_registry(registry);



#
# Write the theme_registry cache into the database.
#
def _theme_save_registry(_theme, registry):
  cache_set("theme_registry:%s" % theme.name, registry);



#
# Force the system to rebuild the theme registry; this should be called
# when modules are added to the system, or when a dynamic system needs
# to add more theme hooks.
#
def drupal_rebuild_theme_registry():
  cache_clear_all('theme_registry', 'cache', True);



#
# Process a single invocation of the theme hook. type will be one
# of 'module', 'theme_engine' or 'theme' and it tells us some
# important information.
#
# Because cache is a reference, the cache will be continually
# expanded upon; new entries will replace old entries in the
# array_merge, but we are careful to ensure some data is carried
# forward, such as the arguments a theme hook needs.
#
# An override flag can be set for preprocess functions. When detected the
# cached preprocessors for the hook will not be merged with the newly set.
# This can be useful to themes and theme engines by giving them more control
# over how and when the preprocess functions are run.
#
def _theme_process_registry(cache, name, _type, _theme, path):
  drupy.helper.Reference.check(cache);
  function = name + '_theme';
  if (function_exists(function)):
    result = function(cache.val, _type, _theme, path);
    for hook,info in result.items():
      result[hook]['type'] = _type;
      result[hook]['theme path'] = path;
      # if function and file are left out, default to standard naming
      # conventions.
      if (not isset(info, 'template') and not isset(info, 'function')):
        result[hook]['function'] = ('theme_' if (_type == 'module') else name + '_') + hook;
      # If a path is set in the info, use what was set. Otherwise use the
      # default path. This is mostly so system.module can declare theme
      # functions on behalf of core .include files.
      # All files are included to be safe. Conditionally included
      # files can prevent them from getting registered.
      if (isset(info, 'file') and not isset(info['path'])):
        result[hook]['file'] = path + '/' + info['file'];
        include_once(result[hook]['file']);
      elif (isset(info, 'file') and isset(info, 'path')):
        include_once(info['path'] + '/' + info['file']);
      if (isset(info, 'template') and not isset(info, 'path')):
        result[hook]['template'] = path + '/' + info['template'];
      # If 'arguments' have been defined previously, carry them forward.
      # This should happen if a theme overrides a Drupal defined theme
      # function, for example.
      if (not isset(info, 'arguments') and isset(cache.val, hook)):
        result[hook]['arguments'] = cache[hook]['arguments'];
      # Likewise with theme paths. These are used for template naming suggestions.
      # Theme implementations can occur in multiple paths. Suggestions should follow.
      if (not isset(info, 'theme paths') and isset(cache.val, hook)):
        result[hook]['theme paths'] = cache[hook]['theme paths'];
      # Check for sub-directories.
      result[hook]['theme paths'].append( info['path'] if isset(info, 'path') else path );
      # Check for default _preprocess_ functions. Ensure arrayness.
      if (not isset(info, 'preprocess functions') or not is_array(info['preprocess functions'])):
        info['preprocess functions'] = [];
        prefixes = [];
        if (type == 'module'):
          # Default preprocessor prefix.
          prefixes.append( 'template' );
          # Add all modules so they can intervene with their own preprocessors. This allows them
          # to provide preprocess functions even if they are not the owner of the current hook.
          prefixes += module_list();
        elif (_type == 'theme_engine'):
          # Theme engines get an extra set that come before the normally named preprocessors.
          prefixes.append( name + '_engine' );
          # The theme engine also registers on behalf of the theme. The theme or engine name can be used.
          prefixes.append( name );
          prefixes.append( _theme );
        else:
          # This applies when the theme manually registers their own preprocessors.
          prefixes.append( name );
        for prefix in prefixes:
          if (function_exists(prefix + '_preprocess')):
            info['preprocess functions'].append( prefix + '_preprocess' );
          if (function_exists(prefix + '_preprocess_' + hook)):
            info['preprocess functions'].append( prefix + '_preprocess_' + hook );
      # Check for the override flag and prevent the cached preprocess functions from being used.
      # This allows themes or theme engines to remove preprocessors set earlier in the registry build.
      if (not empty(info['override preprocess functions'])):
        # Flag not needed inside the registry.
        del(result[hook]['override preprocess functions']);
      elif (isset(cache[hook], 'preprocess functions') and is_array(cache.val[hook]['preprocess functions'])):
        info['preprocess functions'] = array_merge(cache[hook]['preprocess functions'], info['preprocess functions']);
      result[hook]['preprocess functions'] = info['preprocess functions'];
    # Merge the newly created theme hooks into the existing cache.
    cache.val = array_merge(cache.val, result);



#
# Rebuild the hook theme_registry cache.
#
# @param theme
#   The loaded theme object.
# @param base_theme
#   An array of loaded theme objects representing the ancestor themes in
#   oldest first order.
# @param theme_engine
#   The name of the theme engine.
#
def _theme_build_registry(_theme, base_theme, theme_engine):
  cache = {};
  # First, process the theme hooks advertised by modules. This will
  # serve as the basic registry.
  for module in module_implements('theme'):
    _theme_process_registry(cache, module, 'module', module, drupal_get_path('module', module));
  # Process each base theme.
  for base in base_theme:
    # If the theme uses a theme engine, process its hooks.
    base_path = dirname(base.filename);
    if (theme_engine):
      _theme_process_registry(cache, _theme_engine, 'base_theme_engine', base.name, base_path);
    _theme_process_registry(cache, base.name, 'base_theme', base.name, base_path);
  # And then the same thing, but for the theme.
  if (theme_engine):
    _theme_process_registry(cache, theme_engine, 'theme_engine', theme.name, dirname(_theme.filename));
  # Finally, hooks provided by the theme itself.
  _theme_process_registry(cache, _theme.name, 'theme', _theme.name, dirname(_theme.filename));
  # Let modules alter the registry
  drupal_alter('theme_registry', cache);
  return cache;



#
# Provides a list of currently available themes.
#
# If the database is active then it will be retrieved from the database.
# Otherwise it will retrieve a new list.
#
# @param refresh
#   Whether to reload the list of themes from the database.
# @return
#   An array of the currently available themes.
#
def list_themes(refresh = False):
  global static_listthemes_list;
  if (refresh):
    static_listthemes_list = [];
  if (empty(static_listthemes_list)):
    static_listthemes_list = [];
    themes = [];
    # Extract from the database only when it is available.
    # Also check that the site is not in the middle of an install or update.
    if (db_is_active() and not defined('MAINTENANCE_MODE')):
      result = db_query("SELECT * FROM {system} WHERE type = '%s'", 'theme');
      while True:
        _theme = db_fetch_object(result);
        if _theme == False or _theme == None:
          break;
        if (file_exists(_theme.filename)):
          _theme.info = unserialize(_theme.info);
          themes.append( _theme );
    else:
      # Scan the installation when the database should not be read.
      themes = _system_theme_data();
    for _theme in themes:
      for media,stylesheets in _theme.info['stylesheets']:
        for stylesheet,path in stylesheets:
          if (file_exists(path)):
            _theme.stylesheets[media][stylesheet] = path;
      for script,path in theme.info['scripts'].items():
        if (file_exists(path)):
          _theme.scripts[script] = path;
      if (isset(_theme.info, 'engine')):
        _theme.engine = _theme.info['engine'];
      if (isset(_theme.info, 'base theme')):
        _theme.base_theme = _theme.info['base theme'];
      # Status is normally retrieved from the database. Add zero values when
      # read from the installation directory to prevent notices.
      if (not isset(_theme, 'status')):
        _theme.status = 0;
      static_listthemes_list[_theme.name] = _theme;
  return static_listthemes_list;



#
# Generate the themed output.
#
# All requests for theme hooks must go through this function. It examines
# the request and routes it to the appropriate theme function. The theme
# registry is checked to determine which implementation to use, which may
# be a function or a template.
#
# If the implementation is a function, it is executed and its return value
# passed along.
#
# If the implementation is a template, the arguments are converted to a
# variables array. This array is then modified by the module implementing
# the hook, theme engine (if applicable) and the theme. The following
# functions may be used to modify the variables array. They are processed in
# this order when available:
#
# - template_preprocess(&variables)
#   This sets a default set of variables for all template implementations.
#
# - template_preprocess_HOOK(&variables)
#   This is the first preprocessor called specific to the hook; it should be
#   implemented by the module that registers it.
#
# - MODULE_preprocess(&variables)
#   This will be called for all templates; it should only be used if there
#   is a real need. It's purpose is similar to template_preprocess().
#
# - MODULE_preprocess_HOOK(&variables)
#   This is for modules that want to alter or provide extra variables for
#   theming hooks not registered to itself. For example, if a module named
#   "foo" wanted to alter the submitted variable for the hook "node" a
#   preprocess function of foo_preprocess_node() can be created to intercept
#   and alter the variable.
#
# - ENGINE_engine_preprocess(&variables)
#   This function should only be implemented by theme engines and exists
#   so that it can set necessary variables for all hooks.
#
# - ENGINE_engine_preprocess_HOOK(&variables)
#   This is the same as the previous function, but it is called for a single
#   theming hook.
#
# - ENGINE_preprocess(&variables)
#   This is meant to be used by themes that utilize a theme engine. It is
#   provided so that the preprocessor is not locked into a specific theme.
#   This makes it easy to share and transport code but theme authors must be
#   careful to prevent fatal re-declaration errors when using sub-themes that
#   have their own preprocessor named exactly the same as its base theme. In
#   the default theme engine (PHPTemplate), sub-themes will load their own
#   template.php file in addition to the one used for its parent theme. This
#   increases the risk for these errors. A good practice is to use the engine
#   name for the base theme and the theme name for the sub-themes to minimize
#   this possibility.
#
# - ENGINE_preprocess_HOOK(&variables)
#   The same applies from the previous function, but it is called for a
#   specific hook.
#
# - THEME_preprocess(&variables)
#   These functions are based upon the raw theme; they should primarily be
#   used by themes that do not use an engine or by sub-themes. It serves the
#   same purpose as ENGINE_preprocess().
#
# - THEME_preprocess_HOOK(&variables)
#   The same applies from the previous function, but it is called for a
#   specific hook.
#
# There are two special variables that these hooks can set:
#   'template_file' and 'template_files'. These will be merged together
#   to form a list of 'suggested' alternate template files to use, in
#   reverse order of priority. template_file will always be a higher
#   priority than items in template_files. theme() will then look for these
#   files, one at a time, and use the first one
#   that exists.
# @param hook
#   The name of the theme function to call. May be an array, in which
#   case the first hook that actually has an implementation registered
#   will be used. This can be used to choose 'fallback' theme implementations,
#   so that if the specific theme hook isn't implemented anywhere, a more
#   generic one will be used. This can allow themes to create specific theme
#   implementations for named objects.
# @param ...
#   Additional arguments to pass along to the theme function.
# @return
#   An HTML string that generates the themed output.
#
def theme():
  global theme_path;
  global theme_engine;
  global static_theme_hooks;
  args = func_get_args();
  hook = array_shift(args);
  if (static_theme_hooks == None):
    init_theme();
    static_theme_hooks = theme_get_registry();
  if (is_array(hook)):
    for candidate in hook:
      if (isset(hooks, candidate)):
        break;
    hook = candidate;
  if (not isset(hooks, hook)):
    return;
  info = static_theme_hooks[hook];
  temp = theme_path;
  # point path_to_theme() to the currently used theme path:
  theme_path = info['theme path'];
  # Include a file if the theme function or preprocess function is held elsewhere.
  if (not empty(info['file'])):
    include_file = info['file'];
    if (isset(info, 'path')):
      include_file = info['path'] + '/' + include_file;
    include_once(include_file);
  if (isset(info, 'function')):
    # The theme call is a function.
    output = call_user_func_array(info['function'], args);
  else:
    # The theme call is a template.
    variables = {
      'template_files' : []
    };
    if (not empty(info['arguments'])):
      count = 0;
      for name,default in info['arguments'].items():
        variables[name] = (args[count] if isset(args[count]) else default);
        count += 1;
    # default render function and extension.
    render_function = 'theme_render_template';
    extension = '.tpl.py';
    # Run through the theme engine variables, if necessary
    if (theme_engine != None):
      # If theme or theme engine is implementing this, it may have
      # a different extension and a different renderer.
      if (info['type'] != 'module'):
        if (function_exists(theme_engine + '_render_template')):
          render_function = theme_engine + '_render_template';
        extension_function = theme_engine + '_extension';
        if (function_exists(extension_function)):
          extension = extension_function();
    if (isset(info['preprocess functions']) and is_array(info['preprocess functions'])):
      # This construct ensures that we can keep a reference through
      # call_user_func_array.
      _variables = drupy.helper.Reference(variables);
      args = (_variables, hook);
      for preprocess_function in info['preprocess functions']:
        if (function_exists(preprocess_function)):
          call_user_func_array(preprocess_function, args);
    # Get suggestions for alternate templates out of the variables
    # that were set. This lets us dynamically choose a template
    # from a list. The order is FILO, so this array is ordered from
    # least appropriate first to most appropriate last.
    suggestions = {};
    if (isset(_variables.val, 'template_files')):
      suggestions = _variables.val['template_files'];
    if (isset(_variables.val, 'template_file')):
      suggestions.append( _variables.val['template_file'] );
    if (suggestions):
      template_file = drupal_discover_template(info['theme paths'], suggestions, extension);
    if (empty(template_file)):
      template_file = info['template'] + extension;
      if (isset(info, 'path')):
        template_file = info['path'] + '/' + template_file;
    output = render_function(template_file, variables);
  # restore path_to_theme()
  theme_path = temp;
  return output;



#
# Choose which template file to actually render. These are all suggested
# templates from themes and modules. Theming implementations can occur on
# multiple levels. All paths are checked to account for this.
#
def drupal_discover_template(paths, suggestions, extension = '.tpl.php'):
  global theme_engine;
  # Loop through all paths and suggestions in FIFO order.
  suggestions = array_reverse(suggestions);
  paths = array_reverse(paths);
  for suggesiton in suggestions:
    if (not empty(suggestion)):
      for path in paths:
        file = path + '/' + suggestion + extension;
        if (file_exists(file)):
          return file;



#
# Return the path to the currently selected theme.
#
def path_to_theme():
  global theme_path;
  if (theme_path == None):
    init_theme();
  return theme_path;



#
# Find overridden theme functions. Called by themes and/or theme engines to
# easily discover theme functions.
#
# @param cache
#   The existing cache of theme hooks to test against.
# @param prefixes
#   An array of prefixes to test, in reverse order of importance.
#
# @return templates
#   The functions found, suitable for returning from hook_theme;
#
def drupal_find_theme_functions(cache, prefixes):
  templates = [];
  functions = get_defined_functions();
  for hook,info in cache.items():
    for prefix in prefixes:
      if (not empty(info['pattern'])):
        matches = preg_grep('/^' + prefix + '_' + info['pattern'] + '/', functions['user']);
        if (matches > 1):
          for match in matches:
            new_hook = str_replace(prefix + '_', '', match);
            templates[new_hook] = {
              'function' : match,
              'arguments' : info['arguments'],
            };
      if (function_exists(prefix + '_' + hook)):
        templates[hook] = {
          'function' : prefix + '_' + hook,
        };
  return templates;


#
# Find overridden theme templates. Called by themes and/or theme engines to
# easily discover templates.
#
# @param cache
#   The existing cache of theme hooks to test against.
# @param extension
#   The extension that these templates will have.
# @param path
#   The path to search.
#
def drupal_find_theme_templates(cache, extension, path):
  global _theme;
  templates = [];
  # Collect paths to all sub-themes grouped by base themes+ These will be
  # used for filtering+ This allows base themes to have sub-themes in its
  # folder hierarchy without affecting the base themes template discovery+ theme_paths = array();
  for theme_info in list_themes():
    if (not empty(theme_info.base_theme)):
      theme_paths[theme_info.base_theme][theme_info.name] = dirname(theme_info.filename);
  for basetheme,subthemes in theme_paths.items():
    for subtheme,subtheme_path in subthemes.items():
      if (isset(theme_paths, subtheme)):
        theme_paths[basetheme] = array_merge(theme_paths[basetheme], theme_paths[subtheme]);
  subtheme_paths = (theme_paths[theme] if isset(theme_paths, theme) else []);
  # Escape the periods in the extension+ regex = str_replace('.', '\.', extension) +'$';
  # Because drupal_system_listing works the way it does, we check for real
  # templates separately from checking for patterns+ files = drupal_system_listing(regex, path, 'name', 0);
  for template,file in files.items():
    # Ignore sub-theme templates for the current theme+ if (strpos(file.filename, str_replace(subtheme_paths, '', file.filename)) !== 0):
    continue;
    # Chop off the remaining extensions if there are any+ template already
    # has the rightmost extension removed, but there might still be more,
    # such as with +tpl.php, which still has +tpl in template at this point+ if ((pos = strpos(template, '.')) !== False):
    template = substr(template, 0, pos);
    # Transform - in filenames to _ to match function naming scheme
    # for the purposes of searching+ hook = strtr(template, '-', '_');
    if (isset(cache, hook)):
      templates[hook] = {
        'template' : template,
        'path' : dirname(file.filename),
      };
  patterns = array_keys(files);
  for hook,info in cache.items():
    if (not empty(info, 'pattern')):
      # Transform _ in pattern to - to match file naming scheme
      # for the purposes of searching+ pattern = strtr(info['pattern'], '_', '-');
      matches = preg_grep('/^'+ pattern +'/', patterns);
      if (matches):
        for match in matches:
          file = substr(match, 0, strpos(match, '.'));
          # Put the underscores back in for the hook name and register this pattern+
          templates[strtr(file, '-', '_')] = {
            'template' : file,
            'path' : dirname(files[match].filename),
            'arguments' : info['arguments'],
          };
  return templates;


#
# Retrieve an associative array containing the settings for a theme+ *
# The final settings are arrived at by merging the default settings,
# the site-wide settings, and the settings defined for the specific theme+ * If no key was specified, only the site-wide theme defaults are retrieved+ *
# The default values for each of settings are also defined in this function+ * To add new settings, add their default values here, and then add form elements
# to system_theme_settings() in system.module+ *
# @param key
#  The template/style value for a given theme+ *
# @return
#   An associative array containing theme settings+ */
def theme_get_settings(key = None):
  defaults = {
    'mission'                       :  '',
    'default_logo'                  :  1,
    'logo_path'                     :  '',
    'default_favicon'               :  1,
    'favicon_path'                  :  '',
    'primary_links'                 :  1,
    'secondary_links'               :  1,
    'toggle_logo'                   :  1,
    'toggle_favicon'                :  1,
    'toggle_name'                   :  1,
    'toggle_search'                 :  1,
    'toggle_slogan'                 :  0,
    'toggle_mission'                :  1,
    'toggle_node_user_picture'      :  0,
    'toggle_comment_user_picture'   :  0,
    'toggle_primary_links'          :  1,
    'toggle_secondary_links'        :  1
  };
  if (module_exists('node')):
    for type,name in node_get_types().items():
      defaults['toggle_node_info_'+ type] = 1;
  settings = array_merge(defaults, variable_get('theme_settings', array()));
  if (key != None):
    settings = array_merge(settings, variable_get(str_replace('/', '_', 'theme_'+ key +'_settings'), []));
  # Only offer search box if search.module is enabled+ if (not module_exists('search') or not user_access('search content')):
    settings['toggle_search'] = 0;
  return settings;



#
# Retrieve a setting for the current theme+ * This function is designed for use from within themes & engines
# to determine theme settings made in the admin interface+ *
# Caches values for speed (use refresh = True to refresh cache)
#
# @param setting_name
#  The name of the setting to be retrieved+ *
# @param refresh
#  Whether to reload the cache of settings+ *
# @return
#   The value of the requested setting, None if the setting does not exist+ */
def theme_get_setting(setting_name, refresh = False):
  global theme_key;
  global static_themegetsetting_settings;
  if (static_themegetsetting_settings == None or refresh):
    static_themegetsetting_settings = theme_get_settings(theme_key);
    themes = list_themes();
    theme_object = themes[theme_key];
    if (static_themegetsetting_settings['mission'] == ''):
      static_themegetsetting_settings['mission'] = variable_get('site_mission', '');
    if (not static_themegetsetting_settings['toggle_mission']):
      static_themegetsetting_settings['mission'] = '';
    if (static_themegetsetting_settings['toggle_logo']):
      if (static_themegetsetting_settings['default_logo']):
        static_themegetsetting_settings['logo'] = base_path() + dirname(theme_object.filename) +'/logo.png';
      elif (static_themegetsetting_settings['logo_path']):
        static_themegetsetting_settings['logo'] = base_path() + static_themegetsetting_settings['logo_path'];
    if (static_themegetsetting_settings['toggle_favicon']):
      if (static_themegetsetting_settings['default_favicon']):
        favicon = (dirname(theme_object.filename) +'/favicon.ico');
        if (file_exists(favicon)):
          static_themegetsetting_settings['favicon'] = base_path() + favicon;
        else:
          static_themegetsetting_settings['favicon'] = base_path() +'misc/favicon.ico';
      elif (static_themegetsetting_settings['favicon_path']):
        static_themegetsetting_settings['favicon'] = base_path() + static_themegetsetting_settings['favicon_path'];
      else:
        static_themegetsetting_settings['toggle_favicon'] = False;
  return (static_themegetsetting_settings[setting_name] if isset(settings, setting_name) else None);



#
# Render a system default template, which is essentially a PHP template+ *
# @param file
#   The filename of the template to render+ * @param variables
#   A keyed array of variables that will appear in the output+ *
# @return
#   The output generated by the template+ */
def theme_render_template(file, variables):
  extract(variables, EXTR_SKIP);  # Extract the variables to a local namespace
  ob_start();                     # Start output buffering
  include( "./file" );               # Include the file
  contents = ob_get_contents();   # Get the contents of the buffer
  ob_end_clean();                 # End buffering and discard
  return contents;                # Return the contents



#
# @defgroup themeable Default theme implementations
# @{
# Functions and templates that present output to the user, and can be
# implemented by themes+ *
# Drupal's presentation layer is a pluggable system known as the theme
# layer+ Each theme can take control over most of Drupal's output, and
# has complete control over the CSS+ *
# Inside Drupal, the theme layer is utilized by the use of the theme()
# function, which is passed the name of a component (the theme hook)
# and several arguments+ For example, theme('table', header, rows);
# Additionally, the theme() function can take an array of theme
# hooks, which can be used to provide 'fallback' implementations to
# allow for more specific control of output+ For example, the function:
# theme(array('table__foo', 'table'), header, rows) would look to see if
# 'table__foo' is registered anywhere; if it is not, it would 'fall back'
# to the generic 'table' implementation+ This can be used to attach specific
# theme functions to named objects, allowing the themer more control over
# specific types of output+ *
# As of Drupal 6, every theme hook is required to be registered by the
# module that owns it, so that Drupal can tell what to do with it and
# to make it simple for themes to identify and override the behavior
# for these calls+ *
# The theme hooks are registered via hook_theme(), which returns an
# array of arrays with information about the hook+ It describes the
# arguments the function or template will need, and provides
# defaults for the template in case they are not filled in+ If the default
# implementation is a function, by convention it is named theme_HOOK()+ *
# Each module should provide a default implementation for themes that
# it registers+ This implementation may be either a function or a template;
# if it is a function it must be specified via hook_theme()+ By convention,
# default implementations of theme hooks are named theme_HOOK+ Default
# template implementations are stored in the module directory+ *
# Drupal's default template renderer is a simple PHP parsing engine that
# includes the template and stores the output+ Drupal's theme engines
# can provide alternate template engines, such as XTemplate, Smarty and
# PHPTal+ The most common template engine is PHPTemplate (included with
# Drupal and implemented in phptemplate.engine, which uses Drupal's default
# template renderer+ *
# In order to create theme-specific implementations of these hooks,
# themes can implement their own version of theme hooks, either as functions
# or templates+ These implementations will be used instead of the default
# implementation+ If using a pure +theme without an engine, the +theme is
# required to implement its own version of hook_theme() to tell Drupal what
# it is implementing; themes utilizing an engine will have their well-named
# theming functions automatically registered for them+ While this can vary
# based upon the theme engine, the standard set by phptemplate is that theme
# functions should be named either phptemplate_HOOK or THEMENAME_HOOK+ For
# example, for Drupal's default theme (Garland) to implement the 'table' hook,
# the phptemplate.engine would find phptemplate_table() or garland_table()+ * The ENGINE_HOOK() syntax is preferred, as this can be used by sub-themes
# (which are themes that share code but use different stylesheets)+ *
# The theme system is described and defined in theme.inc+ *
# @see theme()
# @see hook_theme()
#
#
# Formats text for emphasized display in a placeholder inside a sentence+ * Used automatically by t()+ *
# @param text
#   The text to format (plain-text)+ * @return
#   The formatted text (html)+ */
def theme_placeholder(text):
  return '<em>'+ check_plain(text) +'</em>';




#
# Return a themed set of status and/or error messages+ The messages are grouped
# by type+ *
# @param display
#   (optional) Set to 'status' or 'error' to display only messages of that type+ *
# @return
#   A string containing the messages+ */
def theme_status_messages(display = None):
  output = '';
  for type,messages in drupal_get_messages(display).items():
    output += "<div class=\"messages type\">\n";
    if (count(messages) > 1):
      output += " <ul>\n";
      for message in messages:
        output += '  <li>'+ message +"</li>\n";
      output += " </ul>\n";
    else:
      output += messages[0];
    output += "</div>\n";
  return output;



#
# Return a themed set of links+ *
# @param links
#   A keyed array of links to be themed+ * @param attributes
#   A keyed array of attributes
# @return
#   A string containing an unordered list of links+ */
def theme_links(links, attributes = {'class' : 'links'}):
  output = '';
  if (count(links) > 0):
    output = '<ul'+ drupal_attributes(attributes) +'>';
    num_links = count(links);
    i = 1;
    for key,link in links.items():
      _class = key;
      # Add first, last and active classes to the list of links to help out themers+
      if (i == 1):
        _class += ' first';
      if (i == num_links):
        _class += ' last';
      if (isset(link['href']) and (link['href'] == _GET['q'] or (link['href'] == '<front>' and drupal_is_front_page()))):
        _class += ' active';
      output += '<li class="'+ _class +'">';
      if (isset(link['href'])):
        # Pass in link as options, they share the same keys
        output += l(link['title'], link['href'], link);
      elif (not empty(link, 'title')):
        # Some links are actually not links, but we wrap these in <span> for adding title and class attributes
        if (empty(link, 'html')):
          link['title'] = check_plain(link['title']);
        span_attributes = '';
        if (isset(link, 'attributes')):
          span_attributes = drupal_attributes(link['attributes']);
        output += '<span'+ span_attributes +'>'+ link['title'] +'</span>';
      i += 1;
      output += "</li>\n";
    output += '</ul>';
  return output;



#
# Return a themed image+ *
# @param path
#   Either the path of the image file (relative to base_path()) or a full URL+ * @param alt
#   The alternative text for text-based browsers+ * @param title
#   The title text is displayed when the image is hovered in some popular browsers+ * @param attributes
#   Associative array of attributes to be placed in the img tag+ * @param getsize
#   If set to True, the image's dimension are fetched and added as width/height attributes+ * @return
#   A string containing the image tag+ */
def theme_image(path, alt = '', title = '', attributes = None, getsize = True):
  imageSize = getimagesize(path);
  if (not getsize or (is_file(path) and (imageSize != False))):
    width, height, type, image_attributes = imageSize; 
    attributes = drupal_attributes(attributes);
    url =  path if (url(path) == path) else (base_path() + path);
    return '<img src="'+ check_url(url) +'" alt="'+ check_plain(alt) +'" title="'+ check_plain(title) +'" '+ (image_attributes if not empty(image_attributes) else '') + attributes +' />';



#
# Return a themed breadcrumb trail+ *
# @param breadcrumb
#   An array containing the breadcrumb links+ * @return a string containing the breadcrumb output+ */
def theme_breadcrumb(breadcrumb):
  if (not empty(breadcrumb)):
    return '<div class="breadcrumb">'+ implode(' » ', breadcrumb) +'</div>';



#
# Return a themed help message+ *
# @return a string containing the helptext for the current page+ */
def theme_help():
  help = menu_get_active_help()
  if (help != False):
    return '<div class="help">'+ help +'</div>';



#
# Return a themed submenu, typically displayed under the tabs+ *
# @param links
#   An array of links+ */
def theme_submenu(links):
  return '<div class="submenu">'+ implode(' | ', links) +'</div>';



#
# Return a themed table+ *
# @param header
#   An array containing the table headers+ Each element of the array can be
#   either a localized string or an associative array with the following keys:
#   - "data": The localized title of the table column+ *   - "field": The database field represented in the table column (required if
#     user is to be able to sort on this column)+ *   - "sort": A default sort order for this column ("asc" or "desc")+ *   - Any HTML attributes, such as "colspan", to apply to the column header cell+ * @param rows
#   An array of table rows+ Every row is an array of cells, or an associative
#   array with the following keys:
#   - "data": an array of cells
#   - Any HTML attributes, such as "class", to apply to the table row+ *
#   Each cell can be either a string or an associative array with the following keys:
#   - "data": The string to display in the table cell+ *   - "header": Indicates this cell is a header+ *   - Any HTML attributes, such as "colspan", to apply to the table cell+ *
#   Here's an example for rows:
#   @verbatim
#   rows = array(
#     // Simple row
#     array(
#       'Cell 1', 'Cell 2', 'Cell 3'
#     ),
#     // Row with attributes on the row and some of its cells+ *     array(
#       'data' : array('Cell 1', array('data' : 'Cell 2', 'colspan' : 2)), 'class' : 'funky'
#     )
#   );
#   @endverbatim
#
# @param attributes
#   An array of HTML attributes to apply to the table tag+ * @param caption
#   A localized string to use for the <caption> tag+ * @return
#   An HTML string representing the table+ */
def theme_table(header, rows, attributes = [], caption = None):
  # Add sticky headers, if applicable+
  if (count(header) > 0):
    drupal_add_js('misc/tableheader.js');
    # Add 'sticky-enabled' class to the table to identify it for JS+
    # This is needed to target tables constructed by this function+
    attributes['class'] = ('sticky-enabled' if empty(attributes['class']) else (attributes['class'] +' sticky-enabled'));
  output = '<table'+ drupal_attributes(attributes) +">\n";
  if (caption != None):
    output += '<caption>'+ caption +"</caption>\n";
  # Format the table header:
  if (count(header) > 0):
    ts = tablesort_init(header);
    # HTML requires that the thead tag has tr tags in it follwed by tbody
    # tags+
    #Using ternary operator to check and see if we have any rows+
    output += (' <thead><tr>' if (count(rows) > 1) else ' <tr>');
    for cell in header:
      cell = tablesort_header(cell, header, ts);
      output += _theme_table_cell(cell, True);
    # Using ternary operator to close the tags based on whether or not there are rows
    output += (" </tr></thead>\n" if (count(rows) > 0) else "</tr>\n");
  else:
    ts = [];
  # Format the table rows:
  if (count(rows) > 0):
    output += "<tbody>\n";
    flip = {'even' : 'odd', 'odd' : 'even'};
    _class = 'even';
    for number,row in rows.items():
      attributes = [];
      # Check if we're dealing with a simple or complex row
      if (isset(row, 'data')):
        for key,value in row.items():
          if (key == 'data'):
            cells = value;
          else:
            attributes[key] = value;
      else:
        cells = row;
      if (count(cells) > 0):
        # Add odd/even class
        _class = flip[_class];
        if (isset(attributes, 'class')):
          attributes['class'] += ' '+ _class;
        else:
          attributes['class'] = _class;
        # Build row
        output += ' <tr'+ drupal_attributes(attributes) +'>';
        i = 0;
        for cell in cells:
          cell = tablesort_cell(cell, header, ts, i);
          i += 1;
          output += _theme_table_cell(cell);
        output += " </tr>\n";
    output += "</tbody>\n";
  output += "</table>\n";
  return output;




#
# Returns a header cell for tables that have a select all functionality+
def theme_table_select_header_cell():
  drupal_add_js('misc/tableselect.js');
  return {'class' : 'select-all'};


#
# Return a themed sort icon+ *
# @param style
#   Set to either asc or desc+
# This sets which icon to show+
#  @return
#   A themed sort icon+ */
def theme_tablesort_indicator(style):
  if (style == "asc"):
    return theme('image', 'misc/arrow-asc.png', t('sort icon'), t('sort ascending'));
  else:
    return theme('image', 'misc/arrow-desc.png', t('sort icon'), t('sort descending'));



#
# Return a themed box+ *
# @param title
#   The subject of the box+
# @param content
#   The content of the box+
# @param region
#   The region in which the box is displayed+
# @return
#   A string containing the box output+ */
def theme_box(title, content, region = 'main'):
  output = '<h2 class="title">'+ title +'</h2><div>'+ content +'</div>';
  return output;


#
# Return a themed marker, useful for marking new or updated
# content+ *
# @param type
#   Number representing the marker type to display
# @see MARK_NEW, MARK_UPDATED, MARK_READ
# @return
#   A string containing the marker+ */
def theme_mark(type = MARK_NEW):
  global user;
  if (user.uid > 0):
    if (type == MARK_NEW):
      return ' <span class="marker">'+ t('new') +'</span>';
    elif (type == MARK_UPDATED):
      return ' <span class="marker">'+ t('updated') +'</span>';



#
# Return a themed list of items+ *
# @param items
#   An array of items to be displayed in the list+ If an item is a string,
#   then it is used as is+ If an item is an array, then the "data" element of
#   the array is used as the contents of the list item+ If an item is an array
#   with a "children" element, those children are displayed in a nested list+ *   All other elements are treated as attributes of the list item element+ * @param title
#   The title of the list+ * @param attributes
#   The attributes applied to the list element+ * @param type
#   The type of list to return (e.g+ "ul", "ol")
# @return
#   A string containing the list output+ */
def theme_item_list(items = [], title = None, type = 'ul', attributes = None):
  output = '<div class="item-list">';
  if (title != None):
    output += '<h3>'+ title +'</h3>';
  if (not empty(items)):
    output += "<type"+ drupal_attributes(attributes) +'>';
    num_items = count(items);
    for i,item in items.items():
      attributes = {};
      children = {};
      if (is_array(item)):
        for key,value in item.items():
          if (key == 'data'):
            data = value;
          elif (key == 'children'):
            children = value;
          else:
            attributes[key] = value;
      else:
        data = item;
      if (count(children) > 0):
        data += theme_item_list(children, None, type, attributes); # Render nested list
      if (i == 0):
        attributes['class'] = ('first' if empty(attributes['class']) else (attributes['class'] +' first'));
      if (i == num_items - 1):
        attributes['class'] = ('last' if empty(attributes['class']) else (attributes['class'] +' last'));
      output += '<li'+ drupal_attributes(attributes) +'>'+ data +"</li>\n";
    output += "</type>";
  output += '</div>';
  return output;



#
# Returns code that emits the 'more help'-link+ */
def theme_more_help_link(url):
  return '<div class="more-help-link">' +  t('<a href="@link">More help</a>', {'@link' : check_url(url)}) + '</div>';



#
# Return code that emits an XML icon+ *
# For most use cases, this function has been superseded by theme_feed_icon()+ *
# @see theme_feed_icon()
# @param url
#   The url of the feed+ */
def theme_xml_icon(url):
  image = theme('image', 'misc/xml.png', t('XML feed'), t('XML feed'));
  if (image):
    return '<a href="'+ check_url(url) +'" class="xml-icon">'+ image +'</a>';


#
# Return code that emits an feed icon+ *
# @param url
#   The url of the feed+ * @param title
#   A descriptive title of the feed+ */
def theme_feed_icon(url, title):
  image = theme('image', 'misc/feed.png', t('Syndicate content'), title)
  if (image):
    return '<a href="'+ check_url(url) +'" class="feed-icon">'+ image +'</a>';


#
# Returns code that emits the 'more' link used on blocks+ *
# @param url
#   The url of the main page
# @param title
#   A descriptive verb for the link, like 'Read more'
#
def theme_more_link(url, title):
  return '<div class="more-link">'+ t('<a href="@link" title="@title">more</a>', {'@link' : check_url(url), '@title' : title}) +'</div>';



#
# Execute hook_footer() which is run at the end of the page right before the
# close of the body tag+ *
# @param main (optional)
#   Whether the current page is the front page of the site+ * @return
#   A string containing the results of the hook_footer() calls+ */
def theme_closure(_main = 0):
  footer = module_invoke_all('footer', _main);
  return implode("\n", footer) + drupal_get_js('footer');



#
# Return a set of blocks available for the current user+ *
# @param region
#   Which set of blocks to retrieve+ * @return
#   A string containing the themed blocks for this region+ */
def theme_blocks(region):
  output = '';
  list = block_list(region);
  if (list):
    for key,block in list.items():
      # key == <i>module</i>_<i>delta</i>
      output += theme('block', block);
  # Add any content assigned to this region through drupal_set_content() calls+
  output += drupal_get_content(region);
  return output;



#
# Format a username+ *
# @param object
#   The user object to format, usually returned from user_load()+ * @return
#   A string containing an HTML link to the user's page if the passed object
#   suggests that this is a site user+
# Otherwise, only the username is returned+ */
def theme_username(_object):
  nameSet = (isset(_object, 'name') and not empty(_object.name));
  if (_object.uid > 0 and nameSet):
    # Shorten the name when it is too long or it will break many tables+
    if (drupal_strlen(_object.name) > 20):
      name = drupal_substr(_object.name, 0, 15) +'...';
    else:
      name = _object.name;
    if (user_access('access user profiles')):
      output = l(name, 'user/'+ _object.uid, {'title' : t('View user profile.')});
    else:
      output = check_plain(name);
  elif (nameSet):
    # Sometimes modules display content composed by people who are
    # not registered members of the site (e.g+ mailing list or news
    # aggregator modules)+ This clause enables modules to display
    # the True author of the content+
    if (isset(_object, 'homepage') and not empty(_object.homepage)):
      output = l(_object.name, _object.homepage, {'rel' : 'nofollow'});
    else:
      output = check_plain(_object.name);
    output += ' ('+ t('not verified') +')';
  else:
    output = variable_get('anonymous', t('Anonymous'));
  return output;



#
# Return a themed progress bar+ *
# @param percent
#   The percentage of the progress+ * @param message
#   A string containing information to be displayed+ * @return
#   A themed HTML string representing the progress bar+ */
def theme_progress_bar(percent, message):
  output = '<div id="progress" class="progress">';
  output += '<div class="bar"><div class="filled" style="width: '+ percent +'%"></div></div>';
  output += '<div class="percentage">'+ percent +'%</div>';
  output += '<div class="message">'+ message +'</div>';
  output += '</div>';
  return output;



#
# Create a standard indentation div+ Used for drag and drop tables+ *
# @param size
#   Optional+ The number of indentations to create+ * @return
#   A string containing indentations+ */
def theme_indentation(size = 1):
  output = '';
  for n in range(0, size):
    output += '<div class="indentation">&nbsp;</div>';
  return output;


#
# @} End of "defgroup themeable"+ */

def _theme_table_cell(cell, header = False):
  attributes = '';
  if (is_array(cell)):
    data = (cell['data'] if isset(cell, 'data') else '');
    header |= isset(cell, 'header');
    del(cell['data']);
    del(cell['header']);
    attributes = drupal_attributes(cell);
  else:
    data = cell;
  if (header):
    output = "<th %(attributes)s>%(data)s</th>" % { 'data' : data, 'attributes' : attributes };
  else:
    output = "<td %(attributes)s>%(data)s</td>" % { 'data' : data, 'attributes' : attributes };
  return output;



#
# Adds a default set of helper variables for preprocess functions and
# templates+ This comes in before any other preprocess function which makes
# it possible to be used in default theme implementations (non-overriden
# theme functions)+ */
def template_preprocess(_variables, hook):
  global user;
  global static_template_preprocess_count;
  DrupyHelper.Reference.check(_variables);
  if (static_template_preprocess_count == None):
    static_template_preprocess_count = {};
  # Track run count for each hook to provide zebra striping+
  # See "template_preprocess_block()" which provides the same feature specific to blocks+
  static_template_preprocess_count[hook] = \
    (static_template_preprocess_count[hook] \
      if (isset(static_template_preprocess_count, hook) and \
        is_int(static_template_preprocess_count[hook])) else 1);
  _variables.val['zebra'] = ('odd' if ((static_template_preprocess_count[hook] % 2) > 1) else 'even');
  static_template_preprocess_count[hook] += 1;
  _variables.val['id'] = static_template_preprocess_count[hook];
  # Tell all templates where they are located+
  variables['directory'] = path_to_theme();
  # Set default variables that depend on the database+
  variables['is_admin']            = False;
  _variables.val['is_front']            = False;
  _variables.val['logged_in']           = False;
  _variables.val['db_is_active'] = db_is_active() ;
  if (_variables.val['db_is_active'] and not defined('MAINTENANCE_MODE')):
    # Check for administrators+
    if (user_access('access administration pages')):
      _variables.val['is_admin'] = True;
    # Flag front page status+
    variables['is_front'] = drupal_is_front_page();
    # Tell all templates by which kind of user they're viewed+
    variables['logged_in'] = (user.uid > 0);
    # Provide user object to all templates
    _variables.val['user'] = user;



#
# Process variables for page.tpl.php
#
# Most themes utilize their own copy of page.tpl.php+ The default is located
# inside "modules/system/page.tpl.php"+ Look in there for the full list of
# variables+ *
# Uses the arg() function to generate a series of page template suggestions
# based on the current path+ *
# Any changes to variables in this preprocessor should also be changed inside
# template_preprocess_maintenance_page() to keep all them consistent+ *
# The variables array contains the following arguments:
# - content
# - show_blocks
#
# @see page.tpl.php
#
def template_preprocess_page(_variables):
  global _theme;
  global language;
  DrupyHelper.Reference.check(_variables);
  # Add favicon
  if (theme_get_setting('toggle_favicon')):
    drupal_set_html_head('<link rel="shortcut icon" href="'+ check_url(theme_get_setting('favicon')) +'" type="image/x-icon" />');
  # Populate all block regions+
  regions = system_region_list(theme);
  # Load all region content assigned via blocks+
  for region in array_keys(regions):
    # Prevent left and right regions from rendering blocks when 'show_blocks' == False+
    if (not (not _variables.val['show_blocks'] and (region == 'left' or region == 'right'))):
      blocks = theme('blocks', region);
    else:
      blocks = '';
    # Assign region to a region variable+
    if (isset(variables, region)):
      _variables.val[region] += blocks
    else:
      _variables.val[region] = blocks;
  # Set up layout variable+
  variables['layout'] = 'none';
  if (not empty(_variables.val['left'])):
    _variables.val['layout'] = 'left';
  if (not empty(_variables.val['right'])):
    variables['layout'] = ('both' if (variables['layout'] == 'left') else 'right');
  # Set mission when viewing the frontpage+
  if (drupal_is_front_page()):
    mission = filter_xss_admin(theme_get_setting('mission'));
  else:
    mission = None;
  # Construct page title
  if (drupal_get_title()):
    head_title = [strip_tags(drupal_get_title()), variable_get('site_name', 'Drupal')];
  else:
    head_title = [variable_get('site_name', 'Drupal')];
    if (variable_get('site_slogan', '')):
      head_title.append( variable_get('site_slogan', '') );
  _variables.val['head_title']        = implode(' | ', head_title);
  _variables.val['base_path']         = base_path();
  _variables.val['front_page']        = url();
  _variables.val['breadcrumb']        = theme('breadcrumb', drupal_get_breadcrumb());
  _variables.val['feed_icons']        = drupal_get_feeds();
  _variables.val['footer_message']    = filter_xss_admin(variable_get('site_footer', False));
  _variables.val['head']              = drupal_get_html_head();
  _variables.val['help']              = theme('help');
  _variables.val['language']          = language;
  _variables.val['language'].dir      = ('rtl' if (isset(language, 'direction') and not empty(language.direction)) else 'ltr');
  _variables.val['logo']              = theme_get_setting('logo');
  _variables.val['messages']          = (theme('status_messages') if variables['show_messages'] else '');
  _variables.val['mission']           = (mission if (mission != None) else '');
  _variables.val['primary_links']     = (menu_primary_links() if theme_get_setting('toggle_primary_links') else []);
  _variables.val['secondary_links']   = (menu_secondary_links() if theme_get_setting('toggle_secondary_links') else []);
  _variables.val['search_box']        = (drupal_get_form('search_theme_form') if theme_get_setting('toggle_search') else '');
  _variables.val['site_name']         = (variable_get('site_name', 'Drupal') if theme_get_setting('toggle_name') else '');
  _variables.val['site_slogan']       = (variable_get('site_slogan', '') if theme_get_setting('toggle_slogan') else '');
  _variables.val['css']               = drupal_add_css();
  _variables.val['styles']            = drupal_get_css();
  _variables.val['scripts']           = drupal_get_js();
  _variables.val['tabs']              = theme('menu_local_tasks');
  _variables.val['title']             = drupal_get_title();
  # Closure should be filled last+
  _variables.val['closure']           = theme('closure');
  node = menu_get_object();
  if (node):
    _variables.val['node'] = node;
  # Compile a list of classes that are going to be applied to the body element+
  # This allows advanced theming based on context (home page, node of certain type, etc.)+
  body_classes = [];
  # Add a class that tells us whether we're on the front page or not+
  body_classes.append( ('front' if _variables.val['is_front'] else 'not-front') );
  # Add a class that tells us whether the page is viewed by an authenticated user or not+
  body_classes.append( ('logged-in' if _variables.val['logged_in'] else 'not-logged-in') );
  # Add arg(0) to make it possible to theme the page depending on the current page
  # type (e.g+ node, admin, user, etc.)+ To avoid illegal characters in the class,
  # we're removing everything disallowed+ We are not using 'a-z' as that might leave
  # in certain international characters (e.g+ German umlauts)+
  body_classes.append( preg_replace('not [^abcdefghijklmnopqrstuvwxyz0-9-_]+not s', '', 'page-'+ form_clean_id(drupal_strtolower(arg(0)))) );
  # If on an individual node page, add the node type+
  if (isset(_variables.val, 'node') and _variables.val['node'].type):
    body_classes.append( 'node-type-'+ form_clean_id(_variables.val['node'].type) );
  # Add information about the number of sidebars+
  if (_variables.val['layout'] == 'both'):
    body_classes.append( 'two-sidebars' );
  elif (_variables.val['layout'] == 'none'):
    body_classes.append( 'no-sidebars' );
  else:
    body_classes.append( 'one-sidebar sidebar-'+ _variables.val['layout'] );
  # Implode with spaces+
  _variables.val['body_classes'] = implode(' ', body_classes);
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
    _arg = arg(i);
    if (_arg == False or _arg == None):
      break;
    else:
      i += 1;
    suggestions.append( suggestion +'-'+ _arg );
    if (not is_numeric(_arg)):
      suggestion += '-'+ _arg;
  if (drupal_is_front_page()):
    suggestions.append( 'page-front' );
  if (not empty(suggestions)):
    _variables.val['template_files'] = suggestions;




#
# Process variables for node.tpl.php
#
# Most themes utilize their own copy of node.tpl.php+ The default is located
# inside "modules/node/node.tpl.php"+ Look in there for the full list of
# variables+ *
# The variables array contains the following arguments:
# - node
# - teaser
# - page
#
# @see node.tpl.php
#
def template_preprocess_node(_variables):
  DrupyHelper.Reference.check(variables);
  node = _variables.val['node'];
  if (module_exists('taxonomy')):
    _variables.val['taxonomy'] = taxonomy_link('taxonomy terms', node);
  else:
    _variables.val['taxonomy'] = {};
  if (_variables.val['teaser'] and node.teaser):
    _variables.val['content'] = node.teaser;
  elif (isset(node, 'body')):
    _variables.val['content'] = node.body;
  else:
    _variables.val['content'] = '';
  _variables.val['date']      = format_date(node.created);
  _variables.val['links']     = (theme('links', node.links, {'class' : 'links inline'}) if (not empty(node.links)) else '');
  _variables.val['name']      = theme('username', node);
  _variables.val['node_url']  = url('node/'+ node.nid);
  _variables.val['terms']     = theme('links', _variables.val['taxonomy'], {'class' : 'links inline'});
  _variables.val['title']     = check_plain(node.title);
  # Flatten the node object's member fields+
  _variables.val = array_merge(drupy_array(node), _variables.val);
  # Display info only on certain node types+
  if (theme_get_setting('toggle_node_info_'+ node.type)):
    _variables.val['submitted'] = theme('node_submitted', node);
    _variables.val['picture'] = (theme('user_picture', node) if theme_get_setting('toggle_node_user_picture') else '');
  else:
    _variables.val['submitted'] = '';
    _variables.val['picture'] = '';
  # Clean up name so there are no underscores+
  _variables.val['template_files'].append( 'node-'+ node.type );




#
# Process variables for block.tpl.php
#
# Prepare the values passed to the theme_block function to be passed
# into a pluggable template engine+ Uses block properties to generate a
# series of template file suggestions+ If none are found, the default
# block.tpl.php is used+ *
# Most themes utilize their own copy of block.tpl.php+ The default is located
# inside "modules/system/block.tpl.php"+ Look in there for the full list of
# variables+ *
# The variables array contains the following arguments:
# - block
#
# @see block.tpl.php
#
def template_preprocess_block(_variables):
  global static_templatepreprocessblock_blockcounter;
  DrupyHelper.Reference.check(_variables);
  if (static_templatepreprocessblock_blockcounter == None):
    static_templatepreprocessblock_blockcounter = {};
  # All blocks get an independent counter for each region+
  if (not isset(static_templatepreprocessblock_blockcounter, _variables.val['block'].region)):
    static_templatepreprocessblock_blockcounter[_variables.val['block'].region] = 1;
  # Same with zebra striping+
  _variables.val['block_zebra'] = ('odd' if ((static_templatepreprocessblock_blockcounter[_variables.val['block'].region] % 2) > 0) else 'even');
  _variables.val['block_id'] = static_templatepreprocessblock_blockcounter[_variables.val['block'].region];
  static_templatepreprocessblock_blockcounter[_variables.val['block'].region] += 1;
  _variables.val['template_files'].append( 'block-'+ _variables.val['block'].region );
  _variables.val['template_files'].append('block-'+ _variables.val['block'].module );
  _variables.val['template_files'].append( 'block-'+ _variables.val['block'].module +'-'+ _variables.val['block'].delta );



