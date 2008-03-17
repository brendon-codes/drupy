#!/usr/bin/env python

#
# Test Execution script for drupy
#

execfile('./lib/drupy/php.py', globals())
execfile('./lib/drupy/env.py', globals())
#require_once('./includes/bootstrap.py', globals());

#
#Only one of these can be run
#
#drupal_bootstrap(DRUPAL_BOOTSTRAP_CONFIGURATION);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_EARLY_PAGE_CACHE);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_DATABASE);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_ACCESS);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_SESSION);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_LATE_PAGE_CACHE);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_LANGUAGE);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_PATH);
#drupal_bootstrap(DRUPAL_BOOTSTRAP_FULL);

# Bootstrapping tests
print "Content-Type: text/plain\r\n\r\n"
print _SERVER['REQUEST_METHOD']