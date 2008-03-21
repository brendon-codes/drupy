# Id: theme.maintenance.inc,v 1.11 2008/02/06 19:38:26 dries Exp $
#
# @file
# Theming for maintenance pages.
#
#
# Sets up the theming system for site installs, updates and when the site is
# in off-line mode. It also applies when the database is unavailable.
#
# Minnelli is always used for the initial install and update operations. In
# other cases, "settings.php" must have a "maintenance_theme" key set for the
# conf variable in order to change the maintenance theme.
#


#
# Set globals
#
set_global('theme_path');
set_global('_theme');


def _drupal_maintenance_theme():
  global _theme, theme_key;
  # If theme is already set, assume the others are set too, and do nothing.
  if (_theme != None):
    return;
  require_once( './includes/path.py' );
  require_once( './includes/theme.py' );
  require_once( './includes/common.py' );
  require_once( './includes/unicode.py' );
  require_once( './includes/file.py' );
  require_once( './includes/module.py' );
  require_once( './includes/database.py' );
  unicode_check();
  # Install and update pages are treated differently to prevent theming overrides.
  if (defined('MAINTENANCE_MODE') and (MAINTENANCE_MODE == 'install' or MAINTENANCE_MODE == 'update')):
    _theme = 'minnelli';
  else:
    # Load module basics (needed for hook invokes).
    module_list['system']['filename'] = 'modules/system/system.py';
    module_list['filter']['filename'] = 'modules/filter/filter.py';
    module_list(True, False, False, module_list);
    drupal_load('module', 'system');
    drupal_load('module', 'filter');
    _theme = variable_get('maintenance_theme', 'minnelli');
  themes = list_themes();
  # Store the identifier for retrieving theme settings with.
  theme_key = _theme;
  # Find all our ancestor themes and put them in an array.
  base_theme = array();
  ancestor = _theme;
  while (ancestor and isset(themes[ancestor], base_theme)):
    new_base_theme = themes[themes[ancestor].base_theme];
    base_theme.append(new_base_theme);
    ancestor = themes[ancestor].base_theme;
  _init_theme(themes[theme], array_reverse(base_theme), '_theme_load_offline_registry');
  # These are usually added from system_init() -except maintenance.css.
  # When the database is inactive it's not called so we add it here.
  drupal_add_css(drupal_get_path('module', 'system') + '/defaults.css', 'module');
  drupal_add_css(drupal_get_path('module', 'system') + '/system.css', 'module');
  drupal_add_css(drupal_get_path('module', 'system') + '/system-menus.css', 'module');
  drupal_add_css(drupal_get_path('module', 'system') + '/maintenance.css', 'module');



#
# This builds the registry when the site needs to bypass any database calls.
#
def _theme_load_offline_registry(this_theme, base_theme = None, theme_engine = None):
  registry = _theme_build_registry(this_theme, base_theme, theme_engine);
  _theme_set_registry(registry);


#
# Return a themed list of maintenance tasks to perform.
#
# @ingroup themeable
#
def theme_task_list(items, active = None):
  done = ((active == None) or (isset(items, active)));
  output = '<ol class="task-list">';
  for k in items:
    item = items[k];
    if (active == k):
      _class = 'active';
      done = false;
    else:
      _class = ('done' if done else '');
    output += '<li class="' + _class + '">' + item + '</li>';
  output += '</ol>';
  return output;



#
# Generate a themed installation page.
#
# Note: this function is not themeable.
#
# @param content
#   The page content to show.
#
def theme_install_page(content):
  global theme_path;
  drupal_set_header('Content-Type: text/html; charset=utf-8');
  # Assign content.
  variables['content'] = content;
  # Delay setting the message variable so it can be processed below.
  variables['show_messages'] = False;
  # The maintenance preprocess function is recycled here.
  template_preprocess_maintenance_page(variables);
  # Special handling of error messages
  messages = drupal_set_message();
  if (isset(messages, 'error')):
    title = (st('The following errors must be resolved before you can continue the installation process') if (count(messages['error']) > 1) else st('The following error must be resolved before you can continue the installation process'));
    variables['messages'] += '<h3>' + title + ':</h3>';
    variables['messages'] += theme('status_messages', 'error');
    variables['content'] += '<p>' + st('Please check the error messages and <a href="!url">try again</a>.', {'!url' : request_uri()}) + '</p>';
  # Special handling of warning messages
  if (isset(messages, 'warning')):
    title = (st('The following installation warnings should be carefully reviewed') if (count(messages['warning']) > 1) else st('The following installation warning should be carefully reviewed'));
    variables['messages'] += '<h4>' + title + ':</h4>';
    variables['messages'] += theme('status_messages', 'warning');
  # Special handling of status messages
  if (isset(messages, 'status')):
    title = (st('The following installation warnings should be carefully reviewed, but in most cases may be safely ignored') if (count(messages['status']) > 1) else st('The following installation warning should be carefully reviewed, but in most cases may be safely ignored'));
    variables['messages'] += '<h4>' + title + ':</h4>';
    variables['messages'] += theme('status_messages', 'status');
  # This was called as a theme hook (not template), so we need to
  # fix path_to_theme() for the template, to point at the actual
  # theme rather than system module as owner of the hook.
  theme_path = 'themes/garland';
  return theme_render_template('themes/garland/maintenance-page.tpl.py', variables);



#
# Generate a themed update page.
#
# Note: this function is not themeable.
#
# @param content
#   The page content to show.
# @param show_messages
#   Whether to output status and error messages.
#   FALSE can be useful to postpone the messages to a subsequent page.
#
def theme_update_page(content, show_messages = True):
  global theme_path;
  # Set required headers.
  drupal_set_header('Content-Type: text/html; charset=utf-8');
  # Assign content and show message flag.
  variables['content'] = content;
  variables['show_messages'] = show_messages;
  # The maintenance preprocess function is recycled here.
  template_preprocess_maintenance_page(variables);
  # Special handling of warning messages.
  messages = drupal_set_message();
  if (isset(messages['warning'])):
    title = ('The following update warnings should be carefully reviewed before continuing' if (count(messages['warning']) > 1) else 'The following update warning should be carefully reviewed before continuing');
    variables['messages'] += '<h4>' + title + ':</h4>';
    variables['messages'] += theme('status_messages', 'warning');
  # This was called as a theme hook (not template), so we need to
  # fix path_to_theme() for the template, to point at the actual
  # theme rather than system module as owner of the hook.
  theme_path = 'themes/garland';
  return theme_render_template('themes/garland/maintenance-page.tpl.php', variables);



#
# The variables generated here is a mirror of template_preprocess_page().
# This preprocessor will run it's course when theme_maintenance_page() is
# invoked. It is also used in theme_install_page() and theme_update_page() to
# keep all the variables consistent.
#
# An alternate template file of "maintenance-page-offline.tpl.php" can be
# used when the database is offline to hide errors and completely replace the
# content.
#
# The variables array contains the following arguments:
# - content
# - show_blocks
#
# @see maintenance-page.tpl.php
#
def template_preprocess_maintenance_page(variables):
  global _theme;
  # Add favicon
  if (theme_get_setting('toggle_favicon')):
    drupal_set_html_head('<link rel="shortcut icon" href="' + check_url(theme_get_setting('favicon')) + '" type="image/x-icon" />');
  # Retrieve the theme data to list all available regions.
  theme_data = _system_theme_data();
  regions = theme_data[_theme].i





  