<?php
// $Id: phptemplate.engine,v 1.70 2008/04/14 17:48:45 dries Exp $

/**
 * @file
 * Handles integration of templates written in pure php with the Drupal theme system.
 */

function phptemplate_init($template) {
  $file = dirname($template->filename) . '/template.php';
  if (file_exists($file)) {
    include_once "./$file";
  }
}

/**
 * Implementation of hook_theme to tell Drupal what templates the engine
 * and the current theme use. The $existing argument will contain hooks
 * pre-defined by Drupal so that we can use that information if
 * we need to.
 */
function phptemplate_theme($existing, $type, $theme, $path) {
  $templates = drupal_find_theme_functions($existing, array('phptemplate', $theme));
  $templates += drupal_find_theme_templates($existing, '.tpl.php', $path);
  return $templates;
}

