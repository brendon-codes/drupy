#!/usr/bin/env python


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file drupy.py (ported from Drupal's drupal.inc)
#  Test Execution script for drupy
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


execfile('./lib/drupy/DrupyPHP.py', globals())
execfile('./includes/bootstrap.py', globals());

phases = [
  DRUPAL_BOOTSTRAP_CONFIGURATION,
  DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE,
  DRUPAL_BOOTSTRAP_DATABASE,
  DRUPAL_BOOTSTRAP_ACCESS,
  DRUPAL_BOOTSTRAP_SESSION,
  DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE,
  DRUPAL_BOOTSTRAP_LANGUAGE,
  DRUPAL_BOOTSTRAP_PATH,
  DRUPAL_BOOTSTRAP_FULL
];

which_phase = phases[2];
drupal_bootstrap(which_phase);

# Bootstrapping tests
print "Content-Type: text/html\r\n\r\n";
print "<h1>Drupy</h1>"
print "<h2>Bootstrap Completed Phase(%s)</h2>" % which_phase;
print "<h3>Globals</h3>";
print "<div style='width: 400px; background-color:yellow;'>";
print globals();
print "</div>";