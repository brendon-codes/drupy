#!/usr/bin/env php
<?php
/**
 * Converts drupal core v7 serialized table data to YAML
 * 
 * 
 */
if (!array_key_exists( 1, $argv ) && !is_dir($argv[1])) {
  printf('You must provide a root drupal directory.');
  exit(1);
}
chdir($argv[1]);
require_once('includes/bootstrap.inc');
drupal_bootstrap(DRUPAL_BOOTSTRAP_DATABASE);

?>