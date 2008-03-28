#!/usr/bin/env python

# $Id: index.php,v 1.94 2007/12/26 08:46:48 dries Exp $

#
# @file
# The PHP page that serves all page requests on a Drupal installation.
#
# The routines here dispatch control to the appropriate handler, which then
# prints the appropriate page.
#
# All Drupal code is released under the GNU General Public License.
# See COPYRIGHT.txt and LICENSE.txt.
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





