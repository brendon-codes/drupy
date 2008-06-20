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
import time
import re
import sys
from lib.drupy import DrupyPHP as p
from lib.drupy import DrupyHelper
from includes import bootstrap as inc_bootstrap

phases = (
  (inc_bootstrap.DRUPAL_BOOTSTRAP_CONFIGURATION,    'DRUPAL_BOOTSTRAP_CONFIGURATION'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE, 'DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_DATABASE,         'DRUPAL_BOOTSTRAP_DATABASE'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_ACCESS,           'DRUPAL_BOOTSTRAP_ACCESS'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_SESSION,          'DRUPAL_BOOTSTRAP_SESSION'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE,  'DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_LANGUAGE,         'DRUPAL_BOOTSTRAP_LANGUAGE'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_PATH,             'DRUPAL_BOOTSTRAP_PATH'),
  (inc_bootstrap.DRUPAL_BOOTSTRAP_FULL,             'DRUPAL_BOOTSTRAP_FULL')
);

which_phase = phases[7];
inc_bootstrap.drupal_bootstrap(which_phase[0]);
stamp, revised = time.strftime("%c GMT||%m/%d/%Y", time.gmtime()).split('||')

out_vars = p.print_r(vars(), True)
out_vars = re.sub('[a-zA-Z0-9_\.-]+@.+?\.[a-zA-Z]+', '********', out_vars)
out_vars = re.sub('[a-zA-Z0-9]{32}', '********************************', out_vars)
out_vars = p.htmlspecialchars(out_vars)
out_mods = p.print_r(DrupyHelper.modules(), True)
out_mods = p.htmlspecialchars(out_mods)

#
# Executed from Web
#
if p.SERVER['WEB']:
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
  print "<h2>Bootstrap: Completed Phase '%s' (%s)</h2>" % (which_phase[1],which_phase[0])
  print "<h3>Generated: %s</h3>" % stamp
  print "<h4>Global Scope Objects</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_vars
  print "<h4>Loaded Modules</h4>"
  print "<pre style='background-color:yellow;'>%s</pre>" % out_mods
  print "</body>"
  print "</html>"
#
# Executed from CLI
#
else:
  print "Drupy Bootstrap Diagnostic Status"
  print "Bootstrap: Completed Phase '%s' (%s)" % (which_phase[1],which_phase[0])
  print "Generated: %s" % stamp
  print "You may now query any Drupal Bootstrap object."

#
# Flush
#
p.flush()
  
  
