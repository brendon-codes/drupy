#!/usr/bin/env python
# $Id: index.php,v 1.94 2007/12/26 08:46:48 dries Exp $

"""
  The Python page that serves all page requests on a Drupy installation.
  The routines here dispatch control to the appropriate handler, which then
  prints the appropriate page.

  @package default
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's index.php
  @note
    THIS FILE IS NOT FUNCTIONAL.
    TO SEE A RUNNING INSTANCE OF DRUPY.
    PLEASE RUN DRUPY.PY AS A CGI OR CLI
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
from includes import menu as lib_menu
from includes import common as lib_common
from includes import theme as lib_theme

print
print "THIS FILE IS NOT FUNCTIONAL"
print "TO SEE A RUNNING INSTANCE OF DRUPY"
print "PLEASE RUN DRUPY.PY AS A CGI OR CLI"
print
php.flush()
exit(1)


#
# We need to catch all exceptions and send them to the
# default exception handler
#
drupal_bootstrap(lib_bootstrap.DRUPAL_BOOTSTRAP_FULL);
return_ = lib_menu.execute_active_handler();
# Menu status constants are integers; page content is a string.
if (is_int(return_)):
  if (return_ == lib_menu.MENU_NOT_FOUND):
      lib_bootstrap.drupal_not_found();
  elif (return_ == lib_menu.MENU_ACCESS_DENIED):
    lib_common.drupal_access_denied();
  elif (return_ == lib_menu.MENU_SITE_OFFLINE):
    lib_common.drupal_site_offline();
else:
  # Print any value (including an empty string) except NULL or undefined:
  print lib_theme.theme('page', return_);
lib_common.drupal_page_footer();

#
# Flush the output
#
php.flush()


