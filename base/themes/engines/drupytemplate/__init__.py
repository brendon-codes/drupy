#!/usr/bin/env python
# $Id: phptemplate.engine,v 1.70 2008/04/14 17:48:45 dries Exp $

"""
  Handles integration of templates written in pure php
  with the Drupal theme system.

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

__version__ = "$Revision: 1 $"

from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyImport
from includes import theme as lib_theme

def hook_init(template):
  file = php.dirname(template.filename) + '/template.py'
  if (php.file_exists(file)):
    lib_theme.processors['template'] = DrupyImport.import_file(file)



def hook_theme(existing, type_, this_theme, path_):
  """
    Implementation of hook_theme to tell Drupal what templates the engine
    and the current theme use. The existing argument will contain hooks
    pre-defined by Drupal so that we can use that information if
    we need to.
  """
  templates = drupal_find_theme_functions(existing, ('drupytemplate', this_theme));
  templates += drupal_find_theme_templates(existing, '.tpl.php', path_);
  return templates


