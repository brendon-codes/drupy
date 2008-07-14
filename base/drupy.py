#!/usr/bin/env python

"""
  Drupy CGI and CLI execution script.

  @package base
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
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

import time
import re
import sys
from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyImport
from includes import bootstrap as lib_bootstrap
from includes import plugin as lib_plugin
from includes import theme as lib_theme


phases = (
  (lib_bootstrap.DRUPAL_BOOTSTRAP_CONFIGURATION, \
   'DRUPAL_BOOTSTRAP_CONFIGURATION'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE, \
   'DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_DATABASE, \
   'DRUPAL_BOOTSTRAP_DATABASE'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_ACCESS, \
   'DRUPAL_BOOTSTRAP_ACCESS'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_SESSION, \
   'DRUPAL_BOOTSTRAP_SESSION'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE, \
   'DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_LANGUAGE, \
   'DRUPAL_BOOTSTRAP_LANGUAGE'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_PATH, \
   'DRUPAL_BOOTSTRAP_PATH'),
  (lib_bootstrap.DRUPAL_BOOTSTRAP_FULL, \
   'DRUPAL_BOOTSTRAP_FULL')
);

if 'q' not in php.GET:
  php.GET['q'] = 'node'

which_phase = phases[8];
lib_bootstrap.drupal_bootstrap(which_phase[0]);
stamp, revised = time.strftime("%c GMT||%m/%d/%Y", time.gmtime()).split('||')

out_plugins = php.print_r(lib_plugin.loaded_plugins, True)
out_plugins_html = php.htmlspecialchars(out_plugins)

out_themes = php.print_r(lib_theme.loaded_themes, True)
out_themes_html = php.htmlspecialchars(out_themes)

out_vars = php.print_r(vars(), True)
out_vars = re.sub('[a-zA-Z0-9_\.-]+@.+?\.[a-zA-Z]+', '********', out_vars)
out_vars = re.sub('[a-zA-Z0-9]{32}', \
                  '********************************', out_vars)
out_vars = php.htmlspecialchars(out_vars)

out_mods = php.print_r(DrupyImport.modules(), True)
out_mods = php.htmlspecialchars(out_mods)

#
# Executed from Web
#
if php.SERVER['WEB']:
  print "<?xml version='1.0' encoding='UTF-8'?>"
  print "<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' " + \
    "'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>"
  print "<html xmlns='http://www.w3.org/1999/xhtml'>"
  print "<head>"
  print "<title>Drupy: Drupal in Python</title>"
  print "<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />"
  print "<meta name='revised' content='DrupyStatus, %s' />" % revised
  print "</head>"
  print "<body>"
  print "<h1>Drupy Bootstrap Diagnostic Status</h1>"
  print "<h2>Bootstrap: Completed Phase '%s' (%s)</h2>" % \
    (which_phase[1],which_phase[0])
  print "<h3>Generated: %s</h3>" % stamp
  print "<h4 style='color:blue;'>"
  print "The following Drupy plugins are loaded. "
  print "A Drupy plugin is the equivalent of a Drupal module."
  print "</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_plugins_html
  print "<h4 style='color:blue;'>"
  print "The following theme and template modules are loaded. "
  print "drupytemplate is the equivalent of Drupal's phptemplate"
  print "</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_themes_html
  print "<h4 style='color:blue;'>Global Scope Objects</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_vars
  print "<h4 style='color:blue;'>Loaded Python Modules</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_mods
  print "</body>"
  print "</html>"
#
# Executed from CLI
#
else:
  print "Drupy Bootstrap Diagnostic Status"
  print "Bootstrap: Completed Phase '%s' (%s)" % \
    (which_phase[1],which_phase[0])
  print "Generated: %s" % stamp
  print
  print "The following Drupy plugins are loaded."
  print "A Drupy plugin is the equivalent of a Drupal plugin"
  print
  print out_plugins
  print
  print "The following Drupy theme and template modules are loaded."
  print "drupytemplate is the equivalent of Drupal's phptemplate"
  print
  print out_themes
  print
  print "You may now query any Drupal Bootstrap object."
  print

#
# Flush
#
php.flush()
  
  
