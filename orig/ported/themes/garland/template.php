<?php
// $Id: template.php,v 1.19 2008/06/25 09:12:25 dries Exp $

/**
 * Return a themed breadcrumb trail.
 *
 * @param $breadcrumb
 *   An array containing the breadcrumb links.
 * @return a string containing the breadcrumb output.
 */
function garland_breadcrumb($breadcrumb) {
  if (!empty($breadcrumb)) {
    return '<div class="breadcrumb">' . implode(' › ', $breadcrumb) . '</div>';
  }
}

/**
 * Allow themable wrapping of all comments.
 */
function garland_comment_wrapper($content, $node) {
  if (!$content || $node->type == 'forum') {
    return '<div id="comments">' . $content . '</div>';
  }
  else {
    return '<div id="comments"><h2 class="comments">' . t('Comments') . '</h2>' . $content . '</div>';
  }
}

/**
 * Override or insert variables into the page template.
 */
function garland_preprocess_page(&$vars) {
  $vars['tabs2'] = menu_secondary_local_tasks();
  $vars['primary_nav'] = isset($vars['main_menu']) ? theme('links', $vars['main_menu'], array('class' => 'links main-menu')) : FALSE;
  $vars['secondary_nav'] = isset($vars['secondary_menu']) ? theme('links', $vars['secondary_menu'], array('class' => 'links secondary-menu')) : FALSE;
  $vars['ie_styles'] = garland_get_ie_styles();

  // Prepare header
  $site_fields = array();
  if (!empty($vars['site_name'])) {
    $site_fields[] = check_plain($vars['site_name']);
  }
  if (!empty($vars['site_slogan'])) {
    $site_fields[] = check_plain($vars['site_slogan']);
  }
  $vars['site_title'] = implode(' ', $site_fields);
  if (!empty($site_fields)) {
    $site_fields[0] = '<span>'. $site_fields[0] .'</span>';
  }
  $vars['site_html'] = implode(' ', $site_fields);

  // Hook into color.module
  if (module_exists('color')) {
    _color_page_alter($vars);
  }
}

/**
 * Returns the rendered local tasks. The default implementation renders
 * them as tabs. Overridden to split the secondary tasks.
 */
function garland_menu_local_tasks() {
  return menu_primary_local_tasks();
}

/**
 * Format the "Submitted by username on date/time" for each comment.
 */
function phptemplate_comment_submitted($comment) {
  return t('!datetime — !username',
    array(
      '!username' => theme('username', $comment),
      '!datetime' => format_date($comment->timestamp)
    ));
}

/**
 * Format the "Submitted by username on date/time" for each node.
 */
function garland_node_submitted($node) {
  return t('!datetime — !username',
    array(
      '!username' => theme('username', $node),
      '!datetime' => format_date($node->created),
    ));
}

/**
 * Generates IE CSS links for LTR and RTL languages.
 */
function garland_get_ie_styles() {
  global $language;

  $ie_styles = '<link type="text/css" rel="stylesheet" media="all" href="' . base_path() . path_to_theme() . '/fix-ie.css" />'. "\n";
  if (defined('LANGUAGE_RTL') && $language->direction == LANGUAGE_RTL) {
    $ie_styles .= '      <style type="text/css" media="all">@import "' . base_path() . path_to_theme() . '/fix-ie-rtl.css";</style>'. "\n";
  }

  return $ie_styles;
}
