#!/usr/bin/env python

# Id: system.module,v 1.604 2008/06/28 12:37:52 dries Exp $

"""
  Configuration system that lets administrators
  modify the workings of the site.

  @package system
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's modules/system/system.module
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
from includes import database as lib_database
from includes import bootstrap as lib_bootstrap
from includes import common as lib_common
from includes import menu as lib_menu
#from includes import tablesort as inc_tablesort
#from includes import form as inc_form
from includes import theme as lib_theme
from includes import path as lib_path
#from includes import mail as inc_mail
#from plugins import user as plugin_user
#from plugins import node as plugin_node
#from plugins import taxonomy as plugin_taxonomy

#
#
# The current system version.
#
VERSION = '7.0-dev'

#
# Core API compatibility.
#
DRUPAL_CORE_COMPATIBILITY = '7.x'

#
# Minimum supported version of PHP.
#
DRUPAL_MINIMUM_PHP = None

#
# Minimum supported version of PHP.
#
DRUPAL_MINIMUM_PYTHON = '2.5'

#
# Minimum recommended value of PHP memory_limit.
#
DRUPAL_MINIMUM_PHP_MEMORY_LIMIT = None

#
# Minimum supported version of MySQL, if it is used.
#
DRUPAL_MINIMUM_MYSQL = '5.0'

#
# Minimum supported version of PostgreSQL, if it is used.
#
DRUPAL_MINIMUM_PGSQL = '7.4'

#
# Maximum age of temporary files in seconds.
#
DRUPAL_MAXIMUM_TEMP_FILE_AGE = 1440



def hook_help(path_, arg):
  """
   Implementation of hook_help().
   
   @param path_ Str
   @param arg Dict
   @return Str
  """
  if path_ == 'admin/help#system':
    output = '<p>' +  t('The system module is at the foundation of your ' + \
      'Drupal website, and provides basic but extensible functionality for ' + \
      'use by other modules and themes + Some integral elements of ' + \
      'Drupal are contained in and managed by the system module, including ' + \
      'caching, enabling or disabling of modules and themes, preparing ' + \
      'and displaying the administrative page, and configuring ' + \
      'fundamental site settings. A number of key system maintenance ' + \
      'operations are also part of the system module.') + '</p>'
    output += '<p>' +  t('The system module provides:')  + '</p>'
    output += '<ul><li>' +  t('support for enabling and disabling ' + \
      '<a href="@modules">modules</a> + Drupal comes packaged with a ' + \
      'number of core modules; each module provides a discrete set ' + \
      'of features and may be enabled depending on the needs of your ' + \
      'site. A wide array of additional modules contributed by members ' + \
      'of the Drupal community are available for download at the ' + \
      '<a href="@drupal-modules">Drupal.org module page</a>.', {'@modules' : \
      url('admin/build/modules'), '@drupal-modules' : \
      'http://drupal.org/project/modules'}) + '</li>'
    output += '<li>' +  t('support for enabling and disabling ' + \
      '<a href="@themes">themes</a>, which determine the design and ' + \
      'presentation of your site + Drupal comes packaged with several ' + \
      'core themes and additional contributed themes are available at ' + \
      'the <a href="@drupal-themes">Drupal.org theme page</a>.', \
      {'@themes' : url('admin/build/themes'), '@drupal-themes' : \
       'http://drupal.org/project/themes'}) + '</li>'
    output += '<li>' +  t('a robust ' + \
      '<a href="@cache-settings">caching system</a> that allows the ' + \
      'efficient re-use of previously-constructed web pages and web page ' + \
      'components + Drupal stores the pages requested by anonymous ' + \
      'users in a compressed format; depending on your site configuration ' + \
      'and the amount of your web traffic tied to anonymous visitors, ' + \
      'Drupal\'s caching system may significantly increase the speed ' + \
      'of your site.', {'@cache-settings' : \
      url('admin/settings/performance')}) + '</li>'
    output += '<li>' +  t('a set of routine administrative operations that ' + \
      'rely on a correctly-configured <a href="@cron">cron maintenance ' + \
      'task</a> to run automatically + A number of other modules, ' + \
      'including  the feed aggregator, and search also rely on ' + \
      '<a href="@cron">cron maintenance tasks</a>. For more information, ' + \
      'see the online handbook entry for ' + \
      '<a href="@handbook">configuring cron jobs</a>.', \
      {'@cron' : url('admin/reports/status'), '@handbook' : \
       'http://drupal.org/cron'}) + '</li>'
    output += '<li>' +  t('basic configuration options for your site, ' + \
      'including <a href="@date-settings">date and time settings</a>, ' + \
      '<a href="@file-system">file system settings</a>, ' + \
      '<a href="@clean-url">clean URL support</a>, ' + \
      '<a href="@site-info">site name and other information</a>, and a ' + \
      '<a href="@site-maintenance">site maintenance</a> function for ' + \
      'taking your site temporarily off-line.', {'@date-settings' : \
      url('admin/settings/date-time'), '@file-system' : \
      url('admin/settings/file-system'), '@clean-url' : \
      url('admin/settings/clean-urls'), '@site-info' : \
      url('admin/settings/site-information'), '@site-maintenance' : \
      url('admin/settings/site-maintenance')})  + '</li></ul>'
    output += '<p>' +  t('For more information, see the online handbook ' + \
      'entry for <a href="@system">System module</a>.', \
      {'@system' : 'http://drupal.org/handbook/modules/system/'})  + '</p>'
    return output
  elif path_ == 'admin':
    return '<p>' +  t('Welcome to the administration section + Here ' + \
      'you may control how your site functions.') + '</p>'
  elif path_ == 'admin/by-module':
    return '<p>' +  t('This page shows you all available administration ' + \
      'tasks for each module.')  + '</p>'
  elif path_ == 'admin/build/themes':
    output = '<p>' +  t('Select which themes are available to your users ' + \
      'and specify the default theme + To configure site-wide display ' + \
      'settings, click the "configure" task above. Alternatively, ' + \
      'to override these settings in a specific theme, click the ' + \
      '"configure" link for that theme. Note that different themes ' + \
      'may have different regions available for displaying content; ' + \
      'for consistency in presentation, you may wish to enable ' + \
      'only one theme.') + '</p>'
    output += '<p>' +  t('To change the appearance of your site, a ' + \
      'number of <a href="@themes">contributed themes</a> are available.', \
      {'@themes' : 'http://drupal.org/project/themes'})  + '</p>'
    return output
  elif path_ == 'admin/build/themes/settings/' +  arg[4]:
    reference = php.explode('.', arg[4], 2)
    theme = php.array_pop(reference)
    return '<p>' +  t('These options control the display settings for ' + \
      'the <code>%template</code> theme + When your site is displayed ' + \
      'using this theme, these settings will be used. By clicking ' + \
      '"Reset to defaults," you can choose to use the ' + \
      '<a href="@global">global settings</a> for this theme.', \
      {'%template' : theme, '@global' : \
       url('admin/build/themes/settings')}) + '</p>'
  elif path_ == 'admin/build/themes/settings':
    return '<p>' +  t('These options control the default display settings ' + \
      'for your entire site, across all themes + Unless they have been ' + \
      'overridden by a specific theme, these settings will be used.') + '</p>'
  elif path_ == 'admin/build/modules':
    output = '<p>' +  t('Modules are plugins that extend Drupal\'s core ' + \
      'functionality + Enable modules by selecting the ' + \
      '<em>Enabled</em> checkboxes below and clicking the ' + \
      '<em>Save configuration</em> button. Once a module is enabled, ' + \
      'new <a href="@permissions">permissions</a> may be available.)', \
      {'@permissions' : url('admin/user/permissions')}) + '</p>'
    output += '<p>' +  t('It is important that ' + \
      '<a href="@update-php">update.php</a> is run every time a module ' + \
      'is updated to a newer version.', {'@update-php' : base_url  + \
      '/update.php'}) + '</p>'
    output += '<p>' +  t('You can find all administration tasks belonging ' + \
      'to a particular module on the <a href="@by-module">administration ' + \
      'by module page</a>.', {'@by-module' : url('admin/by-module')})  + '</p>'
    output += '<p>' +  t('To extend the functionality of your site, ' + \
       'a number of <a href="@modules">contributed modules</a> are ' + \
       'available.', {'@modules' : \
       'http://drupal.org/project/modules'})  + '</p>'
    return output
  elif path_ == 'admin/build/modules/uninstall':
    return '<p>' +  t('The uninstall process removes all data related to ' + \
      'a module + To uninstall a module, you must first disable it. ' + \
      'Not all modules support this feature.') + '</p>'
  elif path_ == 'admin/build/block/configure':
    if (arg[4] == 'system' and arg[5] == 0):
      return '<p>' +  t('The <em>Powered by Drupal</em> block is an ' + \
        'optional link to the home page of the Drupal project + ' + \
        'While there is absolutely no requirement that sites feature ' + \
        'this link, it may be used to show support for Drupal.') + '</p>'
  elif path_ == 'admin/settings/actions' or \
      path_ == 'admin/settings/actions/manage':
    output = '<p>' +  t('Actions are individual tasks that the system can ' + \
      'do, such as unpublishing a piece of content or banning a user + ' + \
      'Modules, such as the trigger module, can fire these actions ' + \
      'when certain system events happen; for example, when a new ' + \
      'post is added or when a user logs in. Modules may also ' + \
      'provide additional actions.') + '</p>'
    output += '<p>' +  t('There are two types of actions: simple and ' + \
      'advanced + Simple actions do not require any additional ' + \
      'configuration, and are listed here automatically. Advanced actions ' + \
      'can do more than simple actions; for example, send an e-mail to ' + \
      'a specified address, or check for certain words within a piece ' + \
      'of content. These actions need to be created and configured first ' + \
      'before they may be used. To create an advanced action, select ' + \
      'the action from the drop-down below and click the ' + \
      '<em>Create</em> button.') + '</p>'
    if (lib_plugin.plugin_exists('trigger')):
      output += '<p>' +  t('You may proceed to the ' + \
        '<a href="@url">Triggers</a> page to assign these actions ' + \
        'to system events.', {'@url' : url('admin/build/trigger')})  + '</p>'
    return output
  elif path_ == 'admin/settings/actions/configure':
    return t('An advanced action offers additional configuration options ' + \
      'which may be filled out below + Changing the ' + \
      '<em>Description</em> field is recommended, in order to better ' + \
      'identify the precise action taking place. This description ' + \
      'will be displayed in modules such as the trigger module when ' + \
      'assigning actions to system events, so it is best if it is as ' + \
      'descriptive as possible (for example, "Send e-mail to ' + \
      'Moderation Team" rather than simply "Send e-mail").')
  elif path_ == 'admin/settings/ip-blocking':
    return '<p>' +  t('IP addresses listed here are blocked from your ' + \
      'site before any modules are loaded + You may add IP addresses to ' + \
      'the list, or delete existing entries.') + '</p>'
  elif path_ == 'admin/reports/status':
    return '<p>' +  t("Here you can find a short overview of your " + \
      "site's parameters as well as any problems detected with your " + \
      "installation + It may be useful to copy and paste this " + \
      "information into support requests filed on drupal.org's " + \
      "support forums and project issue queues.") + '</p>'


def hook_theme():
  """
   Implementation of hook_theme().
   
   @return Dict
  """
  return array_merge(drupal_common_theme(), {
    'system_theme_select_form' : {
      'arguments' : {'form' : None},
      'file' : 'system.admin.inc'
    },
    'system_themes_form' : {
      'arguments' : {'form' : None},
      'file' : 'system.admin.inc'
    },
    'system_modules' : {
      'arguments' : {'form' : None},
      'file' : 'system.admin.inc'
    },
    'system_modules_uninstall' : {
      'arguments' : {'form' : None},
      'file' : 'system.admin.inc'
    },
    'status_report' : {
      'arguments' : {'requirements' : None},
      'file' : 'system.admin.inc'
    },
    'admin_page' : {
      'arguments' : {'blocks' : None},
      'file' : 'system.admin.inc'
    },
    'admin_block' : {
      'arguments' : {'block' : None},
      'file' : 'system.admin.inc'
    },
    'admin_block_content' : {
      'arguments' : {'content' : None},
      'file' : 'system.admin.inc'
    },
    'system_admin_by_module' : {
      'arguments' : {'menu_items' : None},
      'file' : 'system.admin.inc'
    },
    'system_powered_by' : {
      'arguments' : {'image_path' : None}
    },
    'meta_generator_html' : {
      'arguments' : {'version' : None}
    },
    'meta_generator_header' : {
      'arguments' : {'version' : None}
    },
    'system_compact_link' : {}
  })



def hook_perm():
  """
   Implementation of hook_perm().
   
   @return Dict
  """
  return {
    'administer site configuration' : t(\
      'Configure site-wide settings such as module or theme ' + \
      'administration settings.'),
    'access administration pages' : t('View the administration panel ' + \
      'and browse the help system.'),
    'administer actions' : t('Manage the actions defined for your site.'),
    'access site reports' : t('View reports from system logs and other ' + \
      'status information.'),
    'select different theme' : t('Select a theme other than the default ' + \
      'theme set by the site administrator.'),
    'administer files' : t('Manage user-uploaded files.'),
    'block IP addresses' : t('Block IP addresses from accessing your site.')
  }


def hook_elements():
  """
   Implementation of hook_elements().
   
   @return Dict
  """
  type_ = {}
  # Top level form
  type_['form'] = {
    '#method' : 'post',
    '#action' : request_uri()
  }
  #
  # Input elements.
  #
  type_['submit'] = {
    '#input' : True,
    '#name' : 'op',
    '#button_type' : 'submit',
    '#executes_submit_callback' : True,
    '#process' : ('form_expand_ahah',)
  }
  type_['button'] = {
    '#input' : True,
    '#name' : 'op',
    '#button_type' : 'submit',
    '#executes_submit_callback' : False,
    '#process' : ('form_expand_ahah',)
  }
  type_['image_button'] = {
    '#input' : True,
    '#button_type' : 'submit',
    '#executes_submit_callback' : True,
    '#process' : ('form_expand_ahah',),
    '#return_value' : True,
    '#has_garbage_value' : True,
    '#src' : None
  }
  type_['textfield'] = {
    '#input' : True,
    '#size' : 60,
    '#maxlength' : 128,
    '#autocomplete_path' : False,
    '#process' : ('form_expand_ahah',)
  }
  type_['password'] = {
    '#input' : True,
    '#size' : 60,
    '#maxlength' : 128,
    '#process' : ('form_expand_ahah',)
  }
  type_['password_confirm'] = {
    '#input' : True,
    '#process' : ('expand_password_confirm',)
  }
  type_['textarea'] = {
    '#input' : True,
    '#cols' : 60,
    '#rows' : 5,
    '#resizable' : True,
    '#process' : ('form_expand_ahah',),
  }
  type_['radios'] = {
    '#input' : True,
    '#process' : ('expand_radios',)
  }
  type_['radio'] = {
    '#input' : True,
    '#default_value' : None,
    '#process' : ('form_expand_ahah',)
  }
  type_['checkboxes'] = {
    '#input' : True,
    '#tree' : True,
    '#process' : ('expand_checkboxes',)
  }
  type_['checkbox'] = {
    '#input' : True,
    '#return_value' : 1,
    '#process' : ('form_expand_ahah',)
  }
  type_['select'] = {
    '#input' : True,
    '#size' : 0,
    '#multiple' : False,
    '#process' : ('form_expand_ahah',)
  }
  type_['weight'] = {
    '#input' : True,
    '#delta' : 10,
    '#default_value' : 0,
    '#process' : ('process_weight', 'form_expand_ahah')
  }
  type_['date'] = {
    '#input' : True,
    '#element_validate' : ('date_validate',),
    '#process' : ('expand_date',)
  }
  type_['file'] = {
    '#input' : True,
    '#size' : 60
  }
  #
  # Form structure.
  #
  type_['item'] = {
    '#value' : ''
  }
  type_['hidden'] = {
    '#input' : True,
    '#process' : ('form_expand_ahah',)
  }
  type_['value'] = {
    '#input' : True
  }
  type_['markup'] = {
    '#prefix' : '',
    '#suffix' : ''
  }
  type_['fieldset'] = {
    '#collapsible' : False,
    '#collapsed' : False,
    '#value' : None,
    '#process' : ('form_expand_ahah',)
  }
  type_['token'] = {
    '#input' : True
  }
  return type_


def hook_menu():
  """
   Implementation of hook_menu().
   
   @return Dict
  """
  items = {}
  items['system/files'] = {
    'title' : 'File download',
    'page callback' : 'file_download',
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  items['admin'] = {
    'title' : 'Administer',
    'access arguments' : ('access administration pages',),
    'page callback' : 'system_main_admin_page',
    'weight' : 9
  }
  items['admin/compact'] = {
    'title' : 'Compact mode',
    'page callback' : 'system_admin_compact_page',
    'access arguments' : ('access administration pages',),
    'type' : MENU_CALLBACK
  }
  items['admin/by-task'] = {
    'title' : 'By task',
    'page callback' : 'system_main_admin_page',
    'access arguments' : ('access administration pages',),
    'type' : MENU_DEFAULT_LOCAL_TASK
  }
  items['admin/by-module'] = {
    'title' : 'By module',
    'page callback' : 'system_admin_by_module',
    'access arguments' : ('access administration pages',),
    'type' : MENU_LOCAL_TASK,
    'weight' : 2
  }
  items['admin/content'] = {
    'title' : 'Content management',
    'description' : "Manage your site's content.",
    'position' : 'left',
    'weight' : -10,
    'page callback' : 'system_admin_menu_block_page',
    'access arguments' : ('access administration pages',)
  }
  # menu items that are basically just menu blocks
  items['admin/settings'] = {
    'title' : 'Site configuration',
    'description' : 'Adjust basic site configuration options.',
    'position' : 'right',
    'weight' : -5,
    'page callback' : 'system_settings_overview',
    'access arguments' : ('access administration pages',)
  }
  items['admin/build'] = {
    'title' : 'Site building',
    'description' : 'Control how your site looks and feels.',
    'position' : 'right',
    'weight' : -10,
    'page callback' : 'system_admin_menu_block_page',
    'access arguments' : ('access administration pages',)
  }
  items['admin/settings/admin'] = {
    'title' : 'Administration theme',
    'description' : 'Settings for how your administrative pages should look.',
    'position' : 'left',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_admin_theme_settings',),
    'access arguments' : ('administer site configuration',),
    'block callback' : 'system_admin_theme_settings'
  }
  # Themes:
  items['admin/build/themes'] = {
    'title' : 'Themes',
    'description' : 'Change which theme your site uses or allows users to set.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_themes_form', None),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/build/themes/select'] = {
    'title' : 'List',
    'description' : 'Select the default theme.',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -1
  }
  items['admin/build/themes/settings'] = {
    'title' : 'Configure',
    'page arguments' : ('system_theme_settings',),
    'access arguments' : ('administer site configuration',),
    'type' : MENU_LOCAL_TASK
  }
  # Theme configuration subtabs
  items['admin/build/themes/settings/global'] = {
    'title' : 'Global settings',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -1
  }
  for theme in list_themes():
    items['admin/build/themes/settings/' +  theme.name] = {
      'title' : theme.info['name'],
      'page arguments' : array('system_theme_settings', theme.name),
      'type' : MENU_LOCAL_TASK,
      'access callback' : '_system_themes_access',
      'access arguments' : (theme,)
    }
  # Modules:
  items['admin/build/modules'] = {
    'title' : 'Modules',
    'description' : 'Enable or disable add-on modules for your site.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_modules',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/build/modules/list'] = {
    'title' : 'List',
    'type' : MENU_DEFAULT_LOCAL_TASK
  }
  items['admin/build/modules/list/confirm'] = {
    'title' : 'List',
    'access arguments' : ('administer site configuration',),
    'type' : MENU_CALLBACK
  }
  items['admin/build/modules/uninstall'] = {
    'title' : 'Uninstall',
    'page arguments' : ('system_modules_uninstall',),
    'access arguments' : ('administer site configuration',),
    'type' : MENU_LOCAL_TASK
  }
  items['admin/build/modules/uninstall/confirm'] = {
    'title' : 'Uninstall',
    'access arguments' : ('administer site configuration',),
    'type' : MENU_CALLBACK
  }
  # Actions:
  items['admin/settings/actions'] = {
    'title' : 'Actions',
    'description' : 'Manage the actions defined for your site.',
    'access arguments' : ('administer actions',),
    'page callback' : 'system_actions_manage'
  }
  items['admin/settings/actions/manage'] = {
    'title' : 'Manage actions',
    'description' : 'Manage the actions defined for your site.',
    'page callback' : 'system_actions_manage',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -2
  }
  items['admin/settings/actions/configure'] = {
    'title' : 'Configure an advanced action',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_actions_configure',),
    'access arguments' : ('administer actions',),
    'type' : MENU_CALLBACK
  }
  items['admin/settings/actions/delete/%actions'] = {
    'title' : 'Delete action',
    'description' : 'Delete an action.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_actions_delete_form', 4),
    'access arguments' : ('administer actions',),
    'type' : MENU_CALLBACK
  }
  items['admin/settings/actions/orphan'] = {
    'title' : 'Remove orphans',
    'page callback' : 'system_actions_remove_orphans',
    'access arguments' : ('administer actions',),
    'type' : MENU_CALLBACK
  }
  # IP address blocking.
  items['admin/settings/ip-blocking'] = {
    'title' : 'IP address blocking',
    'description' : 'Manage blocked IP addresses.',
    'page callback' : 'system_ip_blocking',
    'access arguments' : ('block IP addresses',),
  }
  items['admin/settings/ip-blocking/%'] = {
    'title' : 'IP address blocking',
    'description' : 'Manage blocked IP addresses.',
    'page callback' : 'system_ip_blocking',
    'access arguments' : ('block IP addresses',),
    'type' : MENU_CALLBACK
  }
  items['admin/settings/ip-blocking/delete/%blocked_ip'] = {
    'title' : 'Delete IP address',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_ip_blocking_delete', 4),
    'access arguments' : ('block IP addresses',),
    'type' : MENU_CALLBACK
  }
  # Settings:
  items['admin/settings/site-information'] = {
    'title' : 'Site information',
    'description' : 'Change basic site information, such as the site ' + \
      'name, slogan, e-mail address, mission, front page and more.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_site_information_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/error-reporting'] = {
    'title' : 'Error reporting',
    'description' : 'Control how Drupal deals with errors including ' + \
      '403/404 errors as well as PHP error reporting.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_error_reporting_settings'),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/logging'] = {
    'title' : 'Logging and alerts',
    'description' : "Settings for logging and alerts modules + Various " + \
      "modules can route Drupal's system events to different destination, " + \
      "such as syslog, database, email, + ..etc.",
    'page callback' : 'system_logging_overview',
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/performance'] = {
    'title' : 'Performance',
    'description' : 'Enable or disable page caching for anonymous ' + \
      'users and set CSS and JS bandwidth optimization options.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_performance_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/file-system'] = {
    'title' : 'File system',
    'description' : 'Tell Drupal where to store uploaded files and ' + \
      'how they are accessed.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_file_system_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/image-toolkit'] = {
    'title' : 'Image toolkit',
    'description' : 'Choose which image toolkit to use if you ' + \
      'have installed optional toolkits.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_image_toolkit_settings'),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/content/rss-publishing'] = {
    'title' : 'RSS publishing',
    'description' : 'Configure the number of items per feed and whether ' + \
      'feeds should be titles/teasers/full-text.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_rss_feeds_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/date-time'] = {
    'title' : 'Date and time',
    'description' : "Settings for how Drupal displays date and time, " + \
      "as well as the system's default timezone.",
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_date_time_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/date-time/lookup'] = {
    'title' : 'Date and time lookup',
    'type' : MENU_CALLBACK,
    'page callback' : 'system_date_time_lookup',
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/site-maintenance'] = {
    'title' : 'Site maintenance',
    'description' : 'Take the site off-line for maintenance ' + \
      'or bring it back online.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_site_maintenance_settings',),
    'access arguments' : array('administer site configuration',)
  }
  items['admin/settings/clean-urls'] = {
    'title' : 'Clean URLs',
    'description' : 'Enable or disable clean URLs for your site.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('system_clean_url_settings',),
    'access arguments' : ('administer site configuration',)
  }
  items['admin/settings/clean-urls/check'] = {
    'title' : 'Clean URL check',
    'page callback' : 'drupal_json',
    'page arguments' : ({'status' : True},),
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  # Menu handler to test that drupal_http_request() works locally.
  # @see system_check_http_request()
  items['admin/reports/request-test'] = {
    'title' : 'Request test',
    'page callback' : 'printf',
    'page arguments' : ('request test',),
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  # Reports:
  items['admin/reports'] = {
    'title' : 'Reports',
    'description' : 'View reports from system logs ' + \
      'and other status information.',
    'page callback' : 'system_admin_menu_block_page',
    'access arguments' : ('access site reports',),
    'weight' : 5,
    'position' : 'left'
  }
  items['admin/reports/status'] = {
    'title' : 'Status report',
    'description' : "Get a status report about your site's " + \
      "operation and any detected problems.",
    'page callback' : 'system_status',
    'weight' : 10,
    'access arguments' : ('administer site configuration',)
  }
  items['admin/reports/status/run-cron'] = {
    'title' : 'Run cron',
    'page callback' : 'system_run_cron',
    'access arguments' : ('administer site configuration',),
    'type' : MENU_CALLBACK
  }
  items['admin/reports/status/php'] = {
    'title' : 'PHP',
    'page callback' : 'system_php',
    'access arguments' : ('administer site configuration',),
    'type' : MENU_CALLBACK
  }
  items['admin/reports/status/sql'] = {
    'title' : 'SQL',
    'page callback' : 'system_sql',
    'access arguments' : ('administer site configuration',),
    'type' : MENU_CALLBACK
  }
  # Default page for batch operations
  items['batch'] = {
    'page callback' : 'system_batch_page',
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  return items



def blocked_ip_load(iid):
  """
   Retrieve a blocked IP address from the database.
  
   @param iid integer
     The ID of the blocked IP address to retrieve.
  
   @return
     The blocked IP address from the database as an array.
  """
  blocked_ip = lib_database.db_fetch_array(lib_database.db_query(\
    "SELECT * FROM {blocked_ips} WHERE iid = %d", iid))
  return blocked_ip



def _themes_access(theme_):
  """
   Menu item access callback - only admin or enabled themes can be accessed.
  """
  return plugin_user.access('administer site configuration') and \
    (theme_.status or theme_.name == \
    lib_bootstrap.variable_get('admin_theme', '0'))


def hook_init():
  """
   Implementation of hook_init().
  """
  global custom_theme
  # Use the administrative theme if the user
  # is looking at a page in the admin/* path.
  if (lib_path.arg(0) == 'admin' or \
      (lib_bootstrap.variable_get('node_admin_theme', '0') and \
      lib_path.arg(0) == 'node' and (lib_path.arg(1) == 'add' or \
      lib_path.arg(2) == 'edit'))):
    custom_theme = lib_bootstrap.variable_get('admin_theme', '0')
    lib_common.drupal_add_css(lib_common.drupal_get_path('plugin', 'system') + \
    '/admin.css', 'plugin')
  # Add the CSS for this module.
  lib_common.drupal_add_css(lib_common.drupal_get_path('plugin', 'system') +  \
    '/defaults.css', 'plugin')
  lib_common.drupal_add_css(lib_common.drupal_get_path('plugin', 'system') + \
    '/system.css', 'plugin')
  lib_common.drupal_add_css(lib_common.drupal_get_path('plugin', 'system') + \
    '/system-menus.css', 'plugin')
  # Get the major version
  version = php.explode('.', VERSION)[0]
  # Emit the META tag in the HTML HEAD section
  lib_theme.theme('meta_generator_html', version)
  # Emit the HTTP Header too
  lib_theme.theme('meta_generator_header', version)


def hook_user(type, edit, user, category = None):
  """
   Implementation of hook_user().
  
   Allows users to individually set their theme and time zone.
  """
  php.Reference.check(user)
  if (type_ == 'form' and category == 'account'):
    form['theme_select'] = theme_select_form(lib_common.t(
      'Selecting a different theme will ' + \
      'change the look and feel of the site.'), \
      (edit['theme'] if php.isset(edit, 'theme') else None), 2)
    if (lib_bootstrap.variable_get('configurable_timezones', 1)):
      zones = _zonelist()
      form['timezone'] = {
        '#type' : 'fieldset',
        '#title' : lib_common.t('Locale settings'),
        '#weight' : 6,
        '#collapsible' : True,
      }
      form['timezone']['timezone'] = {
        '#type' : 'select',
        '#title' : lib_common.t('Time zone'),
        '#default_value' : (edit['timezone'] if \
          php.strlen(edit['timezone']) else \
          lib_common.variable_get('date_default_timezone', 0)),
        '#options' : zones,
        '#description' : lib_common.t('Select your current local time. ' + \
          'Dates and times throughout this site will be displayed using ' + \
          'this time zone.'),
      }
    return form


def hook_block(op = 'list', delta = '', edit = None):
  """
   Implementation of hook_block().
  
   Generate a block with a promotional link to Drupal.org.
  """
  if op == 'list':
    blocks['powered-by'] = {
      'info' : lib_common.t('Powered by Drupal'),
      'weight' : '10',
       # Not worth caching.
      'cache' : BLOCK_NO_CACHE
    }
    return blocks
  elif op == 'configure':
    # Compile a list of fields to show
    form['wrapper']['color'] = {
      '#type' : 'select',
      '#title' : lib_common.t('Badge color'),
      '#default_value' : lib_bootstrap.variable_get(\
        'drupal_badge_color', 'powered-blue'),
      '#options' : {
        'powered-black' : lib_common.t('Black'),
        'powered-blue' : lib_common.t('Blue'),
        'powered-gray' : lib_common.t('Gray')
      }
    }
    form['wrapper']['size'] = {
      '#type' : 'select',
      '#title' : t('Badge size'),
      '#default_value' : lib_bootstrap.variable_get(\
        'drupal_badge_size', '80x15'),
      '#options' : {
        '80x15' : lib_common.t('Small'),
        '88x31' : lib_common.t('Medium'),
        '135x42' : lib_common.t('Large')
      }
    }
    return form
  elif op == 'save':
    lib_bootstrap.variable_set('drupal_badge_color', edit['color'])
    lib_bootstrap.variable_set('drupal_badge_size', edit['size'])
  elif op == 'view':
    image_path = 'misc/' + lib_bootstrap.variable_get('drupal_badge_color', \
      'powered-blue')  + '-' + lib_bootstrap.variable_get(\
      'drupal_badge_size', '80x15') + '.png'
    block['subject'] = None # Don't display a title
    block['content'] = lib_theme.theme('system_powered_by', image_path)



def admin_menu_block(item):
  """
   Provide a single block on the administration overview page.
  
   @param item
     The menu item to be displayed.
  """
  content = []
  if (not php.isset(item['mlid'])):
    item += lib_database.db_fetch_array(lib_database.db_query(\
      "SELECT mlid, menu_name FROM {menu_links} ml " + \
      "WHERE ml.router_path = '%s' AND module = 'system'", item['path']))
  result = lib_database.db_query(
    "SELECT m.load_functions, m.to_arg_functions, m.access_callback, " + \
    "m.access_arguments, m.page_callback, m.page_arguments, m.title, " + \
    "m.title_callback, m.title_arguments, m.type, m.description, ml.* " + \
    "FROM {menu_links} ml " +
    "LEFT JOIN {menu_router} m ON ml.router_path = m.path " + \
    "WHERE ml.plid = %d AND ml.menu_name = '%s' AND hidden = 0", \
    item['mlid'], item['menu_name'])
  while True:
    item = lib_database.db_fetch_array(result)
    if not item:
      break
    lib_menu._menu_link_translate(item)
    if (not item['access']):
      continue
    # The link 'description' either derived from the hook_menu 'description' or
    # entered by the user via menu module is saved as the title attribute.
    if (not php.empty(item['localized_options']['attributes']['title'])):
      item['description'] = item['localized_options']['attributes']['title']
    # Prepare for sorting as in function _menu_tree_check_access().
    # The weight is offset so it is always positive, with a uniform 5-digits.
    content[(50000 + item['weight']) +  ' '  + item['title'] + \
      ' ' + item['mlid']] = item
  p.ksort(content)
  return content


def admin_theme_submit(form, form_state):
  """
   Process admin theme form submissions.
  """
  php.Reference.check(form_state)
  # If we're changing themes, make sure the theme has its blocks initialized.
  if (form_state['values']['admin_theme'] and \
      form_state['values']['admin_theme'] != \
      lib_bootstrap.variable_get('admin_theme', '0')):
    result = lib_database.db_result(lib_database.db_query(\
     "SELECT COUNT(*) FROM {blocks} WHERE theme = '%s'", \
      form_state['values']['admin_theme']))
    if (not result):
      initialize_theme_blocks(form_state['values']['admin_theme'])


def theme_select_form(description = '', default_value = '', weight = 0):
  """
   Returns a fieldset containing the theme select form.
  
   @param description
      description of the fieldset
   @param default_value
      default value of theme radios
   @param weight
      weight of the fieldset
   @return
      a form array
  """
  if (plugin_user.access('select different theme')):
    enabled = []
    themes = list_themes()
    for theme_ in themes:
      if (theme_.status):
        enabled.append( theme_ )
    if (php.count(enabled) > 1):
      p.ksort(enabled)
      form['themes'] = {
        '#type' : 'fieldset',
        '#title' : lib_common.t('Theme configuration'),
        '#description' : description,
        '#collapsible' : True,
        '#theme' : 'system_theme_select_form'
      }
      for info in enabled:
        # For the default theme, revert to an empty string
        # so the user's theme updates when the site theme is changed.
        info.key = (info.name == ('' if \
          lib_bootstrap.variable_get('theme_default', 'garland') else \
          info.name))
        screenshot = None
        theme_key = info.name
        while theme_key:
          if (php.file_exists(themes[theme_key].info['screenshot'])):
            screenshot = themes[theme_key].info['screenshot']
            break
          theme_key = (themes[theme_key].info['base theme'] if \
            php.isset(themes[theme_key].info['base theme']) else None)
        screenshot = (screenshot if lib_theme.theme('image', screenshot, \
          lib_common.t('Screenshot for %theme theme', \
          {'%theme' : info.name}), '', {'class' : 'screenshot'}, False) else \
          lib_common.t('no screenshot'))
        form['themes'][info.key]['screenshot'] = {'#value' : screenshot}
        form['themes'][info.key]['description'] =  \
        {
          '#type' : 'item',
          '#title' : info.name,
          '#value' :
            php.dirname(info.filename) + (
              '<br /> <em>' + lib_common.t(\
              '(site default theme)') + '</em>' if \
              info.name == \
              lib_bootstrap.variable_get('theme_default', 'garland') else \
              ''
            )
        }
        options[info.key] = ''
      form['themes']['theme'] = {'#type' : 'radios', '#options' : options, \
        '#default_value' : (default_value if default_value else '')}
      form['#weight'] = weight
      return form



def check_directory(form_element):
  """
   Checks the existence of the directory specified in form_element. This
   function is called from the system_settings form to check both the
   file_directory_path and file_directory_temp directories. If validation
   fails, the form element is flagged with an error from within the
   file_check_directory function.
  
   @param form_element
     The form element containing the name of the directory to check.
  """
  file_check_directory(form_element['#value'], FILE_CREATE_DIRECTORY, \
    form_element['#parents'][0])
  return form_element



def get_files_database(files, type):
  """
   Retrieves the current status of an array of files in the system table.
  
   @param files
     An array of files to check.
   @param type
     The type of the files.
  """
  php.Reference.check(files)
  # Extract current files from database.
  result = lib_database.db_query(
    "SELECT filename, name, type, status, schema_version " + \
    "FROM {system} WHERE type = '%s'", type_)
  while True:
    file = lib_database.db_fetch_object(result)
    if not file:
      break
    if (php.isset(files[file.name]) and php.is_object(files[file.name])):
      file.old_filename = file.filename
      for key,value in file.items():
        if (not php.isset(files[file.name]) or not php.isset(files[file.name], key)):
          setattr(files[file.name], key, value)



def theme_default():
  """
   Prepare defaults for themes.
  
   @return
     An array of default themes settings.
  """
  return {
    'regions' : {
      'left' : 'Left sidebar',
      'right' : 'Right sidebar',
      'content' : 'Content',
      'header' : 'Header',
      'footer' : 'Footer'
    },
    'description' : '',
    'features' : (
      'comment_user_picture',
      'favicon',
      'mission',
      'logo',
      'name',
      'node_user_picture',
      'search',
      'slogan',
      'main_menu',
      'secondary_menu'
    ),
    'stylesheets' : {
      'all' : ('style.css',)
    },
    'scripts' : ('script.js',),
    'screenshot' : 'screenshot.png',
    'python' : DRUPAL_MINIMUM_PYTHON
  }



def theme_data():
  """
   Collect data about all currently available themes.
  
   @return
     Array of all available themes and their data.
  """
  # Scan the installation theme .info files and their engines.
  themes = _theme_data()
  # Extract current files from database.
  get_files_database(themes, 'theme')
  lib_database.db_query("DELETE FROM {system} WHERE type = 'theme'")
  for theme_ in themes:
    if (not isset(theme_, 'owner')):
      theme_.owner = ''
    lib_database.db_query(\
      "INSERT INTO {system} (name, owner, info, type, filename, " + \
      "status, bootstrap) VALUES ('%s', '%s', '%s', '%s', '%s', %d, %d)", \
      theme.name, theme.owner, serialize(theme.info), 'theme', \
      theme.filename, (theme.status if isset(theme, 'status') else 0), 0)
  return themes



def _theme_data():
  """
   Helper function to scan and collect theme .info data and their engines.
  
   @return
     An associative array of themes information.
  """
  php.static(_theme_data, 'theme_info', {})
  if (php.empty(_theme_data.theme_info)):
    # Find themes
    themes = lib_common.drupal_system_listing('\.info$', 'themes')
    # Find theme engines
    engines = lib_common.drupal_system_listing('\.engine$', 'themes/engines')
    defaults = theme_default()
    sub_themes = {}
    # Read info files for each theme
    for key,theme in themes.items():
      themes[key].info = drupal_parse_info_file(theme.filename) + defaults
      # Invoke hook_system_info_alter() to give installed modules a chance to
      # modify the data in the .info files if necessary.
      lib_common.drupal_alter('system_info', themes[key].info, themes[key])
      if (not empty(themes[key].info['base theme'])):
        sub_themes.append( key )
      if (php.empty(themes[key].info['engine'])):
        filename = php.dirname(themes[key].filename) +  \
          '/'  + themes[key].name + '.theme'
        if (php.file_exists(filename)):
          themes[key].owner = filename
          themes[key].prefix = key
      else:
        engine = themes[key].info['engine']
        if (php.isset(engines, engine)):
          themes[key].owner = engines[engine].filename
          themes[key].prefix = engines[engine].name
          themes[key].template = True
      # Give the stylesheets proper path information.
      pathed_stylesheets = {}
      for media, stylesheets in  themes[key].info['stylesheets'].items():
        for stylesheet in stylesheets:
          pathed_stylesheets[media][stylesheet] = \
          php.dirname(themes[key].filename) +  '/'  + stylesheet
      themes[key].info['stylesheets'] = pathed_stylesheets
      # Give the scripts proper path information.
      scripts = {}
      for script in themes[key].info['scripts']:
        scripts[script] = php.dirname(themes[key].filename) +  '/'  + script
      themes[key].info['scripts'] = scripts
      # Give the screenshot proper path information.
      if (not empty(themes[key].info['screenshot'])):
        themes[key].info['screenshot'] = php.dirname(themes[key].filename) +  \
        '/'  + themes[key].info['screenshot']
    # Now that we've established all our master themes, go back and fill in
    # data for subthemes.
    for key in sub_themes:
      base_key = find_base_theme(themes, key)
      if (not base_key):
        continue
      # Copy the 'owner' and 'engine' over if the top level theme uses a
      # theme engine.
      if (isset(themes[base_key], 'owner')):
        if (isset(themes[base_key].info, 'engine')):
          themes[key].info['engine'] = themes[base_key].info['engine']
          themes[key].owner = themes[base_key].owner
          themes[key].prefix = themes[base_key].prefix
        else:
          themes[key].prefix = key
    themes_info = themes
  return themes_info




def find_base_theme(themes, key, used_keys = []):
  """
   Recursive function to find the top level base theme. Themes can inherit
   templates and function implementations from earlier themes.
  
   @param themes
     An array of available themes.
   @param key
     The name of the theme whose base we are looking for.
   @param used_keys
     A recursion parameter preventing endless loops.
   @return
     Returns the top level parent that has no ancestor
     or returns None if there isn't a valid parent.
  """
  base_key = themes[key].info['base theme']
  # Does the base theme exist?
  if (not php.isset(themes, base_key)):
    return None
  # Is the base theme itself a child of another theme?
  if (php.isset(themes[base_key].info, 'base theme')):
    # Prevent loops.
    if (not php.empty(used_keys[base_key])):
      return None
    used_keys[base_key] = True
    return find_base_theme(themes, base_key, used_keys)
  # If we get here, then this is our parent theme.
  return base_key



def region_list(theme_key):
  """
   Get a list of available regions from a specified theme.
  
   @param theme_key
     The name of a theme.
   @return
     An array of regions in the form region['name'] = 'description'.
  """
  php.static(region_list, 'list_', {})
  if (not array_key_exists(theme_key, region_list.list_)):
    info = php.unserialize(lib_database.db_result(lib_database.db_query(\
      "SELECT info FROM {system} WHERE type = 'theme' AND name = '%s'",\
      theme_key)))
    region_list.list_[theme_key] = p.array_map('t', info['regions'])
  return region_list.list_[theme_key]



def default_region(theme_):
  """
   Get the name of the default region for a given theme.
  
   @param theme
     The name of a theme.
   @return
     A string that is the region name.
  """
  regions = php.array_keys(region_list(theme_))
  return (regions[0] if php.isset(regions[0]) else '')



def initialize_theme_blocks(theme_):
  """
   Assign an initial, default set of blocks for a theme.
  
   This function is called the first time a new theme is enabled. The new theme
   gets a copy of the default theme's blocks, with the difference that if a
   particular region isn't available in the new theme, the block is assigned
   to the new theme's default region.
  
   @param theme
     The name of a theme.
  """
  # Initialize theme's blocks if none already registered.
  if (not (db_result(db_query(\
      "SELECT COUNT(*) FROM {blocks} WHERE theme = '%s'", theme)))):
    default_theme = variable_get('theme_default', 'garland')
    regions = system_region_list(theme)
    result = db_query("SELECT * FROM {blocks} WHERE theme = '%s'", \
      default_theme)
    while True:
      block = lib_database.db_fetch_array(result)
      if not block:
        break
      # If the region isn't supported by the theme,
      # assign the block to the theme's default region.
      if (not php.array_key_exists(block['region'], regions)):
        block['region'] = default_region(theme_)
      lib_database.db_query(\
          "INSERT INTO {blocks} (module, delta, theme, status, weight, " + \
          "region, visibility, pages, custom, cache) VALUES ('%s', '%s', " + \
          "'%s', %d, %d, '%s', %d, '%s', %d, %d)", \
          block['module'], block['delta'], theme, block['status'], \
          block['weight'], block['region'], block['visibility'], \
          block['pages'], block['custom'], block['cache'])




def settings_form(form):
  """
   Add default buttons to a form and set its prefix.
  
   @ingroup forms
   @see system_settings_form_submit()
   @param form
     An associative array containing the structure of the form.
   @return
     The form structure.
  """
  form['buttons']['submit'] = {'#type' : 'submit', '#value' : \
    lib_common.t('Save configuration') }
  form['buttons']['reset'] = {'#type' : 'submit', '#value' : \
    lib_common.t('Reset to defaults') }
  if (not empty(php.POST) and inc_form.form_get_errors()):
    lib_common.drupal_set_message(lib_common.t(\
      'The settings have not been saved because of the errors.'), 'error')
  form['#submit'].append( 'system_settings_form_submit' )
  form['#theme'] = 'system_settings_form'
  return form



def settings_form_submit(form, form_state):
  """
   Execute the system_settings_form.
  
   If you want node type configure style handling of your checkboxes,
   add an array_filter value to your form.
  """
  php.Reference.check(form_state)
  op = (form_state['values']['op'] if \
    php.isset(form_state['values']['op']) else '')
  # Exclude unnecessary elements.
  del(form_state['values']['submit'], form_state['values']['reset'], \
    form_state['values']['form_id'], form_state['values']['op'], \
    form_state['values']['form_token'], form_state['values']['form_build_id'])
  for key,value in form_state['values'].items():
    if (op == lib_common.t('Reset to defaults')):
      lib_bootstrap.variable_del(key)
    else:
      if (php.is_array(value) and php.isset(form_state['values']['array_filter'])):
        value = php.array_keys(php.array_filter(value))
      lib_bootstrap.variable_set(key, value)
  if (op == t('Reset to defaults')):
    lib_common.drupal_set_message(lib_common.t(\
      'The configuration options have been reset to their default values.'))
  else:
    lib_common.drupal_set_message(lib_common.t(\
      'The configuration options have been saved.'))
  lib_cache.cache_clear_all()
  lib_theme.drupal_rebuild_theme_registry()




def _sort_requirements(a, b):
  """
   Helper function to sort requirements.
  """
  if (not php.isset(a, 'weight')):
    if (not php.isset(b, 'weight')):
      return p.strcmp(a['title'], b['title'])
    return -b['weight']
  return ((a['weight'] - b['weight']) if php.isset(b['weight']) else a['weight'])



def hook_node_type(op, info):
  """
   Implementation of hook_node_type().
  
   Updates theme settings after a node type change.
  """
  if (op == 'update' and not php.empty(info.old_type) and \
      info.type != info.old_type):
    old = 'toggle_node_info_' +  info.old_type
    new = 'toggle_node_info_' +  info.type
    theme_settings = lib_bootstrap.variable_get('theme_settings', {})
    if (php.isset(theme_settings, old)):
      theme_settings[new] = theme_settings[old]
      del(theme_settings[old])
      lib_bootstrap.variable_set('theme_settings', theme_settings)



def confirm_form(form, question, path_, description = None, yes = None, \
    no = None, name = 'confirm'):
  """
   Output a confirmation form
  
   This function returns a complete form for confirming an action. A link is
   offered to go back to the item that is being changed in case the user changes
   his/her mind.
  
   If the submit handler for this form is invoked, the user successfully
   confirmed the action. You should never directly inspect _POST to see if an
   action was confirmed.
  
   @ingroup forms
   @param form
     Additional elements to inject into the form, for example hidden elements.
   @param question
     The question to ask the user (e.g. "Are you sure you want to delete the
     block <em>foo</em>?").
   @param path
     The page to go to if the user denies the action.
     Can be either a drupal path,
     or an array with the keys 'path', 'query', 'fragment'.
   @param description
     Additional text to display (defaults to "This action cannot be undone.").
   @param yes
     A caption for the button which confirms the action (e.g. "Delete",
     "Replace", ...).
   @param no
     A caption for the link which denies the action (e.g. "Cancel").
   @param name
     The internal name used to refer to the confirmation item.
   @return
     The form.
  """
  description = (description if description is not None \
    else lib_common.t('This action cannot be undone.'))
  # Prepare cancel link
  query = fragment = None
  if (php.is_array(path_)):
    query = (path_['query'] if php.isset(path_, 'query') else None)
    fragment = (path_['fragment'] if php.isset(path_['fragment']) else None)
    path = (path_['path'] if php.isset(path_, 'path') else None)
  cancel = lib_common.l((no if no else lib_common.t('Cancel')), path_, \
    {'query' : query, 'fragment' : fragment})
  lib_path.drupal_set_title(question)
  # Confirm form fails duplication check,
  # as the form values rarely change -- so skip it.
  form['#skip_duplicate_check'] = True
  form['#attributes'] = {'class' : 'confirmation'}
  form['description'] = {'#value' : description}
  form[name] = {'#type' : 'hidden', '#value' : 1}
  form['actions'] = {'#prefix' : \
    '<div class="container-inline">', '#suffix' : '</div>'}
  form['actions']['submit'] = {'#type' : 'submit', '#value' : \
    (yes if yes else lib_common.t('Confirm'))}
  form['actions']['cancel'] = {'#value' : cancel}
  form['#theme'] = 'confirm_form'
  return form




def admin_compact_mode():
  """
   Determine if a user is in compact mode.
  """
  return (lib_bootstrap.user.admin_compact_mode if \
    php.isset(lib_bootstrap.user, 'admin_compact_mode') else \
    variable_get('admin_compact_mode', False))



def admin_compact_page(mode = 'off'):
  """
   Menu callback; Sets whether the admin menu is in compact mode or not.
  
   @param mode
     Valid values are 'on' and 'off'.
  """
  plugin_user.save(lib_bootstrap.user, {'admin_compact_mode' : (mode == 'on')})
  lib_common.drupal_goto(lib_common.drupal_get_destination())



def get_module_admin_tasks(plugin):
  """
   Generate a list of tasks offered by a specified module.
  
   @param module
     Module name.
   @return
     An array of task links.
  """
  php.static(get_module_admin_tasks, 'items', None)
  admin_access = plugin_user.access('administer permissions')
  admin_tasks = {}
  if (get_module_admin_tasks.items is None):
    result = lib_database.db_query(
      "SELECT " + \
      "  m.load_functions, m.to_arg_functions, " + \
      "  m.access_callback, m.access_arguments, " + \
      "  m.page_callback, m.page_arguments, " + \
      "  m.title, m.title_callback, " + \
      "  m.title_arguments, m.type, ml.* " + \
      "FROM {menu_links} ml " + \
      "INNER JOIN {menu_router} m ON ml.router_path = m.path " + \
      "WHERE " + \
      "  ml.link_path LIKE 'admin/%' AND " + \
      "  hidden >= 0 AND " + \
      "  module = 'system' AND " + \
      "  m.number_parts > 2")
    get_module_admin_tasks.items = {}
    while True:
      item = lib_database.db_fetch_array(result)
      if not item:
        break
      lib_menu._menu_link_translate(item)
      if (item['access']):
        get_module_admin_tasks.items[item['router_path']] = item
  admin_tasks = {}
  admin_task_count = 0
  # Check for permissions.
  if (lib_plugin.plugin_hook(plugin, 'perm') and admin_access):
    admin_tasks[-1] = lib_common.l(lib_common.t('Configure permissions'), \
      'admin/user/permissions', {'fragment' : 'plugin-' +  plugin})
  # Check for menu items that are admin links.
  menu_ = lib_plugin.plugin_invoke(plugin, 'menu')
  if menu_:
    for path_ in php.array_keys(menu_):
      if (php.isset(get_module_admin_tasks.items[path_])):
        admin_tasks[ \
          get_module_admin_tasks.items[path_]['title'] + admin_task_count] = \
          l(get_module_admin_tasks.items[path_]['title'], path_)
        admin_task_count += 1
  return admin_tasks



def hook_cron():
  """
   Implementation of hook_cron().
  
   Remove older rows from flood and batch table. Remove old temporary files.
  """
  # Cleanup the flood.
  lib_database.db_query('DELETE FROM {flood} WHERE timestamp < %d', \
    php.time_() - 3600)
  # Cleanup the batch table.
  lib_database.db_query('DELETE FROM {batch} WHERE timestamp < %d', \
    php.time_() - 864000)
  # Remove temporary files that are older than DRUPAL_MAXIMUM_TEMP_FILE_AGE.
  result = lib_database.db_query(
    'SELECT * ' + \
    'FROM {files} ' + \
    'WHERE ' + \
    '  status = %d and ' + \
    '  timestamp < %d', \
    FILE_STATUS_TEMPORARY, \
    php.time_() - DRUPAL_MAXIMUM_TEMP_FILE_AGE)
  while True:
    file = lib_database.db_fetch_object(result)
    if not file:
      break
    if (php.file_exists(file.filepath)):
      # If files that exist cannot be deleted, continue so the database remains
      # consistent.
      if (not lib_path.file_delete(file.filepath)):
        lib_bootstrap.watchdog('file system', \
          'Could not delete temporary file "%path" during garbage collection', \
          {'%path' : file.filepath}, 'error')
        continue
    lib_database.db_query('DELETE FROM {files} WHERE fid = %d', file.fid)



def hook_hook_info():
  """
   Implementation of hook_hook_info().
  """
  return {
    'system' : {
      'cron' : {
        'run' : {
          'runs when' : lib_common.t('When cron runs')
        }
      }
    }
  }



def hook_action_info():
  """
   Implementation of hook_action_info().
  """
  return {
    'system_message_action' : {
      'type' : 'system',
      'description' : lib_common.t('Display a message to the user'),
      'configurable' : True,
      'hooks' : {
        'nodeapi' : ('view', 'insert', 'update', 'delete'),
        'comment' : ('view', 'insert', 'update', 'delete'),
        'user' : ('view', 'insert', 'update', 'delete', 'login'),
        'taxonomy' : ('insert', 'update', 'delete')
      }
    },
    'system_send_email_action' : {
      'description' : lib_common.t('Send e-mail'),
      'type' : 'system',
      'configurable' : True,
      'hooks' : {
        'nodeapi' : ('view', 'insert', 'update', 'delete'),
        'comment' : ('view', 'insert', 'update', 'delete'),
        'user' : ('view', 'insert', 'update', 'delete', 'login'),
        'taxonomy' : ('insert', 'update', 'delete')
      }
    },
    'system_block_ip_action' : {
      'description' : lib_common.t('Ban IP address of current user'),
      'type' : 'user',
      'configurable' : False,
      'hooks' : (),
    },
    'system_goto_action' : {
      'description' : lib_common.t('Redirect to URL'),
      'type' : 'system',
      'configurable' : True,
      'hooks' : {
        'nodeapi' : ('view', 'insert', 'update', 'delete'),
        'comment' : ('view', 'insert', 'update', 'delete'),
        'user' : ('view', 'insert', 'update', 'delete', 'login')
      }
    }
  }



def actions_manage():
  """
   Menu callback. Display an overview of available and configured actions.
  """
  output = ''
  actions = actions_list()
  actions_synchronize(actions)
  actions_map = actions_actions_map(actions)
  options = [lib_common.t('Choose an advanced action')]
  unconfigurable = []
  for key,array_ in actions_map.items():
    if (array_['configurable']):
      options[key] = array_['description'] +  '...'
    else:
      unconfigurable.append( array_ )
  row = []
  instances_present = lib_database.db_fetch_object(lib_database.db_query(\
    "SELECT aid FROM {actions} WHERE parameters != ''"))
  header_ = (
    {'data' : lib_common.t('Action type'), 'field' : 'type'},
    {'data' : lib_common.t('Description'), 'field' : 'description'},
    {'data' : (lib_common.t('Operations') if \
      instances_present else ''), 'colspan' : '2'}
  )
  sql = 'SELECT * FROM {actions}'
  result = pager_query(sql +  inc_tablesort.tablesort_sql(header_), 50)
  while True:
    action = lib_database.db_fetch_object(result)
    if not action:
      break
    row.append((
      {'data' : action.type_},
      {'data' : action.description},
      {'data' : (lib_common.l(lib_common.t('configure'), \
        "admin/settings/actions/configure/%s" % action.aid) if
        action.parameters else '')},
      {'data' : (lib_common.l(lib_common.t('delete'), \
        "admin/settings/actions/delete/%s" % action.aid) if \
        action.parameters else '')}
    ))
  if (row):
    pager = lib_theme.theme('pager', None, 50, 0)
    if (not empty(pager)):
      row.append([{'data' : pager, 'colspan' : '3'}])
    output += '<h3>' +  lib_common.t('Actions available to Drupal:')  + '</h3>'
    output += lib_theme.theme('table', header, row)
  if (actions_map):
    output += inc_form.drupal_get_form('system_actions_manage_form', options)
  return output



def actions_manage_form(form_state, options = []):
  """
   Define the form for the actions overview page.
  
   @see system_actions_manage_form_submit()
   @ingroup forms
   @param form_state
     An associative array containing the current state of the form; not used.
   @param options
     An array of configurable actions.
   @return
     Form definition.
  """
  form['parent'] = {
    '#type' : 'fieldset',
    '#title' : lib_common.t('Make a new advanced action available'),
    '#prefix' : '<div class="container-inline">',
    '#suffix' : '</div>'
  }
  form['parent']['action'] = {
    '#type' : 'select',
    '#default_value' : '',
    '#options' : options,
    '#description' : ''
  }
  form['parent']['buttons']['submit'] = {
    '#type' : 'submit',
    '#value' : lib_common.t('Create')
  }
  return form



def actions_manage_form_submit(form, form_state):
  """
   Process system_actions_manage form submissions.
  """
  php.Reference.check(form_state)
  if (form_state['values']['action']):
    form_state['redirect'] = 'admin/settings/actions/configure/%s' % \
    form_state['values']['action']



def actions_configure(form_state, action = None):
  """
   Menu callback. Create the form for configuration of a single action.
  
   We provide the "Description" field. The rest of the form
   is provided by the action. We then provide the Save button.
   Because we are combining unknown form elements with the action
   configuration form, we use actions_ prefix on our elements.
  
   @see system_actions_configure_validate()
   @see system_actions_configure_submit()
   @param action
     md5 hash of action ID or an integer. If it's an md5 hash, we
     are creating a new instance. If it's an integer, we're editing
     an existing instance.
   @return
     Form definition.
  """
  if (action is None):
    lib_common.drupal_goto('admin/settings/actions')
  actions_map = actions_actions_map(actions_list())
  edit = []
  # Numeric action denotes saved instance of a configurable action
  # else we are creating a new action instance.
  if (php.is_numeric(action)):
    aid = action
    # Load stored parameter values from database.
    data = lib_database.db_fetch_object(lib_database.db_query(\
      "SELECT * FROM {actions} WHERE aid = %d", p.intval(aid)))
    edit['actions_description'] = data.description
    edit['actions_type'] = data.type
    function = data.callback
    action = php.md5(data.callback)
    params = php.unserialize(data.parameters)
    if (params):
      for name,val in params.items():
        edit[name] = val
  else:
    aid = None
    function = actions_map[action]['callback']
    edit['actions_description'] = actions_map[action]['description']
    edit['actions_type'] = actions_map[action]['type']
  form['actions_description'] = {
    '#type' : 'textfield',
    '#title' : lib_common.t('Description'),
    '#default_value' : edit['actions_description'],
    '#maxlength' : '255',
    '#description' : lib_common.t(\
      'A unique description for this advanced action. This description ' + \
      'will be displayed in the interface of modules that integrate ' + \
      'with actions, such as Trigger module.'),
    '#weight' : -10
  }
  action_form = function +  '_form'
  form = php.array_merge(form, action_form(edit))
  form['actions_type'] = {
    '#type' : 'value',
    '#value' : edit['actions_type'],
  }
  form['actions_action'] = {
    '#type' : 'hidden',
    '#value' : action,
  }
  # aid is set when configuring an existing action instance.
  if (aid is not None):
    form['actions_aid'] = {
      '#type' : 'hidden',
      '#value' : aid,
    }
  form['actions_configured'] = {
    '#type' : 'hidden',
    '#value' : '1',
  }
  form['buttons']['submit'] = {
    '#type' : 'submit',
    '#value' : lib_common.t('Save'),
    '#weight' : 13
  }
  return form



def actions_configure_validate(form, form_state):
  """
   Validate system_actions_configure form submissions.
  """
  function = actions_function_lookup(form_state['values']['actions_action']) + \
    '_validate'
  # Hand off validation to the action.
  if (php.function_exists(function)):
    function(form, form_state)



def actions_configure_submit(form, form_state):
  """
   Process system_actions_configure form submissions.
  """
  php.Reference.check(form_state)
  function = actions_function_lookup(form_state['values']['actions_action'])
  submit_function = function +  '_submit'
  # Action will return keyed array of values to store.
  params = submit_function(form, form_state)
  aid = (form_state['values']['actions_aid'] if \
    php.isset(form_state['values']['actions_aid']) else None)
  actions_save(function, form_state['values']['actions_type'], params, \
    form_state['values']['actions_description'], aid)
  lib_bootstrap.drupal_set_message(t('The action has been successfully saved.'))
  form_state['redirect'] = 'admin/settings/actions/manage'


def actions_delete_form(form_state, action):
  """
   Create the form for confirmation of deleting an action.
  
   @ingroup forms
   @see system_actions_delete_form_submit()
  """
  form['aid'] = {
    '#type' : 'hidden',
    '#value' : action.aid,
  }
  return confirm_form(form,
    lib_common.t('Are you sure you want to delete the action %action?', \
      {'%action' : action.description}),
    'admin/settings/actions/manage',
    lib_common.t('This cannot be undone.'),
    lib_common.t('Delete'), lib_common.t('Cancel')
  )



def actions_delete_form_submit(form, form_state):
  """
   Process system_actions_delete form submissions.
  
   Post-deletion operations for action deletion.
  """
  php.Reference.check(form_state)
  aid = form_state['values']['aid']
  action = actions_load(aid)
  actions_delete(aid)
  description = lib_bootstrap.check_plain(action.description)
  lib_bootstrap.watchdog('user', 'Deleted action %aid (%action)', \
    {'%aid' : aid, '%action' : description})
  lib_common.drupal_set_message(lib_common.t('Action %action was deleted', \
    {'%action' : description}))
  form_state['redirect'] = 'admin/settings/actions/manage'



def action_delete_orphans_post(orphaned):
  """
   Post-deletion operations for deleting action orphans.
  
   @param orphaned
     An array of orphaned actions.
  """
  for callback in orphaned:
    lib_common.drupal_set_message(lib_common.t(\
      "Deleted orphaned action (%action).", {'%action' : callback}))



def actions_remove_orphans():
  """
   Remove actions that are in the database but not supported by any enabled module.
  """
  actions_synchronize(actions_list(), True)
  lib_common.drupal_goto('admin/settings/actions/manage')



def send_email_action_form(context):
  """
   Return a form definition so the Send email action can be configured.
  
   @see system_send_email_action_validate()
   @see system_send_email_action_submit()
   @param context
     Default values (if we are editing an existing action instance).
   @return
     Form definition.
  """
  # Set default values for form.
  if (not php.isset(context, 'recipient')):
    context['recipient'] = ''
  if (not php.isset(context, 'subject')):
    context['subject'] = ''
  if (not php.isset(context, 'message')):
    context['message'] = ''
  form['recipient'] = {
    '#type' : 'textfield',
    '#title' : lib_common.t('Recipient'),
    '#default_value' : context['recipient'],
    '#maxlength' : '254',
    '#description' : lib_common.t(\
      'The email address to which the message should be sent OR ' + \
      'enter %author if you would like to send an e-mail to the author ' + \
      'of the original post.', {'%author' : '%author'})
  }
  form['subject'] = {
    '#type' : 'textfield',
    '#title' : lib_common.t('Subject'),
    '#default_value' : context['subject'],
    '#maxlength' : '254',
    '#description' : lib_common.t('The subject of the message.')
  }
  form['message'] = {
    '#type' : 'textarea',
    '#title' : lib_common.t('Message'),
    '#default_value' : context['message'],
    '#cols' : '80',
    '#rows' : '20',
    '#description' : lib_common.t(
      'The message that should be sent. You may include the following ' + \
      'variables: %site_name, %username, %node_url, %node_type, %title, ' + \
      '%teaser, %body. Not all variables will be available in all contexts.')
  }
  return form



def send_email_action_validate(form, form_state):
  """
   Validate system_send_email_action form submissions.
  """
  form_values = form_state['values']
  # Validate the configuration form.
  if (not valid_email_address(form_values['recipient']) and \
      form_values['recipient'] != '%author'):
    # We want the literal %author placeholder
    # to be emphasized in the error message.
    inc_form.form_set_error('recipient', lib_common.t(
      'Please enter a valid email address or %author.', \
      {'%author' : '%author'}))



def send_email_action_submit(form, form_state):
  """
   Process system_send_email_action form submissions.
  """
  form_values = form_state['values']
  # Process the HTML form to store configuration. The keyed array that
  # we return will be serialized to the database.
  params = {
    'recipient' : form_values['recipient'],
    'subject'   : form_values['subject'],
    'message'   : form_values['message']
  }
  return params



def send_email_action(object_, context):
  """
   Implementation of a configurable Drupal action. Sends an email.
  """
  if context['hook'] == 'nodeapi':
    # Because this is not an action of type 'node' the node
    # will not be passed as object, but it will still be available
    # in context.
    node = context['node']
  # The comment hook provides nid, in context.
  elif context['hook'] == 'comment':
    comment = context['comment']
    node = plugin_node.load(comment.nid)
  elif context['hook'] == 'user':
    # Because this is not an action of type 'user' the user
    # object is not passed as object, but it will still be available
    # in context.
    account = context['account']
    if (php.isset(context, 'node')):
      node = context['node']
    elif (context['recipient'] == '%author'):
      # If we don't have a node, we don't have a node author.
      lib_bootstrap.watchdog('error', \
        'Cannot use %author token in this context.')
      return
  else:
    # We are being called directly.
    node = object_
  recipient = context['recipient']
  if node is not None:
    if (account is None):
      account = plugin_user.load({'uid' : node.uid})
    if (recipient == '%author'):
      recipient = account.mail
  if (not isset(account)):
    account = lib_bootstrap.user
  language = plugin_user.preferred_language(account)
  params = {'account' : account, 'object' : object_, 'context' : context}
  if (node is not None):
    params['node'] = node
  if (inc_mail.drupal_mail('system', 'action_send_email', recipient, \
      language, params)):
    lib_bootstrap.watchdog('action', 'Sent email to %recipient', \
      {'%recipient' : recipient})
  else:
    lib_bootstrap.watchdog('error', 'Unable to send email to %recipient', \
      {'%recipient' : recipient})



def hook_mail(key, message, params):
  """
   Implementation of hook_mail().
  """
  php.Reference.check(message)
  account = params['account']
  context = params['context']
  variables_ = {
    '%site_name' : lib_bootstrap.variable_get('site_name', 'Drupal'),
    '%username' : account.name,
  }
  if (context['hook'] == 'taxonomy'):
    object_ = params['object']
    vocabulary = plugin_taxonomy.vocabulary_load(object_.vid)
    variables_ += {
      '%term_name' : object_.name,
      '%term_description' : object_.description,
      '%term_id' : object_.tid,
      '%vocabulary_name' : vocabulary.name,
      '%vocabulary_description' : vocabulary.description,
      '%vocabulary_id' : vocabulary.vid
    }
  # Node-based variable translation is only available if we have a node.
  if (php.isset(params['node'])):
    node = params['node']
    variables_ += {
      '%uid' : node.uid,
      '%node_url' : lib_common.url('node/' + node.nid, {'absolute' : True}),
      '%node_type' : plugin_node.get_types('name', node),
      '%title' : node.title,
      '%teaser' : node.teaser,
      '%body' : node.body
    }
  subject = php.strtr(context['subject'], variables_)
  body = php.strtr(context['message'], variables_)
  message['subject'] += php.str_replace(("\r", "\n"), '', subject)
  message['body'].append( inc_mail.drupal_html_to_text(body) )




def message_action_form(context):
  form['message'] = {
    '#type' : 'textarea',
    '#title' : lib_common.t('Message'),
    '#default_value' : (context['message'] if \
      php.isset(context['message']) else ''),
    '#required' : True,
    '#rows' : '8',
    '#description' : lib_common.t(\
      'The message to be displayed to the current user. You may include ' + \
      'the following variables: %site_name, %username, %node_url, ' + \
      '%node_type, %title, %teaser, %body. Not all variables will be ' + \
      'available in all contexts.')
  }
  return form


def message_action_submit(form, form_state):
  return {'message' : form_state['values']['message']}



def message_action(object_, context = []):
  """
   A configurable Drupal action. Sends a message to the current user's screen.
  """
  php.Reference.check(object_)
  variables_ = {
    '%site_name' : lib_common.variable_get('site_name', 'Drupal'),
    '%username' : (lib_bootstrap.user.name if lib_bootstrap.user.name else \
      lib_bootstrap.variable_get('anonymous', lib_common.t('Anonymous')))
  }
  # This action can be called in any context, but if placeholders
  # are used a node object must be present to be the source
  # of substituted text.
  if context['hook'] == 'nodeapi':
    # Because this is not an action of type 'node' the node
    # will not be passed as object, but it will still be available
    # in context.
    node = context['node']
  # The comment hook also provides the node, in context.
  elif context['hook'] == 'comment':
    comment = context['comment']
    node = plugin_node.load(comment.nid)
  elif context['hook'] == 'taxonomy':
    vocabulary = plugin_taxonomy.vocabulary_load(object_.vid)
    variables_ = php.array_merge(variables_, {
      '%term_name' : object_.name,
      '%term_description' : object_.description,
      '%term_id' : object_.tid,
      '%vocabulary_name' : vocabulary.name,
      '%vocabulary_description' : vocabulary.description,
      '%vocabulary_id' : vocabulary.vid
    })
  else:
    # We are being called directly.
    node = object_
  if (php.isset(node) and php.is_object(node)):
    variables_ = php.array_merge(variables_, {
      '%uid' : node.uid,
      '%node_url' : lib_common.url('node/' +  node.nid, {'absolute' : True}),
      '%node_type' : lib_bootstrap.check_plain(\
        plugin_node.get_types('name', node)),
      '%title' : plugin_filter.xss(node.title),
      '%teaser' : plugin_filter.xss(node.teaser),
      '%body' : plugin_filter.xss(node.body)
    })
  context['message'] = php.strtr(context['message'], variables_)
  lib_bootstrap.drupal_set_message(context['message'])



def goto_action_form(context):
  """
   Implementation of a configurable Drupal action. Redirect user to a URL.
  """
  form['url'] = {
    '#type' : 'textfield',
    '#title' : lib_common.t('URL'),
    '#description' : t(\
      'The URL to which the user should be redirected. This can be an ' + \
      'internal URL like node/1234 or an external URL like http://drupal.org.'),
    '#default_value' : (context['url'] if php.isset(context['url']) else ''),
    '#required' : True,
  }
  return form




def goto_action_submit(form, form_state):
  return {
    'url' : form_state['values']['url']
  }



def goto_action(object_, context):
  lib_common.drupal_goto(context['url'])



def block_ip_action():
  """
   Implementation of a Drupal action.
   Blocks the user's IP address.
  """
  ip = lib_bootstrap.ip_address()
  db_query("INSERT INTO {blocked_ips} (ip) VALUES ('%s')", ip);
  lib_bootstrap.watchdog('action', 'Banned IP address %ip', {'%ip' : ip})



def _zonelist():
  """
   Generate an array of time zones and their local time&date.
  """
  timestamp = time()
  zonelist = array(-11, -10, -9.5, -9, -8, -7, -6, -5, -4, -3.5, -3, \
    -2, -1, 0, 1, 2, 3, 3.5, 4, 5, 5.5, 5.75, 6, 6.5, 7, 8, 9, 9.5, 10, \
    10.5, 11, 11.5, 12, 12.75, 13, 14)
  zones = []
  for offset in zonelist:
    zone = offset * 3600
    zones[zone] = p.format_date(timestamp, 'custom', \
      lib_bootstrap.variable_get('date_format_long', \
      'l, F j, Y - H:i') +  ' O', zone)
  return zones



def check_http_request():
  """
   Checks whether the server is capable of issuing HTTP requests.
  
   The function sets the drupal_http_request_fail system variable to True if
   drupal_http_request() does not work and then the system status report page
   will contain an error.
  
   @return
    Whether the admin/reports/request-test page can be requested via HTTP
    and contains the same output as if called via the menu system.
  """
  # Check whether we can do any request at all. First get the results for
  # a very simple page which has access True set via the menu system. Then,
  # try to drupal_http_request() the same page and compare.
  # ob_start()
  path_ = 'admin/reports/request-test'
  lib_menu.menu_execute_active_handler(path_)
  nothing = None
  # nothing = ob_get_contents()
  # ob_end_clean()
  result = lib_common.drupal_http_request(lib_common.url(path_, \
    {'absolute' : True}))
  works = (php.isset(result.data) and (result.data == nothing))
  lib_bootstrap.variable_set('drupal_http_request_fails', not works)
  return works



def theme_powered_by(image_path):
  """
   Format the Powered by Drupal text.
  
   @ingroup themeable
  """
  image = theme('image', image_path, \
    lib_common.t(\
    'Powered by Drupal, an open source content management system'), \
    lib_common.t(\
    'Powered by Drupal, an open source content management system'))
  return lib_common.l(image, 'http://drupal.org', \
    {'html' : True, 'absolute' : True, 'external' : True})



def theme_compact_link():
  """
   Display the link to show or hide inline help descriptions.
  
   @ingroup themeable
  """
  output = '<div class="compact-link">'
  if (admin_compact_mode()):
    output += lib_common.l(lib_common.t('Show descriptions'), \
      'admin/compact/off', {'attributes' : \
      {'title' : lib_common.t('Expand layout to include descriptions.')}, \
      'query' : lib_common.drupal_get_destination()})
  else:
    output += lib_common.l(lib_common.t('Hide descriptions'), \
      'admin/compact/on', {'attributes' : \
      {'title' : lib_common.t('Compress layout by hiding descriptions.')}, \
      'query' : drupal_get_destination()})
  output += '</div>'
  return output



def theme_meta_generator_html(version = VERSION):
  """
   Send Drupal and the major version number in the META GENERATOR HTML.
  
   @ingroup themeable
  """
  lib_common.drupal_set_html_head('<meta name="Generator" content="Drupal ' +  \
    version  + ' (http://drupal.org)" />')



def theme_meta_generator_header(version = VERSION):
  """
   Send Drupal and the major version number in the HTTP headers.
  
   @ingroup themeable
  """
  lib_common.drupal_set_header(\
    'X-Generator: Drupal ' +  version  + ' (http://drupal.org)')



