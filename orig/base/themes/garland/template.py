#!/usr/bin/env python
# Id: template.php,v 1.19 2008/06/25 09:12:25 dries Exp $

"""
  Garland theme template override file

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's themes/garland/template.php
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
from includes import bootstrap as lib_bootstrap
from includes import common as lib_common
from includes import plugin as lib_plugin

def theme_breadcrumb(breadcrumb):
  """
   Return a themed breadcrumb trail.
  
   @param breadcrumb
     An array containing the breadcrumb links.
   @return a string containing the breadcrumb output.
  """
  if (not php.empty(breadcrumb)):
    return '<div class="breadcrumb">' +  \
      php.implode(' &#8250; ', breadcrumb)  + '</div>'


def theme_comment_wrapper(content, node):
  """
   Allow themable wrapping of all comments.
  """
  if (not content or node.type_ == 'forum'):
    return '<div id="comments">' +  content  + '</div>'
  else:
    return '<div id="comments"><h2 class="comments">' + \
      lib_common.t('Comments')  + '</h2>' + content + '</div>'



def theme_preprocess_page(vars_):
  """
   Override or insert variables into the page template.
  """
  php.Reference.check(vars_)
  vars_['tabs2'] = menu_secondary_local_tasks()
  vars_['primary_nav'] = (lib_theme.theme('links', \
    vars_['main_menu'], {'class' : 'links main-menu'}) if \
    php.isset(vars_, 'main_menu') else False)
  vars_['secondary_nav'] =  (lib_theme.theme('links', \
    vars_['secondary_menu'], \
    {'class' : 'links secondary-menu'}) if \
    php.isset(vars_, 'secondary_menu') else False)
  vars_['ie_styles'] = get_ie_styles()
  # Prepare header
  site_fields = []
  if (not php.empty(vars_['site_name'])):
    site_fields.append( check_plain(vars_['site_name']) )
  if (not php.empty(vars_['site_slogan'])):
    site_fields.append( check_plain(vars_['site_slogan']) )
  vars_['site_title'] = php.implode(' ', site_fields)
  if (not php.empty(site_fields)):
    site_fields[0] = '<span>' + site_fields[0] + '</span>'
  vars_['site_html'] = php.implode(' ', site_fields)
  # Hook into color.module
  if (lib_plugin.exists('color')):
    lib_plugin.plugins['color']._page_alter(vars_)



def theme_menu_local_tasks():
  """
   Returns the rendered local tasks. The default implementation renders
   them as tabs. Overridden to split the secondary tasks.
  """
  return menu_primary_local_tasks()


def drupytemplate_comment_submitted(comment):
  """
   Format the Submitted by username on date/time' for each comment.
  """
  return lib_common.t('not datetime &#8212; not username',
    {
      'not username' : lib_theme.theme('username', comment),
      'not datetime' : php.format_date(comment.timestamp)
    })



def theme_node_submitted(node):
  """
   Format the 'Submitted by username on date/time' for each node.
  """
  return lib_common.t('not datetime &#8212; not username',
    {
      'not username' : lib_theme.theme('username', node),
      'not datetime' : php.format_date(node.created),
    })



def theme_get_ie_styles():
  """
   Generates IE CSS links for LTR and RTL languages.
  """
  ie_styles = '<link type="text/css" rel="stylesheet" media="all" href="' +  \
    lib_bootstrap.base_path()  + lib_theme.path_to_theme() + \
    '/fix-ie.css" />' + "\n"
  if (lib_plugin.exists('locale') and \
      lib_bootstrap.language.direction == \
      lib_plugin.plugins['locale'].LANGUAGE_RTL):
    ie_styles += \
      '      <style type="text/css" media="all">@import "' +  \
      lib_bootstrap.base_path()  + lib_theme.path_to_theme() + \
      '/fix-ie-rtl.css";</style>' + "\n"
  return ie_styles



