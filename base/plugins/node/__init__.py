#!/usr/bin/env python
# $Id: node.module,v 1.971 2008/08/03 19:02:06 dries Exp $

"""
  The core that allows content to be submitted to the site. Modules and
  scripts may programmatically submit nodes using the usual form API pattern.

  @package user
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's modules/node/node.module
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

from lib.drupy import DrupyPHP as php
from lib.drupy import DrupyImport
from includes import common as lib_common
from includes import path as lib_path
from includes import database as lib_database
from includes import bootstrap as lib_bootstrap
from includes import plugin as lib_plugin



#
# Nodes changed before this time are always marked as read.
#
# Nodes changed after this time may be marked new, updated, or read, depending
# on their state for the current user. Defaults to 30 days ago.
#
NODE_NEW_LIMIT = php.time_() - 30 * 24 * 60 * 60

#
# Node is being built before being viewed normally.
#
NODE_BUILD_NORMAL = 0

#
# Node is being built before being previewed.
#
NODE_BUILD_PREVIEW = 1

#
# Node is being built before being indexed by search module.
#
NODE_BUILD_SEARCH_INDEX = 2

#
# Node is being built before being displayed as a search result.
#
NODE_BUILD_SEARCH_RESULT = 3

#
# Node is being built before being displayed as part of an RSS feed.
#
NODE_BUILD_RSS = 4

#
# Node is being built before being printed.
#
NODE_BUILD_PRINT = 5

def hook_help(path, arg):
  """
   Implementation of hook_help().
  """
  # Remind site administrators about the {node_access} table being flagged
  # for rebuild. We don't need to issue the message on the confirm form, or
  # while the rebuild is being processed.
  if (path != 'admin/content/node-settings/rebuild' and \
      path != 'batch' and php.strpos(path, '#') == False
      and lib_plugin.plugins['user'].access(\
      'access administration pages') and access_needs_rebuild()):
    if (path == 'admin/content/node-settings'):
      message = lib_common.t(\
        'The content access permissions need to be rebuilt.')
    else:
      message = lib_common.t('The content access permissions need to ' + \
        'be rebuilt. Please visit ' + \
        '<a href="@node_access_rebuild">this page</a>.', \
        {'@node_access_rebuild' : \
        lib_common.url('admin/content/node-settings/rebuild')})
    lib_bootstrap.drupal_set_message(message, 'error')
  if path == 'admin/help#node':
    output = '<p>' +  t('The node module manages content on your ' + \
      'site, and stores all posts (regardless of type) as a ' + \
      '"node". In addition to basic publishing settings, including ' + \
      'whether the post has been published, promoted to the site ' + \
      'front page, or should remain present (or sticky) at the top ' + \
      'of lists, the node module also records basic information about ' + \
      'the author of a post. Optional revision control over edits is ' + \
      'available. For additional functionality, the node module is ' + \
      'often extended by other modules.') + '</p>'
    output += '<p>' +  t('Though each post on your site is a node, each ' + \
      'post is also of a particular ' + \
      '<a href="@content-type">content type</a>. ' + \
      '<a href="@content-type">Content types</a> are used to define the ' + \
      'characteristics of a post, including the title and description ' + \
      'of the fields displayed on its add and edit pages. Each ' + \
      'content type may have different default settings for ' + \
      '<em>Publishing options</em> and other workflow controls. ' + \
      'By default, the two content types in a standard Drupal ' + \
      'installation are <em>Page</em> and <em>Story</em>. Use the ' + \
      '<a href="@content-type">content types page</a> to add new or ' + \
      'edit existing content types. Additional content types also ' + \
      'become available as you enable additional core, contributed and ' + \
      'custom modules.', {'@content-type' : \
      lib_common.url('admin/build/types')}) + '</p>'
    output += '<p>' +  lib_common.t('The administrative ' + \
      '<a href="@content">content page</a> allows you to review and ' + \
      'manage your site content. The ' + \
      '<a href="@post-settings">post settings page</a> sets certain ' + \
      'options for the display of posts. The node module makes a ' + \
      'number of permissions available for each content type, which ' + \
      'may be set by role on the ' + \
      '<a href="@permissions">permissions page</a>.', \
      {'@content' : lib_common.url('admin/content/node'), \
      '@post-settings' : lib_common.url('admin/content/node-settings'), \
      '@permissions' : lib_common.url('admin/user/permissions')}) + '</p>'
    output += '<p>' +  t('For more information, see the online ' + \
      'handbook entry for <a href="@node">Node module</a>.', \
      {'@node' : 'http://drupal.org/handbook/modules/node/'})  + '</p>'
    return output
  elif path == 'admin/content/node':
    # Return a non-None value so that the 'more help' link is shown.
    return ' '
  elif path == 'admin/build/types':
    return '<p>' +  t('Below is a list of all the content types on your ' + \
      'site. All posts that exist on your site are instances of one ' + \
      'of these content types.') + '</p>'
  elif path == 'admin/build/types/add':
    return '<p>' +  t('To create a new content type, enter the ' + \
      'human-readable name, the machine-readable name, and all other ' + \
      'relevant fields that are on this page. Once created, users ' + \
      'of your site will be able to create posts that are ' + \
      'instances of this content type.') + '</p>'
  elif path == 'node/%/revisions':
    return '<p>' +  lib_common.t('The revisions let you track differences ' + \
      'between multiple versions of a post.')  + '</p>'
  elif path == 'node/%/edit':
    node = load(arg[1])
    type_ = get_types('type', node.type_)
    return (('<p>' +  filter_xss_admin(type.help)  + '</p>') if \
      (not php.empty(type_.help)) else '')
  if (arg[0] == 'node' and arg[1] == 'add' and arg[2]):
    type_ = get_types('type', php.str_replace('-', '_', arg[2]))
    return (('<p>' +  filter_xss_admin(type_.help)  + '</p>') if \
      (not empty(type_.help)) else '')




def hook_theme():
  """
   Implementation of hook_theme().
  """
  return {
    'node' : {
      'arguments' : {'node' : None, 'teaser' : False, 'page' : False},
      'template' : 'node'
    },
    'node_list' : {
      'arguments' : {'items' : None, 'title' : None}
    },
    'node_search_admin' : {
      'arguments' : {'form' : None}
    },
    'node_filter_form' : {
      'arguments' : {'form' : None},
      'file' : 'node.admin.inc'
    },
    'node_filters' : {
      'arguments' : {'form' : None},
      'file' : 'node.admin.inc'
    },
    'node_admin_nodes' : {
      'arguments' : {'form' : None},
      'file' : 'node.admin.inc'
    },
    'node_add_list' : {
      'arguments' : {'content' : None},
      'file' : 'node.pages.inc'
    },
    'node_form' : {
      'arguments' : {'form' : None},
      'file' : 'node.pages.inc'
    },
    'node_preview' : {
      'arguments' : {'node' : None},
      'file' : 'node.pages.inc'
    },
    'node_log_message' : {
      'arguments' : {'log' : None}
    },
    'node_submitted' : {
      'arguments' : {'node' : None}
    },
  }




def hook_cron():
  """
   Implementation of hook_cron().
  """
  lib_database.query('DELETE FROM {history} WHERE timestamp < %d', \
    NODE_NEW_LIMIT)


def title_list(result, title = None):
  """
   Gather a listing of links to nodes.
  
   @param result
     A DB result object from a query to fetch node objects. If your query
     joins the <code>node_comment_statistics</code> table so that the
     <code>comment_count</code> field is available, a title attribute will
     be added to show the number of comments.
   @param title
     A heading for the resulting list.
  
   @return
     An HTML list suitable as content for a block, or False if no result can
     fetch from DB result object.
  """
  items = []
  num_rows = False
  while True:
    node = db_fetch_object(result)
    if not node:
      break
    items.append(l((({'attributes' : {'title' : format_plural(\
      node.comment_count, '1 comment', '@count comments')}}) if \
      (node.title, 'node/' + node.nid, \
      not php.empty(node.comment_count)) else {})))
    num_rows = True
  return (lib_theme.theme('node_list', items, title) if num_rows else False)



def theme_list(items, title = None):
  """
   Format a listing of links to nodes.
  
   @ingroup themeable
  """
  return lib_theme.theme('item_list', items, title)


def tag_new(nid):
  """
   Update the 'last viewed' timestamp of the specified node for current user.
  """
  if (lib_appglobals.user.uid):
    if (last_viewed(nid)):
      lib_database.query('UPDATE {history} SET timestamp = %d ' + \
        'WHERE uid = %d AND nid = %d', php.time_(), \
        lib_appglobals.user.uid, nid)
    else:
      lib_database.query('INSERT INTO {history} (uid, nid, timestamp) ' + \
        'VALUES (%d, %d, %d)', lib_appglobals.user.uid, nid, php.time_())



def last_viewed(nid):
  """
   Retrieves the timestamp at which the current user last viewed the
   specified node.
  """
  php.static(last_view, 'history', {})
  if (not php.isset(last_view.history, 'nid')):
    last_view.history[nid] = lib_database.fetch_object(lib_database.query(\
      "SELECT timestamp FROM {history} " + \
      "WHERE uid = %d AND nid = %d", lib_appglobals.user.uid, nid))
  return (last_view.history[nid].timestamp if \
    php.isset(last_view.history[nid], 'timestamp') else 0)



def mark(nid, timestamp):
  """
   Decide on the type of marker to be displayed for a given node.
  
   @param nid
     Node ID whose history supplies the "last viewed" timestamp.
   @param timestamp
     Time which is compared against node's "last viewed" timestamp.
   @return
     One of the MARK constants.
  """
  php.static(mark, 'cache', {})
  if (not lib_appglobals.user.uid):
    return MARK_READ
  if (not php.isset(mark.cache, 'nid')):
    mark.cache[nid] = last_viewed(nid)
  if (mark.cache[nid] == 0 and timestamp > NODE_NEW_LIMIT):
    return MARK_NEW
  elif (timestamp > mark.cache[nid] and timestamp > NODE_NEW_LIMIT):
    return MARK_UPDATED
  return MARK_READ


def teaser_js(form, form_state):  
  """
   See if the user used JS to submit a teaser.
  """
  php.Reference.check(form)
  php.Reference.check(form_state)
  if (php.isset(form['#post'], 'teaser_js')):
    # Glue the teaser to the body.
    if (php.trim(form_state['values']['teaser_js'])):
      # Space the teaser from the body
      body = php.trim(form_state['values']['teaser_js']) + \
        "\r\n<not --break-.\r\n"  + php.trim(form_state['values']['body'])
    else:
      # Empty teaser, no spaces.
      body = '<not --break-.' +  form_state['values']['body']
    # Pass updated body value on to preview/submit form processing.
    form_set_value(form['body'], body, form_state)
    # Pass updated body value back onto form for those cases
    # in which the form is redisplayed.
    form['body']['#value'] = body
  return form



def teaser_include_verify(form, form_state):
  """
   Ensure value of "teaser_include" checkbox is consistent with other form data.
  
   This handles two situations in which an unchecked checkbox is rejected:
  
     1. The user defines a teaser (summary) but it is empty
     2. The user does not define a teaser (summary) (in this case an
        unchecked checkbox would cause the body to be empty, or missing
        the auto-generated teaser).
  
   If JavaScript is active then it is used to force the checkbox to be
   checked when hidden, and so the second case will not arise.
  
   In either case a warning message is output.
  """
  php.Reference.check(form)
  php.Reference.check(form_state)
  message = ''
  # form['#post'] is set only when the form is built for preview/submit.
  if (php.isset(form['#post']['body']) and \
      php.isset(form_state['values'], 'teaser_include') and \
      not form_state['values']['teaser_include']):
    # "teaser_include" checkbox is present and unchecked.
    if (php.strpos(form_state['values']['body'], '<!--break-.') == 0):
      # Teaser is empty string.
      message = lib_common.t(\
        'You specified that the summary should not be shown when this ' + \
        'post is displayed in full view. This setting is ignored ' + \
        'when the summary is empty.')
    elif (php.strpos(form_state['values']['body'], '<!--break-.') == False):
      # Teaser delimiter is not present in the body.
      message = lib_common.t('You specified that the summary should ' + \
        'not be shown when this post is displayed in full view. ' + \
        'This setting has been ignored since you have not defined a ' + \
        'summary for the post. (To define a summary, insert the ' + \
        'delimiter "&lt;not --break--&gt;" (without the quotes) in ' + \
        'the Body of the post to indicate the end of the summary and ' + \
        'the start of the main content.)')
    if (not php.empty(message)):
      drupal_set_message(message, 'warning')
      # Pass new checkbox value on to preview/submit form processing.
      form_set_value(form['teaser_include'], 1, form_state)
      # Pass new checkbox value back onto form for those cases
      # in which form is redisplayed.
      form['teaser_include']['#value'] = 1
  return form



def teaser(body, format = None, size = None):
  """
   Generate a teaser for a node body.
  
   If the end of the teaser is not indicated using the <!--break-. delimiter
   then we generate the teaser automatically, trying to end it at a sensible
   place such as the end of a paragraph, a line break, or the end of a
   sentence (in that order of preference).
  
   @param body
     The content for which a teaser will be generated.
   @param format
     The format of the content. If the content contains PHP code, we do not
     split it up to prevent parse errors. If the line break filter is present
     then we treat newlines embedded in body as line breaks.
   @param size
     The desired character length of the teaser. If omitted, the default
     value will be used. Ignored if the special delimiter is present
     in body.
   @return
     The generated teaser.
  """
  if (size is None):
    size = lib_bootstrap.variable_get('teaser_length', 600)
  # Find where the delimiter is in the body
  delimiter = php.strpos(body, '<!--break-.')
  # If the size is zero, and there is no delimiter,
  # the entire body is the teaser.
  if (size == 0 and delimiter == False):
    return body
  # If a valid delimiter has been specified, use it to chop off the teaser.
  if (delimiter is not False):
    return php.substr(body, 0, delimiter)
  # We check for the presence of the PHP evaluator filter in the current
  # format. If the body contains PHP code, we do not split it up to prevent
  # parse errors.
  if (format is not None):
    filters = filter_list_format(format)
    if (php.isset(filters['php/0']) and php.strpos(body, '<?') is not False):
      return body
  # If we have a short body, the entire body is the teaser.
  if (drupal_strlen(body) <= size):
    return body
  # If the delimiter has not been specified, try to split at paragraph or
  # sentence boundaries.
  # The teaser may not be longer than maximum length specified. Initial slice.
  teaser = truncate_utf8(body, size)
  # Store the actual length of the UTF8 string -- which might not be the same
  # as size.
  max_rpos = php.strlen(teaser)
  # How much to cut off the end of the teaser so that it doesn't end in the
  # middle of a paragraph, sentence, or word.
  # Initialize it to maximum in order to find the minimum.
  min_rpos = max_rpos
  # Store the reverse of the teaser.  We use strpos on the reversed needle and
  # haystack for speed and convenience.
  reversed = php.strrev(teaser)
  # Build an array of arrays of break points grouped by preference.
  break_points = array()
  # A paragraph near the end of sliced teaser is most preferable.
  break_points.append( {'</p>' : 0} )
  # If no complete paragraph then treat line breaks as paragraphs.
  line_breaks = {'<br />' : 6, '<br>' : 4}
  # Newline only indicates a line break if line break converter
  # filter is present.
  if (php.isset(filters['filter/1'])):
    line_breaks["\n"] = 1
  break_points.append( line_breaks )
  # If the first paragraph is too long, split at the end of a sentence.
  # @TODO DRUPY: Fix this somehow
  # There are additional characters at the end of this line
  break_points.append( {'. ' : 1, '!  ' : 1, '? ' : 1} )
  # Iterate over the groups of break points until a break point is found.
  for points in break_points:
    # Look for each break point, starting at the end of the teaser.
    for point,offset in points.items():
      # The teaser is already reversed, but the break point isn't.
      rpos = php.strpos(reversed, php.strrev(point))
      if (rpos is not False):
        min_rpos = php.min(rpos + offset, min_rpos)
    # If a break point was found in this group, slice and return the teaser.
    if (min_rpos != max_rpos):
      # Don't slice with length 0.  Length must be <0 to slice from RHS.
      return (teaser if (min_rpos == 0) else \
        php.substr(teaser, 0, 0 - min_rpos))
  # If a break point was not found, still return a teaser.
  return teaser




def get_types(op = 'types', node = None, reset = False):
  """
   Builds a list of available node types, and returns all of part of this list
   in the specified format.
  
   @param op
     The format in which to return the list. When this is set to 'type',
     'module', or 'name', only the specified node type is returned. When set to
     'types' or 'names', all node types are returned.
   @param node
     A node object, array, or string that indicates the node type to return.
     Leave at default value (None) to return a list of all node types.
   @param reset
     Whether or not to reset this function's internal cache (defaults to
     False).
  
   @return
     Either an array of all available node types, or a single node type, in a
     variable format. Returns False if the node type is not found.
  """
  php.static(get_types, '_node_types', {})
  php.static(get_types, '_get_types', {})
  if (reset or php.empty(get_types._node_types)):
    get_types._node_types, get_types._node_names = _types_build()
  if (node):
    if (php.is_array(node)):
      type_ = node['type']
    elif (php.is_object(node)):
      type_ = node.type_
    elif (php.is_string(node)):
      type_ = node
    if (not php.isset(get_types._node_types, 'type_')):
      return False
  if op == 'types':
    return _node_types
  elif op =='type':
    return (_node_types[type] if \
      php.isset(get_types._node_types, type_) else False)
  elif op == 'module':
    return (get_types._node_types[type_].plugin if \
      php.isset(get_types._node_types[type_], 'plugin') else False)
  elif op == 'names':
    return get_types._node_names
  elif op =='name':
    return (get_types._node_names[type_] if \
      php.isset(_node_names, type_) else False)



def types_rebuild():
  """
   Resets the database cache of node types, and saves all new or non-modified
   module-defined node types to the database.
  """
  _types_build()
  node_types = get_types('types', None, True)
  for type_,info in node_types.items():
    if (not empty(info.is_new)):
      type_save(info)
    if (not empty(info.disabled)):
      type_delete(info.type_)
  _types_build()



def type_save(info):
  """
   Saves a node type to the database.
  
   @param info
     The node type to save, as an object.
  
   @return
     Status flag indicating outcome of the operation.
  """
  is_existing = False
  existing_type = not empty(info.old_type) ? info.old_type : info.type
  is_existing = db_result(db_query("SELECT COUNT(*) FROM {node_type} WHERE type = '%s'", existing_type))
  if (not isset(info.help)):
    info.help = ''
  }
  if (not isset(info.min_word_count)):
    info.min_word_count = 0
  }
  if (not isset(info.body_label)):
    info.body_label = ''
  }

  if (is_existing):
    db_query("UPDATE {node_type} SET type = '%s', name = '%s', module = '%s', has_title = %d, title_label = '%s', has_body = %d, body_label = '%s', description = '%s', help = '%s', min_word_count = %d, custom = %d, modified = %d, locked = %d WHERE type = '%s'", info.type, info.name, info.module, info.has_title, info.title_label, info.has_body, info.body_label, info.description, info.help, info.min_word_count, info.custom, info.modified, info.locked, existing_type)
    module_invoke_all('node_type', 'update', info)
    return SAVED_UPDATED
  }
  else:
    db_query("INSERT INTO {node_type} (type, name, module, has_title, title_label, has_body, body_label, description, help, min_word_count, custom, modified, locked, orig_type) VALUES ('%s', '%s', '%s', %d, '%s', %d, '%s', '%s', '%s', %d, %d, %d, %d, '%s')", info.type, info.name, info.module, info.has_title, info.title_label, info.has_body, info.body_label, info.description, info.help, info.min_word_count, info.custom, info.modified, info.locked, info.orig_type)
    module_invoke_all('node_type', 'insert', info)
    return SAVED_NEW
  }
}
#
# Deletes a node type from the database.
#
# @param type
#   The machine-readable name of the node type to be deleted.
#
def node_type_delete(type):
  info = node_get_types('type', type)
  db_query("DELETE FROM {node_type} WHERE type = '%s'", type)
  module_invoke_all('node_type', 'delete', info)
}
#
# Updates all nodes of one type to be of another type.
#
# @param old_type
#   The current node type of the nodes.
# @param type
#   The new node type of the nodes.
#
# @return
#   The number of nodes whose node type field was modified.
#
def node_type_update_nodes(old_type, type):
  db_query("UPDATE {node} SET type = '%s' WHERE type = '%s'", type, old_type)
  return db_affected_rows()
}
#
# Builds and returns the list of available node types.
#
# The list of types is built by querying hook_node_info() in all modules, and
# by comparing this information with the node types in the {node_type} table.
#
#
def _node_types_build():
  _node_types = array()
  _node_names = array()
  info_array = module_invoke_all('node_info')
  for type,info in info_array.items():
    info['type'] = type
    _node_types[type] = (object) _node_type_set_defaults(info)
    _node_names[type] = info['name']
  }

  type_result = db_query(db_rewrite_sql('SELECT nt.type, nt.* FROM {node_type} nt ORDER BY nt.type ASC', 'nt', 'type'))
  while (type_object = db_fetch_object(type_result)):
    # Check for node types from disabled modules and mark their types for removal.
    # Types defined by the node module in the database (rather than by a separate
    # module using hook_node_info) have a module value of 'node'.
    if (type_object.module != 'node' and empty(info_array[type_object.type])):
      type_object.disabled = True
    }
    if (not isset(_node_types[type_object.type]) or type_object.modified):
      _node_types[type_object.type] = type_object
      _node_names[type_object.type] = type_object.name
      if (type_object.type != type_object.orig_type):
        unset(_node_types[type_object.orig_type])
        unset(_node_names[type_object.orig_type])
      }
    }
  }

  asort(_node_names)
  return array(_node_types, _node_names)
}
#
# Set default values for a node type defined through hook_node_info().
#
def _node_type_set_defaults(info):
  if (not isset(info['has_title'])):
    info['has_title'] = True
  }
  if (info['has_title'] and not isset(info['title_label'])):
    info['title_label'] = t('Title')
  }

  if (not isset(info['has_body'])):
    info['has_body'] = True
  }
  if (info['has_body'] and not isset(info['body_label'])):
    info['body_label'] = t('Body')
  }

  if (not isset(info['help'])):
    info['help'] = ''
  }
  if (not isset(info['min_word_count'])):
    info['min_word_count'] = 0
  }
  if (not isset(info['custom'])):
    info['custom'] = False
  }
  if (not isset(info['modified'])):
    info['modified'] = False
  }
  if (not isset(info['locked'])):
    info['locked'] = True
  }

  info['orig_type'] = info['type']
  info['is_new'] = True
  return info
}
#
# Determine whether a node hook exists.
#
# @param &node
#   Either a node object, node array, or a string containing the node type.
# @param hook
#   A string containing the name of the hook.
# @return
#   True iff the hook exists in the node type of node.
#
def node_hook(&node, hook):
  module = node_get_types('module', node)
  if (module == 'node'):
    # Avoid function name collisions.
    module = 'node_content'
  }
  return module_hook(module, hook)
}
#
# Invoke a node hook.
#
# @param &node
#   Either a node object, node array, or a string containing the node type.
# @param hook
#   A string containing the name of the hook.
# @param a2, a3, a4
#   Arguments to pass on to the hook, after the node argument.
# @return
#   The returned value of the invoked hook.
#
def node_invoke(&node, hook, a2 = None, a3 = None, a4 = None):
  if (node_hook(node, hook)):
    module = node_get_types('module', node)
    if (module == 'node'):
      module = 'node_content'; // Avoid function name collisions.
    }
    function = module +  '_'  + hook
    return (function(node, a2, a3, a4))
  }
}
#
# Invoke a hook_nodeapi() operation in all modules.
#
# @param &node
#   A node object.
# @param op
#   A string containing the name of the nodeapi operation.
# @param a3, a4
#   Arguments to pass on to the hook, after the node and op arguments.
# @return
#   The returned value of the invoked hooks.
#
def node_invoke_nodeapi(&node, op, a3 = None, a4 = None):
  return = array()
  foreach (module_implements('nodeapi') as name):
    function = name +  '_nodeapi'
    result = function(node, op, a3, a4)
    if (isset(result) and is_array(result)):
      return = array_merge(return, result)
    }
    elif (isset(result)):
      return[] = result
    }
  }
  return return
}
#
# Load a node object from the database.
#
# @param param
#   Either the nid of the node or an array of conditions to match against in the database query
# @param revision
#   Which numbered revision to load. Defaults to the current version.
# @param reset
#   Whether to reset the internal node_load cache.
#
# @return
#   A fully-populated node object.
#
def node_load(param = array(), revision = None, reset = None):
  static nodes = array()
  if (reset):
    nodes = array()
  }

  cachable = (revision == None)
  arguments = array()
  if (is_numeric(param)):
    if (cachable):
      # Is the node statically cached?
      if (isset(nodes[param])):
        return is_object(nodes[param]) ? clone nodes[param] : nodes[param]
      }
    }
    cond = 'n.nid = %d'
    arguments[] = param
  }
  elif (is_array(param)):
    # Turn the conditions into a query.
    for key,value in param.items():
      cond[] = 'n.' +  db_escape_table(key)  + " = '%s'"
      arguments[] = value
    }
    cond = implode(' AND ', cond)
  }
  else:
    return False
  }

  # Retrieve a field list based on the site's schema.
  fields = drupal_schema_fields_sql('node', 'n')
  fields = array_merge(fields, drupal_schema_fields_sql('node_revisions', 'r'))
  fields = array_merge(fields, array('u.name', 'u.picture', 'u.data'))
  # Remove fields not needed in the query: n.vid and r.nid are redundant,
  # n.title is unnecessary because the node title comes from the
  # node_revisions table.  We'll keep r.vid, r.title, and n.nid.
  fields = array_diff(fields, array('n.vid', 'n.title', 'r.nid'))
  fields = implode(', ', fields)
  # Rename timestamp field for clarity.
  fields = str_replace('r.timestamp', 'r.timestamp AS revision_timestamp', fields)
  # Change name of revision uid so it doesn't conflict with n.uid.
  fields = str_replace('r.uid', 'r.uid AS revision_uid', fields)
  # Retrieve the node.
  # No db_rewrite_sql is applied so as to get complete indexing for search.
  if (revision):
    array_unshift(arguments, revision)
    node = db_fetch_object(db_query('SELECT ' +  fields  + ' FROM {node} n INNER JOIN {users} u ON u.uid = n.uid INNER JOIN {node_revisions} r ON r.nid = n.nid AND r.vid = %d WHERE ' . cond, arguments))
  }
  else:
    node = db_fetch_object(db_query('SELECT ' +  fields  + ' FROM {node} n INNER JOIN {users} u ON u.uid = n.uid INNER JOIN {node_revisions} r ON r.vid = n.vid WHERE ' . cond, arguments))
  }

  if (node and node.nid):
    # Call the node specific callback (if any) and piggy-back the
    # results to the node or overwrite some values.
    if (extra = node_invoke(node, 'load')):
      for key,value in extra.items():
        node.$key = value
      }
    }

    if (extra = node_invoke_nodeapi(node, 'load')):
      for key,value in extra.items():
        node.$key = value
      }
    }
    if (cachable):
      nodes[node.nid] = is_object(node) ? clone node : node
    }
  }

  return node
}
#
# Perform validation checks on the given node.
#
def node_validate(node, form = array()):
  # Convert the node to an object, if necessary.
  node = (object)node
  type = node_get_types('type', node)
  # Make sure the body has the minimum number of words.
  # TODO : use a better word counting algorithm that will work in other languages
  if (not empty(type.min_word_count) and isset(node.body) and count(explode(' ', node.body)) < type.min_word_count):
    form_set_error('body', t('The body of your @type is too short + You need at least %words words.', array('%words' : type.min_word_count, '@type' : type.name)))
  }

  if (isset(node.nid) and (node_last_changed(node.nid) > node.changed)):
    form_set_error('changed', t('This content has been modified by another user, changes cannot be saved.'))
  }

  if (user_access('administer nodes')):
    # Validate the "authored by" field.
    if (not empty(node.name) and not (account = user_load(array('name' : node.name)))):
      # The use of empty() is mandatory in the context of usernames
      # as the empty string denotes the anonymous user. In case we
      # are dealing with an anonymous user we set the user ID to 0.
      form_set_error('name', t('The username %name does not exist.', array('%name' : node.name)))
    }

    # Validate the "authored on" field. As of PHP 5.1.0, strtotime returns False instead of -1 upon failure.
    if (not empty(node.date) and strtotime(node.date) <= 0):
      form_set_error('date', t('You have to specify a valid date.'))
    }
  }

  # Do node-type-specific validation checks.
  node_invoke(node, 'validate', form)
  node_invoke_nodeapi(node, 'validate', form)
}
#
# Prepare node for save and allow modules to make changes.
#
def node_submit(node):
  global user
  # Convert the node to an object, if necessary.
  node = (object)node
  # Generate the teaser, but only if it hasn't been set (e.g. by a
  # module-provided 'teaser' form item).
  if (not isset(node.teaser)):
    if (isset(node.body)):
      node.teaser = node_teaser(node.body, isset(node.format) ? node.format : None)
      # Chop off the teaser from the body if needed. The teaser_include
      # property might not be set (eg. in Blog API postings), so only act on
      # it, if it was set with a given value.
      if (isset(node.teaser_include) and not node.teaser_include and node.teaser == substr(node.body, 0, strlen(node.teaser))):
        node.body = substr(node.body, strlen(node.teaser))
      }
    }
    else:
      node.teaser = ''
    }
  }

  if (user_access('administer nodes')):
    # Populate the "authored by" field.
    if (account = user_load(array('name' : node.name))):
      node.uid = account.uid
    }
    else:
      node.uid = 0
    }
  }
  node.created = not empty(node.date) ? strtotime(node.date) : time()
  node.validated = True
  return node
}
#
# Save a node object into the database.
#
def node_save(&node):
  # Let modules modify the node before it is saved to the database.
  node_invoke_nodeapi(node, 'presave')
  global user
  node.is_new = False
  # Apply filters to some default node fields:
  if (empty(node.nid)):
    # Insert a new node.
    node.is_new = True
    # When inserting a node, node.log must be set because
    # {node_revisions}.log does not (and cannot) have a default
    # value.  If the user does not have permission to create
    # revisions, however, the form will not contain an element for
    # log so node.log will be unset at this point.
    if (not isset(node.log)):
      node.log = ''
    }

    # For the same reasons, make sure we have node.teaser and
    # node.body.  We should consider making these fields Noneable
    # in a future version since node types are not required to use them.
    if (not isset(node.teaser)):
      node.teaser = ''
    }
    if (not isset(node.body)):
      node.body = ''
    }
  }
  elif (not empty(node.revision)):
    node.old_vid = node.vid
  }
  else:
    # When updating a node, avoid clobberring an existing log entry with an empty one.
    if (empty(node.log)):
      unset(node.log)
    }
  }

  # Set some required fields:
  if (empty(node.created)):
    node.created = time()
  }
  # The changed timestamp is always updated for bookkeeping purposes (revisions, searching, ...)
  node.changed = time()
  node.timestamp = time()
  node.format = isset(node.format) ? node.format : FILTER_FORMAT_DEFAULT
  update_node = True
  # Generate the node table query and the node_revisions table query.
  if (node.is_new):
    drupal_write_record('node', node)
    _node_save_revision(node, user.uid)
    op = 'insert'
  }
  else:
    drupal_write_record('node', node, 'nid')
    if (not empty(node.revision)):
      _node_save_revision(node, user.uid)
    }
    else:
      _node_save_revision(node, user.uid, 'vid')
      update_node = False
    }
    op = 'update'
  }
  if (update_node):
    db_query('UPDATE {node} SET vid = %d WHERE nid = %d', node.vid, node.nid)
  }

  # Call the node specific callback (if any). This can be
  # node_invoke(node, 'insert') or
  # node_invoke(node, 'update').
  node_invoke(node, op)
  node_invoke_nodeapi(node, op)
  # Update the node access table for this node.
  node_access_acquire_grants(node)
  # Clear the page and block caches.
  cache_clear_all()
}
#
# Helper function to save a revision with the uid of the current user.
#
# Node is taken by reference, becuse drupal_write_record() updates the
# node with the revision id, and we need to pass that back to the caller.
#
def _node_save_revision(&node, uid, update = None):
  temp_uid = node.uid
  node.uid = uid
  if (isset(update)):
    drupal_write_record('node_revisions', node, update)
  }
  else:
    drupal_write_record('node_revisions', node)
  }
  node.uid = temp_uid
}
#
# Delete a node.
#
def node_delete(nid):

  node = node_load(nid)
  if (node_access('delete', node)):
    db_query('DELETE FROM {node} WHERE nid = %d', node.nid)
    db_query('DELETE FROM {node_revisions} WHERE nid = %d', node.nid)
    # Call the node-specific callback (if any):
    node_invoke(node, 'delete')
    node_invoke_nodeapi(node, 'delete')
    # Clear the page and block caches.
    cache_clear_all()
    # Remove this node from the search index if needed.
    # This code is implemented in node module rather than in search module,
    # because node module is implementing search module's API, not the other
    # way around.
    if (module_exists('search')):
      search_wipe(node.nid, 'node')
    }
    watchdog('content', '@type: deleted %title.', array('@type' : node.type, '%title' : node.title))
    drupal_set_message(t('@type %title has been deleted.', array('@type' : node_get_types('name', node), '%title' : node.title)))
  }
}
#
# Generate a display of the given node.
#
# @param node
#   A node array or node object.
# @param teaser
#   Whether to display the teaser only or the full form.
# @param page
#   Whether the node is being displayed by itself as a page.
# @param links
#   Whether or not to display node links. Links are omitted for node previews.
#
# @return
#   An HTML representation of the themed node.
#
def node_view(node, teaser = False, page = False, links = True):
  node = (object)node
  node = node_build_content(node, teaser, page)
  if (links):
    node.links = module_invoke_all('link', 'node', node, teaser)
    drupal_alter('link', node.links, node)
  }

  # Set the proper node part, then unset unused node part so that a bad
  # theme can not open a security hole.
  content = drupal_render(node.content)
  if (teaser):
    node.teaser = content
    unset(node.body)
  }
  else:
    node.body = content
    unset(node.teaser)
  }

  # Allow modules to modify the fully-built node.
  node_invoke_nodeapi(node, 'alter', teaser, page)
  return theme('node', node, teaser, page)
}
#
# Apply filters and build the node's standard elements.
#
def node_prepare(node, teaser = False):
  # First we'll overwrite the existing node teaser and body with
  # the filtered copiesnot  Then, we'll stick those into the content
  # array and set the read more flag if appropriate.
  node.readmore = (strlen(node.teaser) < strlen(node.body))
  if (teaser == False):
    node.body = check_markup(node.body, node.format, False)
  }
  else:
    node.teaser = check_markup(node.teaser, node.format, False)
  }

  node.content['body'] = array(
    '#markup' : teaser ? node.teaser : node.body,
    '#weight' : 0,
  )
  return node
}
#
# Builds a structured array representing the node's content.
#
# @param node
#   A node object.
# @param teaser
#   Whether to display the teaser only, as on the main page.
# @param page
#   Whether the node is being displayed by itself as a page.
#
# @return
#   An structured array containing the individual elements
#   of the node's body.
#
def node_build_content(node, teaser = False, page = False):

  # The build mode identifies the target for which the node is built.
  if (not isset(node.build_mode)):
    node.build_mode = NODE_BUILD_NORMAL
  }

  # Remove the delimiter (if any) that separates the teaser from the body.
  node.body = isset(node.body) ? str_replace('<not --break-.', '', node.body) : ''
  # The 'view' hook can be implemented to overwrite the default function
  # to display nodes.
  if (node_hook(node, 'view')):
    node = node_invoke(node, 'view', teaser, page)
  }
  else:
    node = node_prepare(node, teaser)
  }

  # Allow modules to make their own additions to the node.
  node_invoke_nodeapi(node, 'view', teaser, page)
  return node
}
#
# Generate a page displaying a single node, along with its comments.
#
def node_show(node, cid, message = False):
  if (message):
    drupal_set_title(t('Revision of %title from %date', array('%title' : node.title, '%date' : format_date(node.revision_timestamp))))
  }
  output = node_view(node, False, True)
  if (function_exists('comment_render') and node.comment):
    output += comment_render(node, cid)
  }

  # Update the history table, stating that this user viewed this node.
  node_tag_new(node.nid)
  return output
}
#
# Theme a log message.
#
# @ingroup themeable
#
def theme_node_log_message(log):
  return '<div class="log"><div class="title">' +  t('Log')  + ':</div>' . log . '</div>'
}
#
# Implementation of hook_perm().
#
def node_perm():
  perms = array(
    'administer content types' : t('Manage content types and content type administration settings.'),
    'administer nodes' : t('Manage all website content, and bypass any content-related access control + %warning', array('%warning' : t('Warning: Give to trusted roles only; this permission has security implications.'))),
    'access content' : t('View published content.'),
    'view revisions' : t('View content revisions.'),
    'revert revisions' : t('Replace content with an older revision.'),
    'delete revisions' : t('Delete content revisions.'),
  )
  for type in node_get_types():
    if (type.module == 'node'):
      perms += node_list_permissions(type)
    }
  }

  return perms
}
#
# Gather the rankings from the the hook_ranking implementations.
#
def _node_rankings():
  rankings = array(
    'total' : 0, 'join' : array(), 'score' : array(), 'args' : array(),
  )
  if (ranking = module_invoke_all('ranking')):
    for rank,values in ranking.items():
      if (node_rank = variable_get('node_rank_' + rank, 0)):
        # If the table defined in the ranking isn't already joined, then add it.
        if (isset(values['join']) and not isset(rankings['join'][values['join']])):
          rankings['join'][values['join']] = values['join']
        }

        # Add the rankings weighted score multiplier value, handling None gracefully.
        rankings['score'][] = '%f * COALESCE((' + values['score'] + '), 0)'
        # Add the the administrator's weighted score multiplier value for this ranking.
        rankings['total'] += node_rank
        rankings['arguments'][] = node_rank
        # Add any additional arguments used by this ranking.
        if (isset(values['arguments'])):
          rankings['arguments'] = array_merge(rankings['arguments'], values['arguments'])
        }
      }
    }
  }
  return rankings
}
#
# Implementation of hook_search().
#
def node_search(op = 'search', keys = None):
  switch (op):
    case 'name':
      return t('Content')
    case 'reset':
      db_query("UPDATE {search_dataset} SET reindex = %d WHERE type = 'node'", time())
      return
    case 'status':
      total = db_result(db_query('SELECT COUNT(*) FROM {node} WHERE status = 1'))
      remaining = db_result(db_query("SELECT COUNT(*) FROM {node} n LEFT JOIN {search_dataset} d ON d.type = 'node' AND d.sid = n.nid WHERE n.status = 1 AND d.sid IS None OR d.reindex <> 0"))
      return array('remaining' : remaining, 'total' : total)
    case 'admin':
      form = array()
      # Output form for defining rank factor weights.
      form['content_ranking'] = array(
        '#type' : 'fieldset',
        '#title' : t('Content ranking'),
      )
      form['content_ranking']['#theme'] = 'node_search_admin'
      form['content_ranking']['info'] = array(
        '#value' : '<em>' . t('The following numbers control which properties the content search should favor when ordering the results. Higher numbers mean more influence, zero means the property is ignored. Changing these numbers does not require the search index to be rebuilt. Changes take effect immediately.') . '</em>'
      )
      # Note: reversed to reflect that higher number = higher ranking.
      options = drupal_map_assoc(range(0, 10))
      foreach (module_invoke_all('ranking') as var : values):
        form['content_ranking']['factors']['node_rank_' + var] = array(
          '#title' : values['title'],
          '#type' : 'select',
          '#options' : options,
          '#default_value' : variable_get('node_rank_'. var, 0),
        )
      }
      return form
    case 'search':
      # Build matching conditions
      list(join1, where1) = _db_rewrite_sql()
      arguments1 = array()
      conditions1 = 'n.status = 1'
      if (type = search_query_extract(keys, 'type')):
        types = array()
        foreach (explode(',', type) as t):
          types[] = "n.type = '%s'"
          arguments1[] = t
        }
        conditions1 += ' AND (' +  implode(' OR ', types)  + ')'
        keys = search_query_insert(keys, 'type')
      }

      if (category = search_query_extract(keys, 'category')):
        categories = array()
        foreach (explode(',', category) as c):
          categories[] = "tn.tid = %d"
          arguments1[] = c
        }
        conditions1 += ' AND (' +  implode(' OR ', categories)  + ')'
        join1 += ' INNER JOIN {term_node} tn ON n.vid = tn.vid'
        keys = search_query_insert(keys, 'category')
      }

      if (languages = search_query_extract(keys, 'language')):
        categories = array()
        foreach (explode(',', languages) as l):
          categories[] = "n.language = '%s'"
          arguments1[] = l
        }
        conditions1 += ' AND (' +  implode(' OR ', categories)  + ')'
        keys = search_query_insert(keys, 'language')
      }

      # Get the ranking expressions.
      rankings = _node_rankings()
      # When all search factors are disabled (ie they have a weight of zero),
      # The default score is based only on keyword relevance.
      if (rankings['total'] == 0):
        total = 1
        arguments2 = array()
        join2 = ''
        select2 = 'i.relevance AS score'
      }
      else:
        total = rankings['total']
        arguments2 = rankings['arguments']
        join2 = implode(' ', rankings['join'])
        select2 = '(' + implode(' + ', rankings['score']) + ') AS score'
      }

      # Do search.
      find = do_search(keys, 'node', 'INNER JOIN {node} n ON n.nid = i.sid ' +  join1, conditions1  + (empty(where1) ? '' : ' AND ' . where1), arguments1, select2, join2, arguments2)
      # Load results.
      results = array()
      for item in find:
        # Build the node body.
        node = node_load(item.sid)
        node.build_mode = NODE_BUILD_SEARCH_RESULT
        node = node_build_content(node, False, False)
        node.body = drupal_render(node.content)
        # Fetch comments for snippet.
        node.body += module_invoke('comment', 'nodeapi', node, 'update index')
        # Fetch terms for snippet.
        node.body += module_invoke('taxonomy', 'nodeapi', node, 'update index')
        extra = node_invoke_nodeapi(node, 'search result')
        results[] = array(
          'link' : url('node/' +  item.sid, array('absolute' : True)),
          'type' : check_plain(node_get_types('name', node)),
          'title' : node.title,
          'user' : theme('username', node),
          'date' : node.changed,
          'node' : node,
          'extra' : extra,
          'score' : total ? (item.score / total) : 0,
          'snippet' : search_excerpt(keys, node.body),
        )
      }
      return results
  }
}
#
# Implementation of hook_ranking().
#
def node_ranking():
  # Create the ranking array and add the basic ranking options.
  ranking = array(
    'relevance' : array(
      'title' : t('Keyword relevance'),
      # Average relevance values hover around 0.15
      'score' : 'i.relevance',
    ),
    'sticky' : array(
      'title' : t('Content is sticky at top of lists'),
      # The sticky flag is either 0 or 1, which is automatically normalized.
      'score' : 'n.sticky',
    ),
    'promote' : array(
      'title' : t('Content is promoted to the front page'),
      # The promote flag is either 0 or 1, which is automatically normalized.
      'score' : 'n.promote',
    ),
  )
  # Add relevance based on creation or changed date.
  if (node_cron_last = variable_get('node_cron_last', 0)):
    ranking['recent'] = array(
      'title' : t('Recently posted'),
      # Exponential decay with half-life of 6 months, starting at last indexed node
      'score' : '(POW(2, GREATEST(n.created, n.changed) - %d) * 6.43e-8)',
      'arguments' : array(node_cron_last),
    )
  }
  return ranking
}
#
# Implementation of hook_user().
#
def node_user(op, &edit, &user):
  if (op == 'delete'):
    db_query('UPDATE {node} SET uid = 0 WHERE uid = %d', user.uid)
    db_query('UPDATE {node_revisions} SET uid = 0 WHERE uid = %d', user.uid)
  }
}
#
# Theme the content ranking part of the search settings admin page.
#
# @ingroup themeable
#
def theme_node_search_admin(form):
  output = drupal_render(form['info'])
  header = array(t('Factor'), t('Weight'))
  foreach (element_children(form['factors']) as key):
    row = array()
    row[] = form['factors'][key]['#title']
    unset(form['factors'][key]['#title'])
    row[] = drupal_render(form['factors'][key])
    rows[] = row
  }
  output += theme('table', header, rows)
  output += drupal_render(form)
  return output
}
#
# Retrieve the comment mode for the given node ID (none, read, or read/write).
#
def node_comment_mode(nid):
  static comment_mode
  if (not isset(comment_mode[nid])):
    comment_mode[nid] = db_result(db_query('SELECT comment FROM {node} WHERE nid = %d', nid))
  }
  return comment_mode[nid]
}
#
# Implementation of hook_link().
#
def node_link(type, node = None, teaser = False):
  links = array()
  if (type == 'node'):
    if (teaser == 1 and node.teaser and not empty(node.readmore)):
      links['node_read_more'] = array(
        'title' : t('Read more'),
        'href' : "node/node.nid",
        # The title attribute gets escaped when the links are processed, so
        # there is no need to escape here.
        'attributes' : array('title' : t('Read the rest of not title.', array('not title' : node.title)))
      )
    }
  }

  return links
}

def _node_revision_access(node, op = 'view'):
  static access = array()
  if (not isset(access[node.vid])):
    node_current_revision = node_load(node.nid)
    is_current_revision = node_current_revision.vid == node.vid
    # There should be at least two revisions. If the vid of the given node
    # and the vid of the current revision differs, then we already have two
    # different revisions so there is no need for a separate database check.
    # Also, if you try to revert to or delete the current revision, that's
    # not good.
    if (is_current_revision and (db_result(db_query('SELECT COUNT(vid) FROM {node_revisions} WHERE nid = %d', node.nid)) == 1 or op == 'update' or op == 'delete')):
      access[node.vid] = False
    }
    elif (user_access('administer nodes')):
      access[node.vid] = True
    }
    else:
      map = array('view' : 'view revisions', 'update' : 'revert revisions', 'delete' : 'delete revisions')
      # First check the user permission, second check the access to the
      # current revision and finally, if the node passed in is not the current
      # revision then access to that, too.
      access[node.vid] = isset(map[op]) and user_access(map[op]) and node_access(op, node_current_revision) and (is_current_revision or node_access(op, node))
    }
  }
  return access[node.vid]
}

def _node_add_access():
  types = node_get_types()
  for type in types:
    if (node_hook(type.type, 'form') and node_access('create', type.type)):
      return True
    }
  }
  return False
}
#
# Implementation of hook_menu().
#
def node_menu():
  items['admin/content/node'] = array(
    'title' : 'Content',
    'description' : "View, edit, and delete your site's content.",
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_admin_content'),
    'access arguments' : array('administer nodes'),
  )
  items['admin/content/node/overview'] = array(
    'title' : 'List',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -10,
  )
  items['admin/content/node-settings'] = array(
    'title' : 'Post settings',
    'description' : 'Control posting behavior, such as teaser length, requiring previews before posting, and the number of posts on the front page.',
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_configure'),
    'access arguments' : array('administer nodes'),
  )
  items['admin/content/node-settings/rebuild'] = array(
    'title' : 'Rebuild permissions',
    'page arguments' : array('node_configure_rebuild_confirm'),
    # Any user than can potentially trigger a node_acess_needs_rebuild(True)
    # has to be allowed access to the 'node access rebuild' confirm form.
    'access arguments' : array('access administration pages'),
    'type' : MENU_CALLBACK,
  )
  items['admin/build/types'] = array(
    'title' : 'Content types',
    'description' : 'Manage posts by content type, including default status, front page promotion, etc.',
    'page callback' : 'node_overview_types',
    'access arguments' : array('administer content types'),
  )
  items['admin/build/types/list'] = array(
    'title' : 'List',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -10,
  )
  items['admin/build/types/add'] = array(
    'title' : 'Add content type',
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_type_form'),
    'access arguments' : array('administer content types'),
    'type' : MENU_LOCAL_TASK,
  )
  items['node'] = array(
    'title' : 'Content',
    'page callback' : 'node_page_default',
    'access arguments' : array('access content'),
    'type' : MENU_CALLBACK,
  )
  items['node/add'] = array(
    'title' : 'Create content',
    'page callback' : 'node_add_page',
    'access callback' : '_node_add_access',
    'weight' : 1,
  )
  items['rss.xml'] = array(
    'title' : 'RSS feed',
    'page callback' : 'node_feed',
    'access arguments' : array('access content'),
    'type' : MENU_CALLBACK,
  )
  foreach (node_get_types('types', None, True) as type):
    type_url_str = str_replace('_', '-', type.type)
    items['node/add/' +  type_url_str] = array(
      'title' : drupal_ucfirst(type.name),
      'title callback' : 'check_plain',
      'page callback' : 'node_add',
      'page arguments' : array(2),
      'access callback' : 'node_access',
      'access arguments' : array('create', type.type),
      'description' : type.description,
    )
    items['admin/build/node-type/' +  type_url_str] = array(
      'title' : type.name,
      'page callback' : 'drupal_get_form',
      'page arguments' : array('node_type_form', type),
      'access arguments' : array('administer content types'),
      'type' : MENU_CALLBACK,
    )
    items['admin/build/node-type/' +  type_url_str  + '/edit'] = array(
      'title' : 'Edit',
      'type' : MENU_DEFAULT_LOCAL_TASK,
    )
    items['admin/build/node-type/' +  type_url_str  + '/delete'] = array(
      'title' : 'Delete',
      'page arguments' : array('node_type_delete_confirm', type),
      'access arguments' : array('administer content types'),
      'type' : MENU_CALLBACK,
    )
  }
  items['node/%node'] = array(
    'title callback' : 'node_page_title',
    'title arguments' : array(1),
    'page callback' : 'node_page_view',
    'page arguments' : array(1),
    'access callback' : 'node_access',
    'access arguments' : array('view', 1),
    'type' : MENU_CALLBACK)
  items['node/%node/view'] = array(
    'title' : 'View',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -10)
  items['node/%node/edit'] = array(
    'title' : 'Edit',
    'page callback' : 'node_page_edit',
    'page arguments' : array(1),
    'access callback' : 'node_access',
    'access arguments' : array('update', 1),
    'weight' : 1,
    'type' : MENU_LOCAL_TASK,
  )
  items['node/%node/delete'] = array(
    'title' : 'Delete',
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_delete_confirm', 1),
    'access callback' : 'node_access',
    'access arguments' : array('delete', 1),
    'weight' : 1,
    'type' : MENU_CALLBACK)
  items['node/%node/revisions'] = array(
    'title' : 'Revisions',
    'page callback' : 'node_revision_overview',
    'page arguments' : array(1),
    'access callback' : '_node_revision_access',
    'access arguments' : array(1),
    'weight' : 2,
    'type' : MENU_LOCAL_TASK,
  )
  items['node/%node/revisions/%/view'] = array(
    'title' : 'Revisions',
    'load arguments' : array(3),
    'page callback' : 'node_show',
    'page arguments' : array(1, None, True),
    'access callback' : '_node_revision_access',
    'access arguments' : array(1),
    'type' : MENU_CALLBACK,
  )
  items['node/%node/revisions/%/revert'] = array(
    'title' : 'Revert to earlier revision',
    'load arguments' : array(3),
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_revision_revert_confirm', 1),
    'access callback' : '_node_revision_access',
    'access arguments' : array(1, 'update'),
    'type' : MENU_CALLBACK,
  )
  items['node/%node/revisions/%/delete'] = array(
    'title' : 'Delete earlier revision',
    'load arguments' : array(3),
    'page callback' : 'drupal_get_form',
    'page arguments' : array('node_revision_delete_confirm', 1),
    'access callback' : '_node_revision_access',
    'access arguments' : array(1, 'delete'),
    'type' : MENU_CALLBACK,
  )
  return items
}
#
# Title callback.
#
def node_page_title(node):
  return node.title
}
#
# Implementation of hook_init().
#
def node_init():
  drupal_add_css(drupal_get_path('module', 'node') +  '/node.css')
}

def node_last_changed(nid):
  node = db_fetch_object(db_query('SELECT changed FROM {node} WHERE nid = %d', nid))
  return (node.changed)
}
#
# Return a list of all the existing revision numbers.
#
def node_revision_list(node):
  revisions = array()
  result = db_query('SELECT r.vid, r.title, r.log, r.uid, n.vid AS current_vid, r.timestamp, u.name FROM {node_revisions} r LEFT JOIN {node} n ON n.vid = r.vid INNER JOIN {users} u ON u.uid = r.uid WHERE r.nid = %d ORDER BY r.timestamp DESC', node.nid)
  while (revision = db_fetch_object(result)):
    revisions[revision.vid] = revision
  }

  return revisions
}
#
# Implementation of hook_block().
#
def node_block(op = 'list', delta = ''):
  if (op == 'list'):
    blocks['syndicate']['info'] = t('Syndicate')
    # Not worth caching.
    blocks['syndicate']['cache'] = BLOCK_NO_CACHE
    return blocks
  }
  elif (op == 'view'):
    block['subject'] = t('Syndicate')
    block['content'] = theme('feed_icon', url('rss.xml'), t('Syndicate'))
    return block
  }
}
#
# A generic function for generating RSS feeds from a set of nodes.
#
# @param nids
#   An array of node IDs (nid). Defaults to False so empty feeds can be
#   generated with passing an empty array, if no items are to be added
#   to the feed.
# @param channel
#   An associative array containing title, link, description and other keys.
#   The link should be an absolute URL.
#
def node_feed(nids = False, channel = array()):
  global base_url, language
  if (nids == False):
    nids = array()
    result = db_query_range(db_rewrite_sql('SELECT n.nid, n.created FROM {node} n WHERE n.promote = 1 AND n.status = 1 ORDER BY n.created DESC'), 0, variable_get('feed_default_items', 10))
    while (row = db_fetch_object(result)):
      nids[] = row.nid
    }
  }

  item_length = variable_get('feed_item_length', 'teaser')
  namespaces = array('xmlns:dc' : 'http://purl.org/dc/elements/1.1/')
  items = ''
  for nid in nids:
    # Load the specified node:
    item = node_load(nid)
    item.build_mode = NODE_BUILD_RSS
    item.link = url("node/nid", array('absolute' : True))
    if (item_length != 'title'):
      teaser = (item_length == 'teaser') ? True : False
      # Filter and prepare node teaser
      if (node_hook(item, 'view')):
        item = node_invoke(item, 'view', teaser, False)
      }
      else:
        item = node_prepare(item, teaser)
      }

      # Allow modules to change node.teaser before viewing.
      node_invoke_nodeapi(item, 'view', teaser, False)
    }

    # Allow modules to add additional item fields and/or modify item
    extra = node_invoke_nodeapi(item, 'rss item')
    extra = array_merge(extra, array(array('key' : 'pubDate', 'value' : gmdate('r', item.created)), array('key' : 'dc:creator', 'value' : item.name), array('key' : 'guid', 'value' : item.nid +  ' at '  + base_url, 'attributes' : array('isPermaLink' : 'False'))))
    for element in extra:
      if (isset(element['namespace'])):
        namespaces = array_merge(namespaces, element['namespace'])
      }
    }

    # Prepare the item description
    switch (item_length):
      case 'fulltext':
        item_text = item.body
        break
      case 'teaser':
        item_text = item.teaser
        if (not empty(item.readmore)):
          item_text += '<p>' +  l(t('read more'), 'node/'  + item.nid, array('absolute' : True, 'attributes' : array('target' : '_blank'))) . '</p>'
        }
        break
      case 'title':
        item_text = ''
        break
    }

    items += format_rss_item(item.title, item.link, item_text, extra)
  }

  channel_defaults = array(
    'version'     : '2.0',
    'title'       : variable_get('site_name', 'Drupal'),
    'link'        : base_url,
    'description' : variable_get('site_mission', ''),
    'language'    : language.language
  )
  channel = array_merge(channel_defaults, channel)
  output = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
  output += "<rss version=\"" +  channel["version"]  + "\" xml:base=\"" . base_url . "\" " . drupal_attributes(namespaces) . ">\n"
  output += format_rss_channel(channel['title'], channel['link'], channel['description'], items, channel['language'])
  output += "</rss>\n"
  drupal_set_header('Content-Type: application/rss+xml; charset=utf-8')
  print output
}
#
# Menu callback; Generate a listing of promoted nodes.
#
def node_page_default():
  result = pager_query(db_rewrite_sql('SELECT n.nid, n.sticky, n.created FROM {node} n WHERE n.promote = 1 AND n.status = 1 ORDER BY n.sticky DESC, n.created DESC'), variable_get('default_nodes_main', 10))
  output = ''
  num_rows = False
  while (node = db_fetch_object(result)):
    output += node_view(node_load(node.nid), 1)
    num_rows = True
  }

  if (num_rows):
    feed_url = url('rss.xml', array('absolute' : True))
    drupal_add_feed(feed_url, variable_get('site_name', 'Drupal') +  ' '  + t('RSS'))
    output += theme('pager', None, variable_get('default_nodes_main', 10))
  }
  else:
    default_message = '<h1 class="title">' +  t('Welcome to your new Drupal websitenot ')  + '</h1>'
    default_message += '<p>' +  t('Please follow these steps to set up and start using your website:')  + '</p>'
    default_message += '<ol>'
    default_message += '<li>' +  t('<strong>Configure your website</strong> Once logged in, visit the <a href="@admin">administration section</a>, where you can <a href="@config">customize and configure</a> all aspects of your website.', array('@admin' : url('admin'), '@config' : url('admin/settings')))  + '</li>'
    default_message += '<li>' +  t('<strong>Enable additional functionality</strong> Next, visit the <a href="@modules">module list</a> and enable features which suit your specific needs + You can find additional modules in the <a href="@download_modules">Drupal modules download section</a>.', array('@modules' : url('admin/build/modules'), '@download_modules' : 'http://drupal.org/project/modules')) . '</li>'
    default_message += '<li>' +  t('<strong>Customize your website design</strong> To change the "look and feel" of your website, visit the <a href="@themes">themes section</a> + You may choose from one of the included themes or download additional themes from the <a href="@download_themes">Drupal themes download section</a>.', array('@themes' : url('admin/build/themes'), '@download_themes' : 'http://drupal.org/project/themes')) . '</li>'
    default_message += '<li>' +  t('<strong>Start posting content</strong> Finally, you can <a href="@content">create content</a> for your website + This message will disappear once you have promoted a post to the front page.', array('@content' : url('node/add'))) . '</li>'
    default_message += '</ol>'
    default_message += '<p>' +  t('For more information, please refer to the <a href="@help">help section</a>, or the <a href="@handbook">online Drupal handbooks</a> + You may also post at the <a href="@forum">Drupal forum</a>, or view the wide range of <a href="@support">other support options</a> available.', array('@help' : url('admin/help'), '@handbook' : 'http://drupal.org/handbooks', '@forum' : 'http://drupal.org/forum', '@support' : 'http://drupal.org/support')) . '</p>'
    output = '<div id="first-time">' +  default_message  + '</div>'
  }
  drupal_set_title('')
  return output
}
#
# Menu callback; view a single node.
#
def node_page_view(node, cid = None):
  drupal_set_title(check_plain(node.title))
  return node_show(node, cid)
}
#
# Implementation of hook_update_index().
#
def node_update_index():
  limit = (int)variable_get('search_cron_limit', 100)
  # Store the maximum possible comments per thread (used for ranking by reply count)
  variable_set('node_cron_comments_scale', 1.0 / max(1, db_result(db_query('SELECT MAX(comment_count) FROM {node_comment_statistics}'))))
  variable_set('node_cron_views_scale', 1.0 / max(1, db_result(db_query('SELECT MAX(totalcount) FROM {node_counter}'))))
  result = db_query_range("SELECT n.nid FROM {node} n LEFT JOIN {search_dataset} d ON d.type = 'node' AND d.sid = n.nid WHERE d.sid IS None OR d.reindex <> 0 ORDER BY d.reindex ASC, n.nid ASC", 0, limit)
  while (node = db_fetch_object(result)):
    _node_index_node(node)
  }
}
#
# Index a single node.
#
# @param node
#   The node to index.
#
def _node_index_node(node):
  node = node_load(node.nid)
  # save the changed time of the most recent indexed node, for the search results half-life calculation
  variable_set('node_cron_last', node.changed)
  # Build the node body.
  node.build_mode = NODE_BUILD_SEARCH_INDEX
  node = node_build_content(node, False, False)
  node.body = drupal_render(node.content)
  text = '<h1>' +  check_plain(node.title)  + '</h1>' . node.body
  # Fetch extra data normally not visible
  extra = node_invoke_nodeapi(node, 'update index')
  for t in extra:
    text += t
  }

  # Update index
  search_index(node.nid, 'node', text)
}
#
# Implementation of hook_form_alter().
#
def node_form_alter(&form, form_state, form_id):
  # Advanced node search form
  if (form_id == 'search_form' and form['module']['#value'] == 'node' and user_access('use advanced search')):
    # Keyword boxes:
    form['advanced'] = array(
      '#type' : 'fieldset',
      '#title' : t('Advanced search'),
      '#collapsible' : True,
      '#collapsed' : True,
      '#attributes' : array('class' : 'search-advanced'),
    )
    form['advanced']['keywords'] = array(
      '#prefix' : '<div class="criterion">',
      '#suffix' : '</div>',
    )
    form['advanced']['keywords']['or'] = array(
      '#type' : 'textfield',
      '#title' : t('Containing any of the words'),
      '#size' : 30,
      '#maxlength' : 255,
    )
    form['advanced']['keywords']['phrase'] = array(
      '#type' : 'textfield',
      '#title' : t('Containing the phrase'),
      '#size' : 30,
      '#maxlength' : 255,
    )
    form['advanced']['keywords']['negative'] = array(
      '#type' : 'textfield',
      '#title' : t('Containing none of the words'),
      '#size' : 30,
      '#maxlength' : 255,
    )
    # Taxonomy box:
    if (taxonomy = module_invoke('taxonomy', 'form_all', 1)):
      form['advanced']['category'] = array(
        '#type' : 'select',
        '#title' : t('Only in the category(s)'),
        '#prefix' : '<div class="criterion">',
        '#size' : 10,
        '#suffix' : '</div>',
        '#options' : taxonomy,
        '#multiple' : True,
      )
    }

    # Node types:
    types = array_map('check_plain', node_get_types('names'))
    form['advanced']['type'] = array(
      '#type' : 'checkboxes',
      '#title' : t('Only of the type(s)'),
      '#prefix' : '<div class="criterion">',
      '#suffix' : '</div>',
      '#options' : types,
    )
    form['advanced']['submit'] = array(
      '#type' : 'submit',
      '#value' : t('Advanced search'),
      '#prefix' : '<div class="action">',
      '#suffix' : '</div>',
    )
    # Languages:
    language_options = array()
    foreach (language_list('language') as key : object):
      language_options[key] = object.name
    }
    if (count(language_options) > 1):
      form['advanced']['language'] = array(
        '#type' : 'checkboxes',
        '#title' : t('Languages'),
        '#prefix' : '<div class="criterion">',
        '#suffix' : '</div>',
        '#options' : language_options,
      )
    }


    form['#validate'][] = 'node_search_validate'
  }
}
#
# Form API callback for the search form. Registered in node_form_alter().
#
def node_search_validate(form, &form_state):
  # Initialise using any existing basic search keywords.
  keys = form_state['values']['processed_keys']
  # Insert extra restrictions into the search keywords string.
  if (isset(form_state['values']['type']) and is_array(form_state['values']['type'])):
    # Retrieve selected types - Forms API sets the value of unselected checkboxes to 0.
    form_state['values']['type'] = array_filter(form_state['values']['type'])
    if (count(form_state['values']['type'])):
      keys = search_query_insert(keys, 'type', implode(',', array_keys(form_state['values']['type'])))
    }
  }

  if (isset(form_state['values']['category']) and is_array(form_state['values']['category'])):
    keys = search_query_insert(keys, 'category', implode(',', form_state['values']['category']))
  }
  if (isset(form_state['values']['language']) and is_array(form_state['values']['language'])):
    keys = search_query_insert(keys, 'language', implode(',', array_filter(form_state['values']['language'])))
  }
  if (form_state['values']['or'] != ''):
    if (preg_match_all('/ ("[^"]+"|[^" ]+)/i', ' ' +  form_state['values']['or'], matches)):
      keys += ' ' +  implode(' OR ', matches[1])
    }
  }
  if (form_state['values']['negative'] != ''):
    if (preg_match_all('/ ("[^"]+"|[^" ]+)/i', ' ' +  form_state['values']['negative'], matches)):
      keys += ' -' +  implode(' -', matches[1])
    }
  }
  if (form_state['values']['phrase'] != ''):
    keys += ' "' +  str_replace('"', ' ', form_state['values']['phrase'])  + '"'
  }
  if (not empty(keys)):
    form_set_value(form['basic']['inline']['processed_keys'], trim(keys), form_state)
  }
}
#
# @defgroup node_access Node access rights
# @{
# The node access system determines who can do what to which nodes.
#
# In determining access rights for a node, node_access() first checks
# whether the user has the "administer nodes" permission. Such users have
# unrestricted access to all nodes. Then the node module's hook_access()
# is called, and a True or False return value will grant or deny access.
# This allows, for example, the blog module to always grant access to the
# blog author, and for the book module to always deny editing access to
# PHP pages.
#
# If node module does not intervene (returns None), then the
# node_access table is used to determine access. All node access
# modules are queried using hook_node_grants() to assemble a list of
# "grant IDs" for the user. This list is compared against the table.
# If any row contains the node ID in question (or 0, which stands for "all
# nodes"), one of the grant IDs returned, and a value of True for the
# operation in question, then access is granted. Note that this table is a
# list of grants; any matching row is sufficient to grant access to the
# node.
#
# In node listings, the process above is followed except that
# hook_access() is not called on each node for performance reasons and for
# proper functioning of the pager system. When adding a node listing to your
# module, be sure to use db_rewrite_sql() to add
# the appropriate clauses to your query for access checks.
#
# To see how to write a node access module of your own, see
# node_access_example.module.
#
#
# Determine whether the current user may perform the given operation on the
# specified node.
#
# @param op
#   The operation to be performed on the node. Possible values are:
#   - "view"
#   - "update"
#   - "delete"
#   - "create"
# @param node
#   The node object (or node array) on which the operation is to be performed,
#   or node type (e.g. 'forum') for "create" operation.
# @param account
#   Optional, a user object representing the user for whom the operation is to
#   be performed. Determines access for a user other than the current user.
# @return
#   True if the operation may be performed.
#
def node_access(op, node, account = None):
  global user
  if (not node):
    return False
  }
  # Convert the node to an object if necessary:
  if (op != 'create'):
    node = (object)node
  }
  # If no user object is supplied, the access check is for the current user.
  if (empty(account)):
    account = user
  }
  # If the node is in a restricted format, disallow editing.
  if (op == 'update' and not filter_access(node.format)):
    return False
  }

  if (user_access('administer nodes', account)):
    return True
  }

  if (not user_access('access content', account)):
    return False
  }

  # Can't use node_invoke('access', node), because the access hook takes the
  # op parameter before the node parameter.
  module = node_get_types('module', node)
  if (module == 'node'):
    module = 'node_content'; // Avoid function name collisions.
  }
  access = module_invoke(module, 'access', op, node, account)
  if (not is_None(access)):
    return access
  }

  # If the module did not override the access rights, use those set in the
  # node_access table.
  if (op != 'create' and node.nid and node.status):
    grants = array()
    foreach (node_access_grants(op, account) as realm : gids):
      for gid in gids:
        grants[] = "(gid = gid AND realm = 'realm')"
      }
    }

    grants_sql = ''
    if (count(grants)):
      grants_sql = 'AND (' +  implode(' OR ', grants)  + ')'
    }

    sql = "SELECT COUNT(*) FROM {node_access} WHERE (nid = 0 OR nid = %d) grants_sql AND grant_op >= 1"
    result = db_query(sql, node.nid)
    return (db_result(result))
  }

  # Let authors view their own nodes.
  if (op == 'view' and account.uid == node.uid and account.uid != 0):
    return True
  }

  return False
}
#
# Generate an SQL join clause for use in fetching a node listing.
#
# @param node_alias
#   If the node table has been given an SQL alias other than the default
#   "n", that must be passed here.
# @param node_access_alias
#   If the node_access table has been given an SQL alias other than the default
#   "na", that must be passed here.
# @return
#   An SQL join clause.
#
def _node_access_join_sql(node_alias = 'n', node_access_alias = 'na'):
  if (user_access('administer nodes')):
    return ''
  }

  return 'INNER JOIN {node_access} ' +  node_access_alias  + ' ON ' . node_access_alias . '.nid = ' . node_alias . '.nid'
}
#
# Generate an SQL where clause for use in fetching a node listing.
#
# @param op
#   The operation that must be allowed to return a node.
# @param node_access_alias
#   If the node_access table has been given an SQL alias other than the default
#   "na", that must be passed here.
# @param account
#   The user object for the user performing the operation. If omitted, the
#   current user is used.
# @return
#   An SQL where clause.
#
def _node_access_where_sql(op = 'view', node_access_alias = 'na', account = None):
  if (user_access('administer nodes')):
    return
  }

  grants = array()
  foreach (node_access_grants(op, account) as realm : gids):
    for gid in gids:
      grants[] = "(node_access_alias.gid = gid AND node_access_alias.realm = 'realm')"
    }
  }

  grants_sql = ''
  if (count(grants)):
    grants_sql = 'AND (' +  implode(' OR ', grants)  + ')'
  }

  sql = "node_access_alias.grant_op >= 1 grants_sql"
  return sql
}
#
# Fetch an array of permission IDs granted to the given user ID.
#
# The implementation here provides only the universal "all" grant. A node
# access module should implement hook_node_grants() to provide a grant
# list for the user.
#
# @param op
#   The operation that the user is trying to perform.
# @param account
#   The user object for the user performing the operation. If omitted, the
#   current user is used.
# @return
#   An associative array in which the keys are realms, and the values are
#   arrays of grants for those realms.
#
def node_access_grants(op, account = None):

  if (not isset(account)):
    account = GLOBALS['user']
  }

  return array_merge(array('all' : array(0)), module_invoke_all('node_grants', account, op))
}
#
# Determine whether the user has a global viewing grant for all nodes.
#
def node_access_view_all_nodes():
  static access
  if (not isset(access)):
    grants = array()
    foreach (node_access_grants('view') as realm : gids):
      for gid in gids:
        grants[] = "(gid = gid AND realm = 'realm')"
      }
    }

    grants_sql = ''
    if (count(grants)):
      grants_sql = 'AND (' +  implode(' OR ', grants)  + ')'
    }

    sql = "SELECT COUNT(*) FROM {node_access} WHERE nid = 0 grants_sql AND grant_view >= 1"
    result = db_query(sql)
    access = db_result(result)
  }

  return access
}
#
# Implementation of hook_db_rewrite_sql().
#
def node_db_rewrite_sql(query, primary_table, primary_field):
  if (primary_field == 'nid' and not node_access_view_all_nodes()):
    return['join'] = _node_access_join_sql(primary_table)
    return['where'] = _node_access_where_sql()
    return['distinct'] = 1
    return return
  }
}
#
# This function will call module invoke to get a list of grants and then
# write them to the database. It is called at node save, and should be
# called by modules whenever something other than a node_save causes
# the permissions on a node to change.
#
# This function is the only function that should write to the node_access
# table.
#
# @param node
#   The node to acquire grants for.
#
def node_access_acquire_grants(node):
  grants = module_invoke_all('node_access_records', node)
  if (empty(grants)):
    grants[] = array('realm' : 'all', 'gid' : 0, 'grant_view' : 1, 'grant_update' : 0, 'grant_delete' : 0)
  }
  else:
    # retain grants by highest priority
    grant_by_priority = array()
    for g in grants:
      grant_by_priority[intval(g['priority'])][] = g
    }
    krsort(grant_by_priority)
    grants = array_shift(grant_by_priority)
  }

  node_access_write_grants(node, grants)
}
#
# This function will write a list of grants to the database, deleting
# any pre-existing grants. If a realm is provided, it will only
# delete grants from that realm, but it will always delete a grant
# from the 'all' realm. Modules which utilize node_access can
# use this function when doing mass updates due to widespread permission
# changes.
#
# @param node
#   The node being written to. All that is necessary is that it contain a nid.
# @param grants
#   A list of grants to write. Each grant is an array that must contain the
#   following keys: realm, gid, grant_view, grant_update, grant_delete.
#   The realm is specified by a particular module; the gid is as well, and
#   is a module-defined id to define grant privileges. each grant_* field
#   is a boolean value.
# @param realm
#   If provided, only read/write grants for that realm.
# @param delete
#   If False, do not delete records. This is only for optimization purposes,
#   and assumes the caller has already performed a mass delete of some form.
#
def node_access_write_grants(node, grants, realm = None, delete = True):
  if (delete):
    query = 'DELETE FROM {node_access} WHERE nid = %d'
    if (realm):
      query += " AND realm in ('%s', 'all')"
    }
    db_query(query, node.nid, realm)
  }

  # Only perform work when node_access modules are active.
  if (count(module_implements('node_grants'))):
    for grant in grants:
      if (realm and realm != grant['realm']):
        continue
      }
      # Only write grants; denies are implicit.
      if (grant['grant_view'] or grant['grant_update'] or grant['grant_delete']):
        db_query("INSERT INTO {node_access} (nid, realm, gid, grant_view, grant_update, grant_delete) VALUES (%d, '%s', %d, %d, %d, %d)", node.nid, grant['realm'], grant['gid'], grant['grant_view'], grant['grant_update'], grant['grant_delete'])
      }
    }
  }
}
#
# Flag / unflag the node access grants for rebuilding, or read the current
# value of the flag.
#
# When the flag is set, a message is displayed to users with 'access
# administration pages' permission, pointing to the 'rebuild' confirm form.
# This can be used as an alternative to direct node_access_rebuild calls,
# allowing administrators to decide when they want to perform the actual
# (possibly time consuming) rebuild.
# When unsure the current user is an adminisrator, node_access_rebuild
# should be used instead.
#
# @param rebuild
#   (Optional) The boolean value to be written.
# @return
#   (If no value was provided for rebuild) The current value of the flag.
#
def node_access_needs_rebuild(rebuild = None):
  if (not isset(rebuild)):
    return variable_get('node_access_needs_rebuild', False)
  }
  elif (rebuild):
    variable_set('node_access_needs_rebuild', True)
  }
  else:
    variable_del('node_access_needs_rebuild')
  }
}
#
# Rebuild the node access database. This is occasionally needed by modules
# that make system-wide changes to access levels.
#
# When the rebuild is required by an admin-triggered action (e.g module
# settings form), calling node_access_needs_rebuild(True) instead of
# node_access_rebuild() lets the user perform his changes and actually
# rebuild only once he is done.
#
# Note : As of Drupal 6, node access modules are not required to (and actually
# should not) call node_access_rebuild() in hook_enable/disable anymore.
#
# @see node_access_needs_rebuild()
#
# @param batch_mode
#   Set to True to process in 'batch' mode, spawning processing over several
#   HTTP requests (thus avoiding the risk of PHP timeout if the site has a
#   large number of nodes).
#   hook_update_N and any form submit handler are safe contexts to use the
#   'batch mode'. Less decidable cases (such as calls from hook_user,
#   hook_taxonomy, hook_node_type...) might consider using the non-batch mode.
#
def node_access_rebuild(batch_mode = False):
  db_query("DELETE FROM {node_access}")
  # Only recalculate if the site is using a node_access module.
  if (count(module_implements('node_grants'))):
    if (batch_mode):
      batch = array(
        'title' : t('Rebuilding content access permissions'),
        'operations' : array(
          array('_node_access_rebuild_batch_operation', array()),
        ),
        'finished' : '_node_access_rebuild_batch_finished'
      )
      batch_set(batch)
    }
    else:
      # If not in 'safe mode', increase the maximum execution time.
      if (not ini_get('safe_mode')):
        set_time_limit(240)
      }
      result = db_query("SELECT nid FROM {node}")
      while (node = db_fetch_object(result)):
        loaded_node = node_load(node.nid, None, True)
        # To preserve database integrity, only aquire grants if the node
        # loads successfully.
        if (not empty(loaded_node)):
          node_access_acquire_grants(loaded_node)
        }
      }
    }
  }
  else:
    # Not using any node_access modules. Add the default grant.
    db_query("INSERT INTO {node_access} VALUES (0, 0, 'all', 1, 0, 0)")
  }

  if (not isset(batch)):
    drupal_set_message(t('Content permissions have been rebuilt.'))
    node_access_needs_rebuild(False)
    cache_clear_all()
  }
}
#
# Batch operation for node_access_rebuild_batch.
#
# This is a mutlistep operation : we go through all nodes by packs of 20.
# The batch processing engine interrupts processing and sends progress
# feedback after 1 second execution time.
#
def _node_access_rebuild_batch_operation(&context):
  if (empty(context['sandbox'])):
    # Initiate multistep processing.
    context['sandbox']['progress'] = 0
    context['sandbox']['current_node'] = 0
    context['sandbox']['max'] = db_result(db_query('SELECT COUNT(DISTINCT nid) FROM {node}'))
  }

  # Process the next 20 nodes.
  limit = 20
  result = db_query_range("SELECT nid FROM {node} WHERE nid > %d ORDER BY nid ASC", context['sandbox']['current_node'], 0, limit)
  while (row = db_fetch_array(result)):
    loaded_node = node_load(row['nid'], None, True)
    # To preserve database integrity, only aquire grants if the node
    # loads successfully.
    if (not empty(loaded_node)):
      node_access_acquire_grants(loaded_node)
    }
    context['sandbox']['progress']++
    context['sandbox']['current_node'] = loaded_node.nid
  }

  # Multistep processing : report progress.
  if (context['sandbox']['progress'] != context['sandbox']['max']):
    context['finished'] = context['sandbox']['progress'] / context['sandbox']['max']
  }
}
#
# Post-processing for node_access_rebuild_batch.
#
def _node_access_rebuild_batch_finished(success, results, operations):
  if (success):
    drupal_set_message(t('The content access permissions have been rebuilt.'))
    node_access_needs_rebuild(False)
  }
  else:
    drupal_set_message(t('The content access permissions have not been properly rebuilt.'), 'error')
  }
  cache_clear_all()
}
#
# @} End of "defgroup node_access".
#
#
# @defgroup node_content Hook implementations for user-created content types.
# @{
#
#
# Implementation of hook_access().
#
# Named so as not to conflict with node_access()
#
def node_content_access(op, node, account):
  type = is_string(node) ? node : (is_array(node) ? node['type'] : node.type)
  if (op == 'create'):
    return user_access('create ' +  type  + ' content', account)
  }

  if (op == 'update'):
    if (user_access('edit any ' +  type  + ' content', account) or (user_access('edit own ' . type . ' content', account) and (account.uid == node.uid))):
      return True
    }
  }

  if (op == 'delete'):
    if (user_access('delete any ' +  type  + ' content', account) or (user_access('delete own ' . type . ' content', account) and (account.uid == node.uid))):
      return True
    }
  }
}
#
# Implementation of hook_form().
#
def node_content_form(node, form_state):
  type = node_get_types('type', node)
  form = array()
  if (type.has_title):
    form['title'] = array(
      '#type' : 'textfield',
      '#title' : check_plain(type.title_label),
      '#required' : True,
      '#default_value' : node.title,
      '#maxlength' : 255,
      '#weight' : -5,
    )
  }

  if (type.has_body):
    form['body_field'] = node_body_field(node, type.body_label, type.min_word_count)
  }

  return form
}
#
# @} End of "defgroup node_content".
#
#
# Implementation of hook_forms(). All node forms share the same form handler
#
def node_forms():
  forms = array()
  if (types = node_get_types()):
    for type in array_keys(types):
      forms[type +  '_node_form']['callback'] = 'node_form'
    }
  }
  return forms
}
#
# Format the "Submitted by username on date/time" for each node
#
# @ingroup themeable
#
def theme_node_submitted(node):
  return t('Submitted by not username on @datetime',
    array(
      'not username' : theme('username', node),
      '@datetime' : format_date(node.created),
    ))
}
#
# Implementation of hook_hook_info().
#
def node_hook_info():
  return array(
    'node' : array(
      'nodeapi' : array(
        'presave' : array(
          'runs when' : t('When either saving a new post or updating an existing post'),
        ),
        'insert' : array(
          'runs when' : t('After saving a new post'),
        ),
        'update' : array(
          'runs when' : t('After saving an updated post'),
        ),
        'delete' : array(
          'runs when' : t('After deleting a post')
        ),
        'view' : array(
          'runs when' : t('When content is viewed by an authenticated user')
        ),
      ),
    ),
  )
}
#
# Implementation of hook_action_info().
#
def node_action_info():
  return array(
    'node_publish_action' : array(
      'type' : 'node',
      'description' : t('Publish post'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('insert', 'update'),
      ),
    ),
    'node_unpublish_action' : array(
      'type' : 'node',
      'description' : t('Unpublish post'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('delete', 'insert', 'update'),
      ),
    ),
    'node_make_sticky_action' : array(
      'type' : 'node',
      'description' : t('Make post sticky'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('insert', 'update'),
      ),
    ),
    'node_make_unsticky_action' : array(
      'type' : 'node',
      'description' : t('Make post unsticky'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('delete', 'insert', 'update'),
      ),
    ),
    'node_promote_action' : array(
      'type' : 'node',
      'description' : t('Promote post to front page'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('insert', 'update'),
      ),
    ),
    'node_unpromote_action' : array(
      'type' : 'node',
      'description' : t('Remove post from front page'),
      'configurable' : False,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'nodeapi' : array('presave'),
        'comment' : array('delete', 'insert', 'update'),
      ),
    ),
    'node_assign_owner_action' : array(
      'type' : 'node',
      'description' : t('Change the author of a post'),
      'configurable' : True,
      'behavior' : array('changes_node_property'),
      'hooks' : array(
        'any' : True,
        'nodeapi' : array('presave'),
        'comment' : array('delete', 'insert', 'update'),
      ),
    ),
    'node_save_action' : array(
      'type' : 'node',
      'description' : t('Save post'),
      'configurable' : False,
      'hooks' : array(
        'comment' : array('delete', 'insert', 'update'),
      ),
    ),
    'node_unpublish_by_keyword_action' : array(
      'type' : 'node',
      'description' : t('Unpublish post containing keyword(s)'),
      'configurable' : True,
      'hooks' : array(
        'nodeapi' : array('presave', 'insert', 'update'),
      ),
    ),
  )
}
#
# Implementation of a Drupal action.
# Sets the status of a node to 1, meaning published.
#
def node_publish_action(&node, context = array()):
  node.status = 1
  watchdog('action', 'Set @type %title to published.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Sets the status of a node to 0, meaning unpublished.
#
def node_unpublish_action(&node, context = array()):
  node.status = 0
  watchdog('action', 'Set @type %title to unpublished.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Sets the sticky-at-top-of-list property of a node to 1.
#
def node_make_sticky_action(&node, context = array()):
  node.sticky = 1
  watchdog('action', 'Set @type %title to sticky.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Sets the sticky-at-top-of-list property of a node to 0.
#
def node_make_unsticky_action(&node, context = array()):
  node.sticky = 0
  watchdog('action', 'Set @type %title to unsticky.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Sets the promote property of a node to 1.
#
def node_promote_action(&node, context = array()):
  node.promote = 1
  watchdog('action', 'Promoted @type %title to front page.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Sets the promote property of a node to 0.
#
def node_unpromote_action(&node, context = array()):
  node.promote = 0
  watchdog('action', 'Removed @type %title from front page.', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a Drupal action.
# Saves a node.
#
def node_save_action(node):
  node_save(node)
  watchdog('action', 'Saved @type %title', array('@type' : node_get_types('name', node), '%title' : node.title))
}
#
# Implementation of a configurable Drupal action.
# Assigns ownership of a node to a user.
#
def node_assign_owner_action(&node, context):
  node.uid = context['owner_uid']
  owner_name = db_result(db_query("SELECT name FROM {users} WHERE uid = %d", context['owner_uid']))
  watchdog('action', 'Changed owner of @type %title to uid %name.', array('@type' : node_get_types('type', node), '%title' : node.title, '%name' : owner_name))
}

def node_assign_owner_action_form(context):
  description = t('The username of the user to which you would like to assign ownership.')
  count = db_result(db_query("SELECT COUNT(*) FROM {users}"))
  owner_name = ''
  if (isset(context['owner_uid'])):
    owner_name = db_result(db_query("SELECT name FROM {users} WHERE uid = %d", context['owner_uid']))
  }

  # Use dropdown for fewer than 200 users; textbox for more than that.
  if (intval(count) < 200):
    options = array()
    result = db_query("SELECT uid, name FROM {users} WHERE uid > 0 ORDER BY name")
    while (data = db_fetch_object(result)):
      options[data.name] = data.name
    }
    form['owner_name'] = array(
      '#type' : 'select',
      '#title' : t('Username'),
      '#default_value' : owner_name,
      '#options' : options,
      '#description' : description,
    )
  }
  else:
    form['owner_name'] = array(
      '#type' : 'textfield',
      '#title' : t('Username'),
      '#default_value' : owner_name,
      '#autocomplete_path' : 'user/autocomplete',
      '#size' : '6',
      '#maxlength' : '7',
      '#description' : description,
    )
  }
  return form
}

def node_assign_owner_action_validate(form, form_state):
  count = db_result(db_query("SELECT COUNT(*) FROM {users} WHERE name = '%s'", form_state['values']['owner_name']))
  if (intval(count) != 1):
    form_set_error('owner_name', t('Please enter a valid username.'))
  }
}

def node_assign_owner_action_submit(form, form_state):
  # Username can change, so we need to store the ID, not the username.
  uid = db_result(db_query("SELECT uid from {users} WHERE name = '%s'", form_state['values']['owner_name']))
  return array('owner_uid' : uid)
}

def node_unpublish_by_keyword_action_form(context):
  form['keywords'] = array(
    '#title' : t('Keywords'),
    '#type' : 'textarea',
    '#description' : t('The post will be unpublished if it contains any of the character sequences above. Use a comma-separated list of character sequences. Example: funny, bungee jumping, "Company, Inc." . Character sequences are case-sensitive.'),
    '#default_value' : isset(context['keywords']) ? drupal_implode_tags(context['keywords']) : '',
  )
  return form
}

def node_unpublish_by_keyword_action_submit(form, form_state):
  return array('keywords' : drupal_explode_tags(form_state['values']['keywords']))
}
#
# Implementation of a configurable Drupal action.
# Unpublish a node if it contains a certain string.
#
# @param context
#   An array providing more information about the context of the call to this action.
# @param comment
#   A node object.
#
def node_unpublish_by_keyword_action(node, context):
  foreach (context['keywords'] as keyword):
    if (strstr(node_view(clone node), keyword) or strstr(node.title, keyword)):
      node.status = 0
      watchdog('action', 'Set @type %title to unpublished.', array('@type' : node_get_types('name', node), '%title' : node.title))
      break
    }
  }
}
#
# Helper function to generate standard node permission list for a given type.
#
# @param type
#   The machine-readable name of the node type.
# @return array
#   An array of permission names and descriptions.
#
def node_list_permissions(type):
  info = node_get_types('type', type)
  type = check_plain(info.type)
  # Build standard list of node permissions for this type.
  perms["create type content"] = t('Create new %type_name content.', array('%type_name' : info.name))
  perms["delete any type content"] = t('Delete any %type_name content, regardless of its author.', array('%type_name' : info.name))
  perms["delete own type content"] = t('Delete %type_name content created by the user.', array('%type_name' : info.name))
  perms["edit own type content"] = t('Edit %type_name content created by the user.', array('%type_name' : info.name))
  perms["edit any type content"] = t('Edit any %type_name content, regardless of its author.', array('%type_name' : info.name))
  return perms
}
