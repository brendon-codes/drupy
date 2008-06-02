# $Id: theme.maintenance.inc,v 1.13 2008/04/28 09:25:26 dries Exp $


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file theme_maintenance.py (ported from Drupal's theme.maintenance.inc)
#  Theming for maintenance pages.
#  Sets up the theming system for site installs, updates and when the site is
#  in off-line mode. It also applies when the database is unavailable.
#  Minnelli is always used for the initial install and update operations. In
#  other cases, "settings.php" must have a "maintenance_theme" key set for the
#  conf variable in order to change the maintenance theme.
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


#
# Set globals
#
theme_path = None
theme_ = None


def _drupal_maintenance_theme():
  global theme_, theme_key
  # If theme is already set, assume the others are set too, and do nothing.
  if (theme_ != None):
    return
  require_once( './includes/path.py' )
  require_once( './includes/theme.py' )
  require_once( './includes/common.py' )
  require_once( './includes/unicode.py' )
  require_once( './includes/file.py' )
  require_once( './includes/module.py' )
  require_once( './includes/database.py' )
  unicode_check()
  # Install and update pages are treated differently to prevent theming overrides.
  if (defined('MAINTENANCE_MODE') and (MAINTENANCE_MODE == 'install' or MAINTENANCE_MODE == 'update')):
    theme_ = 'minnelli'
  else:
    # Load module basics (needed for hook invokes).
    module_list_ = { 'system' : {}, 'filter' : {} }
    module_list_['system']['filename'] = 'modules/system/system.py'
    module_list_['filter']['filename'] = 'modules/filter/filter.py'
    module_list(True, False, False, module_list_)
    drupal_load('module', 'system')
    drupal_load('module', 'filter')
    theme_ = variable_get('maintenance_theme', 'minnelli')
  themes = list_themes()
  # Store the identifier for retrieving theme settings with.
  theme_key = theme_
  # Find all our ancestor themes and put them in an array.
  base_theme = array()
  ancestor = theme_
  while (ancestor and isset(themes[ancestor], base_theme)):
    new_base_theme = themes[themes[ancestor].base_theme]
    base_theme.append(new_base_theme)
    ancestor = themes[ancestor].base_theme
  _init_theme(themes[theme], array_reverse(base_theme), '_theme_load_offline_registry')
  # These are usually added from system_init() -except maintenance.css.
  # When the database is inactive it's not called so we add it here.
  drupal_add_css(drupal_get_path('module', 'system') + '/defaults.css', 'module')
  drupal_add_css(drupal_get_path('module', 'system') + '/system.css', 'module')
  drupal_add_css(drupal_get_path('module', 'system') + '/system-menus.css', 'module')
  drupal_add_css(drupal_get_path('module', 'system') + '/maintenance.css', 'module')
#
# This builds the registry when the site needs to bypass any database calls.
#
def _theme_load_offline_registry(this_theme, base_theme = None, theme_engine = None):
  registry = _theme_build_registry(this_theme, base_theme, theme_engine)
  _theme_set_registry(registry)



#
# Return a themed list of maintenance tasks to perform.
#
# @ingroup themeable
#
def theme_task_list(items_, active = None):
  done = ((active == None) or (isset(items, active)))
  output = '<ol class="task-list">'
  for k,item in items_.items():
    if (active == k):
      class_ = 'active'
      done = False
    else:
      class_ = ('done' if done else '')
    output += '<li class="' + class_ + '">' + item + '</li>'
  output += '</ol>'
  return output



#
# Generate a themed installation page.
#
# Note: this function is not themeable.
#
# @param content
#   The page content to show.
#
def theme_install_page(content):
  global theme_path
  drupal_set_header('Content-Type: text/html; charset=utf-8')
  # Assign content.
  variables['content'] = content
  # Delay setting the message variable so it can be processed below.
  variables['show_messages'] = False
  # The maintenance preprocess function is recycled here.
  template_preprocess_maintenance_page(variables)
  # Special handling of error messages
  messages = drupal_set_message()
  if (isset(messages, 'error')):
    title = (st('The following errors must be resolved before you can continue the installation process') if (count(messages['error']) > 1) else st('The following error must be resolved before you can continue the installation process'))
    variables['messages'] += '<h3>' + title + ':</h3>'
    variables['messages'] += theme('status_messages', 'error')
    variables['content'] += '<p>' + st('Please check the error messages and <a href="not url">try again</a>.', {'not url' : request_uri()}) + '</p>'
  # Special handling of warning messages
  if (isset(messages, 'warning')):
    title = (st('The following installation warnings should be carefully reviewed') if (count(messages['warning']) > 1) else st('The following installation warning should be carefully reviewed'))
    variables['messages'] += '<h4>' + title + ':</h4>'
    variables['messages'] += theme('status_messages', 'warning')
  # Special handling of status messages
  if (isset(messages, 'status')):
    title = (st('The following installation warnings should be carefully reviewed, but in most cases may be safely ignored') if (count(messages['status']) > 1) else st('The following installation warning should be carefully reviewed, but in most cases may be safely ignored'))
    variables['messages'] += '<h4>' + title + ':</h4>'
    variables['messages'] += theme('status_messages', 'status')
  # This was called as a theme hook (not template), so we need to
  # fix path_to_theme() for the template, to point at the actual
  # theme rather than system module as owner of the hook.
  theme_path = 'themes/garland'
  return theme_render_template('themes/garland/maintenance-page.tpl.py', variables)



#
# Generate a themed update page.
#
# Note: this function is not themeable.
#
# @param content
#   The page content to show.
# @param show_messages
#   Whether to output status and error messages.
#   False can be useful to postpone the messages to a subsequent page.
#
def theme_update_page(content, show_messages = True):
  global theme_path
  # Set required headers.
  drupal_set_header('Content-Type: text/html; charset=utf-8')
  # Assign content and show message flag.
  variables['content'] = content
  variables['show_messages'] = show_messages
  # The maintenance preprocess function is recycled here.
  template_preprocess_maintenance_page(variables)
  # Special handling of warning messages.
  messages = drupal_set_message()
  if (isset(messages['warning'])):
    title = ('The following update warnings should be carefully reviewed before continuing' if (count(messages['warning']) > 1) else 'The following update warning should be carefully reviewed before continuing')
    variables['messages'] += '<h4>' + title + ':</h4>'
    variables['messages'] += theme('status_messages', 'warning')
  # This was called as a theme hook (not template), so we need to
  # fix path_to_theme() for the template, to point at the actual
  # theme rather than system module as owner of the hook.
  theme_path = 'themes/garland'
  return theme_render_template('themes/garland/maintenance-page.tpl.php', variables)



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
  DrupyHelper.Reference.check(variables)
  global theme_
  # Add favicon
  if (theme_get_setting('toggle_favicon')):
    drupal_set_html_head('<link rel="shortcut icon" href="' + check_url(theme_get_setting('favicon')) + '" type="image/x-icon" />');
  # Retrieve the theme data to list all available regions.
  theme_data = _system_theme_data()
  regions = theme_data[theme_].info['regions']
  # Get all region content set with drupal_set_content().
  for region in array_keys(regions):
    # Assign region to a region variable.
    region_content = drupal_get_content(region)
    if isset(variables.val, region):
      variables.val[region] += region_content
    else:
      variables[region] = region_content
  # Setup layout variable.
  variables.val['layout'] = 'none'
  if (not empty(variables.val['left'])):
    variables['layout'] = 'left'
  if (not empty(variables['right'])):
    variables.val['layout'] = ('both' if (variables.val['layout'] == 'left') else 'right')
  # Construct page title
  if (drupal_get_title()):
    head_title = [strip_tags(drupal_get_title()), variable_get('site_name', 'Drupal')];
  else:
    head_title = [variable_get('site_name', 'Drupal')]
    if (variable_get('site_slogan', '')):
      head_title.append( variable_get('site_slogan', '') )
  variables.val['head_title']        = implode(' | ', head_title)
  variables.val['base_path']         = base_path()
  variables.val['front_page']        = url()
  variables.val['breadcrumb']        = ''
  variables.val['feed_icons']        = ''
  variables.val['footer_message']    = filter_xss_admin(variable_get('site_footer', FALSE))
  variables.val['head']              = drupal_get_html_head()
  variables.val['help']              = ''
  variables.val['language']          = language
  variables.val['language'].dir     = ('rtl' if language.direction else 'ltr')
  variables.val['logo']              = theme_get_setting('logo');
  variables.val['messages']          = (theme('status_messages') if variables.val['show_messages'] else '')
  variables.val['mission']           = '';
  variables.val['primary_links']     = [];
  variables.val['secondary_links']   = [];
  variables.val['search_box']        = '';
  variables.val['site_name']         = (variable_get('site_name', 'Drupal') if theme_get_setting('toggle_name')  else '')
  variables.val['site_slogan']       = (variable_get('site_slogan', '') if theme_get_setting('toggle_slogan') else '')
  variables.val['css']               = drupal_add_css()
  variables.val['styles']            = drupal_get_css()
  variables.val['scripts']           = drupal_get_js()
  variables.val['tabs']              = ''
  variables.val['title']             = drupal_get_title();
  variables.val['closure']           = ''
  # Compile a list of classes that are going to be applied to the body element.
  body_classes = []
  body_classes.append( 'in-maintenance' )
  if (isset(variables.val, 'db_is_active') and not variables.val['db_is_active']):
    body_classes.append( 'db-offline' )
  if (variables.val['layout'] == 'both'):
    body_classes.append( 'two-sidebars' )
  elif (variables.val['layout'] == 'none'):
    body_classes.append( 'no-sidebars' )
  else:
    body_classes.append( 'one-sidebar sidebar-'  + variables.val['layout'] )
  variables.val['body_classes'] = implode(' ', body_classes)
  # Dead databases will show error messages so supplying this template will
  # allow themers to override the page and the content completely.
  if (isset(variables.val, 'db_is_active') and not variables.val['db_is_active']):
    variables.val['template_file'] = 'maintenance-page-offline';



