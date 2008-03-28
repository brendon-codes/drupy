#!/usr/bin/env python

#
# Test Execution script for drupy
#

execfile('./lib/drupy/DrupyPHP.py', globals())
require_once('./includes/bootstrap.py', globals());

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

which_phase = phases[1];
drupal_bootstrap(which_phase);

# Bootstrapping tests
print "Content-Type: text/html\r\n\r\n";
print "<h1>Drupy</h1>"
print "<h2>Bootstrap Completed Phase(%s)</h2>" % which_phase;
print "<h3>Globals</h3>";
print "<div style='width: 400px; background-color:yellow;'>";
print globals();
print "</div>";