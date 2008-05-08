#!/usr/bin/env python
# $Id: index.php,v 1.94 2007/12/26 08:46:48 dries Exp $

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file index.py (ported from Drupal's index.php)
#  The Python page that serves all page requests on a Drupy installation.
#  The routines here dispatch control to the appropriate handler, which then
#  prints the appropriate page.
#  All Drupy code is released under the GNU General Public License.
# @see COPYRIGHT.txt, LICENSE.txt.
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


execfile('./lib/drupy/DrupyPHP.py', globals());
execfile('./includes/bootstrap.py', globals());

#
# We need to catch all exceptions and send them to the
# default exception handler
#
drupal_bootstrap(DRUPAL_BOOTSTRAP_FULL);
_return = menu_execute_active_handler();
# Menu status constants are integers; page content is a string.
if (is_int(_return)):
  if (_return == MENU_NOT_FOUND):
      drupal_not_found();
  elif (_return == MENU_ACCESS_DENIED):
    drupal_access_denied();
  elif (_return == MENU_SITE_OFFLINE):
    drupal_site_offline();
else:
  # Print any value (including an empty string) except NULL or undefined:
  print theme('page', _return);
drupal_page_footer();





