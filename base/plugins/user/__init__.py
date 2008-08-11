#!/usr/bin/env python
# Id: user.module,v 1.911 2008/06/27 07:25:11 dries Exp $

"""
  Enables the user registration and login system.

  @package user
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's modules/user/user.module
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
#import password as lib_password

#
# Maximum length of username text field.
#
USERNAME_MAX_LENGTH = 60

#
# Maximum length of user e-mail text field.
#
EMAIL_MAX_LENGTH = 64


def module_invoke(type_, array_, user_, category = None):
  """
   Invokes hook_user() in every module.
  
   We cannot use module_invoke() for this, because the arguments need to
   be passed by reference.
  """
  php.Reference.check(array_)
  php.Reference.check(user_)
  for plugin_ in lib_plugin.list():
    function = 'hook_user'
    if (php.function_exists(function, lib_plugin.plugins[plugin_])):
      func = DrupyImport.getFunction(lib_plugin.plugins[plugin_], function)
      php.call_user_func(function, type_, array_, user_, category)




#
# Implementation of hook_theme().
#
def hook_theme():
  return {
    'user_picture' : {
      'arguments' : {'account' : None},
      'template' : 'user-picture'
    },
    'user_profile' : {
      'arguments' : {'account' : None},
      'template' : 'user-profile',
      'file' : 'user.pages.inc'
    },
    'user_profile_category' : {
      'arguments' : {'element' : None},
      'template' : 'user-profile-category',
      'file' : 'user.pages.inc'
    },
    'user_profile_item' : {
      'arguments' : {'element' : None},
      'template' : 'user-profile-item',
      'file' : 'user.pages.inc'
    },
    'user_list' : {
      'arguments' : {'users' : None, 'title' : None}
    },
    'user_admin_perm' : {
      'arguments' : {'form' : None},
      'file' : 'user.admin.inc'
    },
    'user_admin_new_role' : {
      'arguments' : {'form' : None},
      'file' : 'user.admin.inc'
    },
    'user_admin_account' : {
      'arguments' : {'form' : None},
      'file' : 'user.admin.inc'
    },
    'user_filter_form' : {
      'arguments' : {'form' : None},
      'file' : 'user.admin.inc'
    },
    'user_filters' : {
      'arguments' : {'form' : None},
      'file' : 'user.admin.inc'
    },
    'user_signature' : {
      'arguments' : {'signature' : None},
    },
  }




def external_load(authname):
  result = lib_database.query(\
    "SELECT uid FROM {authmap} WHERE authname = '%s'", authname)
  this_user = lib_database.fetch_array(result)
  if (this_user):
    return lib_plugin.plugins['user'].load(this_user)
  else:
    return False



def external_login(account, edit=[]):
  """
   Perform standard Drupal login operations for a user object.
  
   The user object must already be authenticated. This function verifies
   that the user account is not blocked and then performs the login,
   updates the login timestamp in the database, invokes hook_user('login'),
   and regenerates the session.
  
   @param account
      An authenticated user object to be set as the currently logged
      in user.
   @param edit
      The array of form values submitted by the user, if any.
      This array is passed to hook_user op login.
   @return boolean
      True if the login succeeds, False otherwise.
  """
  form = lib_common.drupal_get_form('user_login')
  state['values'] = edit
  if (php.empty(state['values']['name'])):
    state['values']['name'] = account.name
  # Check if user is blocked.
  lib_plugin.plugins['user'].login_name_validate(
    form, state, php.array_(account))
  if (lib_form.get_errors()):
    # Invalid login.
    return False
  # Valid login.
  lib_bootstrap.user = account
  lib_plugin.plugins['user'].authenticate_finalize(state['values'])
  return True



def load(array_={}):
  """
   Fetch a user object.
  
   @param array
     An associative array of attributes to search for in selecting the
     user, such as user name or e-mail address.
  
   @return
     A fully-loaded user object upon successful user load or False if user
     cannot be loaded.
  """
  # Dynamically compose a SQL query:
  query = []
  params = []
  if (php.is_numeric(array_)):
    array_ = {'uid' : array}
  elif (not php.is_array(array_)):
    return False
  for key,value in array_.items():
    if (key == 'uid' or key == 'status'):
      query.append( "key = %d" )
      params.append( value )
    elif (key == 'pass'):
      query.append( "pass = '%s'" )
      params.append( value )
    else:
      query.append( "LOWER(key) = LOWER('%s')" )
      params.append( value )
  result = lib_database.query('SELECT * FROM {users} u WHERE ' + \
    php.implode(' AND ', query), params)
  this_user = db_fetch_object(result)
  if (this_user):
    this_user = drupal_unpack(this_user)
    this_user.roles = {}
    if (this_user.uid):
      this_user.roles[DRUPAL_AUTHENTICATED_RID] = 'authenticated user'
    else:
      this_user.roles[DRUPAL_ANONYMOUS_RID] = 'anonymous user'
    result = lib_database.db_query(\
      'SELECT r.rid, r.name FROM {role} r ' + \
      'INNER JOIN {users_roles} ur ON ur.rid = r.rid ' + \
      'WHERE ur.uid = %d', this_user.uid)
    while True:
      role = lib_database.fetch_object(result)
      if not role:
        break
      this_user.roles[role.rid] = role.name
    module_invoke('load', array_, this_user)
  else:
    this_user = False
  return this_user


def save(account, array_={}, category = 'account'):
  """
   Save changes to a user account or add a new user.
  
   @param account
     The user object for the user to modify or add. If user.uid is
     omitted, a new user will be added.
  
   @param array
     An array of fields and values to save. For example array('name'
     : 'My name').  Keys that do not belong to columns in the user-related
     tables are added to the a serialized array in the 'data' column
     and will be loaded in the user.data array by user_load().
     Setting a field to None deletes it from the data column.
  
   @param category
     (optional) The category for storing profile information in.
  
   @return
     A fully-loaded user object upon successful save or False
     if the save failed.
  """
  table = lib_common.get_schema('users')
  user_fields = table['fields']
  if (not php.empty(array_['pass'])):
    # Allow alternate password hashing schemes.
    array_['pass'] = hash_password(php.trim(array_['pass']))
    # Abort if the hashing failed and returned False.
    if (not array_['pass']):
      return False
  else:
    # Avoid overwriting an existing password with a blank password.
    del(array_['pass'])
  if (php.is_object(account) and account.uid > 0):
    module_invoke('update', array_, account, category)
    data = php.unserialize(lib_database.result(lib_database.query(\
      'SELECT data FROM {users} WHERE uid = %d', account.uid)))
    # Consider users edited by an administrator as logged in, if they haven't
    # already, so anonymous users can view the profile (if allowed).
    if (php.empty(array_['access']) and php.empty(account.access) and \
        lib_plugin.plugins['user'].access('administer users')):
      array_['access'] = php.time_()
    for key,value in array_.items():
      # Fields that don't pertain to the users or user_roles
      # automatically serialized into the users.data column.
      if (key != 'roles' and ph.empty(user_fields[key])):
        if (value is None):
          del(data[key])
        else:
          data[key] = value
    array_['data'] = data
    array_['uid'] = account.uid
    # Save changes to the users table.
    success = lib_common.drupal_write_record('users', array_, 'uid')
    if (not success):
      # The query failed - better to abort the save than risk further
      # data loss.
      return False
    # Reload user roles if provided.
    if (php.isset(php.array_['roles']) and php.is_array(array_['roles'])):
      lib_database.db_query('DELETE FROM {users_roles} WHERE uid = %d', \
        account.uid)
      for rid in php.array_keys(array_['roles']):
        if (not php.in_array(rid, (DRUPAL_ANONYMOUS_RID, \
            DRUPAL_AUTHENTICATED_RID))):
          lin_database.db_query(\
            'INSERT INTO {users_roles} (uid, rid) VALUES (%d, %d)', \
            account.uid, rid)
    # Delete a blocked user's sessions to kick them if they are online.
    if (php.isset(array_['status']) and array_['status'] == 0):
      lib_session.destroy_uid(account.uid)
    # If the password changed, delete all open sessions and recreate
    # the current one.
    if (not empty(array_['pass'])):
      lib_session.destroy_uid(account.uid)
      lib_session.regenerate()
    # Refresh user object.
    this_user = load({'uid' : account.uid})
    # Send emails after we have the new user object.
    if (php.isset(array_['status']) and array_['status'] != account.status):
      # The user's status is changing; conditionally send notification email.
      op = ('status_activated' if (array_['status'] == 1) else \
        'status_blocked')
      _mail_notify(op, this_user)
    module_invoke('after_update', array_, this_user, category)
  else:
    # Allow 'created' to be set by the caller.
    if (not php.isset(array_['created'])):
      array_['created'] = php.time_()
    # Consider users created by an administrator as already logged in, so
    # anonymous users can view the profile (if allowed).
    if (php.empty(array_['access']) and access('administer users')):
      array_['access'] = php.time_()
    success = lib_common.drupal_write_record('users', array_)
    if (not success):
      # On a failed INSERT some other existing user's uid may be returned.
      # We must abort to avoid overwriting their account.
      return False
    # Build the initial user object.
    this_user = load({'uid' : array_['uid']})
    module_invoke('insert', array_, this_user, category)
    # Note, we wait with saving the data column to prevent module-handled
    # fields from being saved there.
    data = []
    for key,value in array_.items():
      if ((key != 'roles') and (php.empty(user_fields[key])) and \
          (value != None)):
        data[key] = value
    if (not empty(data)):
      data_array = {'uid' : user.uid, 'data' : data}
      lib_common.drupal_write_record('users', data_array, 'uid')
    # Save user roles (delete just to be safe).
    if (php.isset(array_['roles']) and php.is_array(array_['roles'])):
      lib_database.db_query('DELETE FROM {users_roles} WHERE uid = %d', \
        array_['uid'])
      for rid in php.array_keys(array_['roles']): 
        if (not php.in_array(rid, (DRUPAL_ANONYMOUS_RID, \
            DRUPAL_AUTHENTICATED_RID))):
          db_query('INSERT INTO {users_roles} (uid, rid) VALUES (%d, %d)', \
            array_['uid'], rid)
    # Build the finished user object.
    this_user = load({'uid' : array_['uid']})
  return this_user



def validate_name(name):
  """
   Verify the syntax of the given name.
  """
  if (not name):
    return lib_common.t('You must enter a username.')
  if (php.substr(name, 0, 1) == ' '):
    return lib_common.t('The username cannot begin with a space.')
  if (php.substr(name, -1) == ' '):
    return lib_common.t('The username cannot end with a space.')
  if (php.strpos(name, '  ') != False):
    return lib_common.t(\
      'The username cannot contain multiple spaces in a row.')
  if (php.preg_match('/[^\x{80}-\x{F7} a-z0-9@_.\'-]/i', name)):
    return lib_common.t('The username contains an illegal character.')
  if (php.preg_match(\
    # Non-printable ISO-8859-1 + NBSP
    '/[\x{80}-\x{A0}' + \
    # Soft-hyphen 
    '\x{AD}' + \
    # Various space characters
    '\x{2000}-\x{200F}' + \
    # Bidirectional text overrides
    '\x{2028}-\x{202F}' + \
    # Various text hinting characters
    '\x{205F}-\x{206F}' + \
    # Byte order mark
    '\x{FEFF}' + \
    # Full-width latin
    '\x{FF01}-\x{FF60}' + \
    # Replacement characters
    '\x{FFF9}-\x{FFFD}' + \
    # None byte and control characters
    '\x{0}-\x{1F}]/u',        
    name)):
    return lib_common.t('The username contains an illegal character.')
  if (drupal_strlen(name) > USERNAME_MAX_LENGTH):
    return lib_common.t(\
      'The username %name is too long: it must be %max characters or less.', \
      {'%name' : name, '%max' : USERNAME_MAX_LENGTH})



def validate_mail(mail):
  if (not mail):
    return lib_common.t('You must enter an e-mail address.')
  if (not valid_email_address(mail)):
    return lib_common.t('The e-mail address %mail is not valid.', \
      {'%mail' : mail})



def validate_picture(form, form_state):
  php.Reference.check(form)
  php.Reference.check(form_state)  
  # If required, validate the uploaded picture.
  validators = {
    'file_validate_is_image' : [],
    'file_validate_image_resolution' : \
      (lib_bootstrap.variable_get('user_picture_dimensions', '85x85')),
    'file_validate_size' : \
      (lib_bootstrap.variable_get('user_picture_file_size', '30') * 1024)
  }
  file_ = lib_file.save_upload('picture_upload', validators)
  if (file_):
    # Remove the old picture.
    if (php.isset(form_state['values']['_account'].picture) and \
        lib_file.exists(form_state['values']['_account'].picture)):
      lib_file.delete(form_state['values']['_account'].picture)
    # The image was saved using file_save_upload() and was added to the
    # files table as a temporary file. We'll make a copy and let the garbage
    # collector delete the original upload.
    info = image_get_info(file_.filepath)
    destination = lib_bootstrap.variable_get('user_picture_path', \
      'pictures') + '/picture-'  + form['#uid'] + '.' + info['extension']
    if (lib_file.copy(file_, destination, FILE_EXISTS_REPLACE)):
      form_state['values']['picture'] = file_.filepath
    else:
      lib_form.set_error('picture_upload', \
        lib_common.t("Failed to upload the picture image; " + \
        "the %directory directory doesn't exist or is not writable.", \
        {'%directory' : \
        lib_common.variable_get('user_picture_path', 'pictures')}))


def user_password(length=10):
  """
   Generate a random alphanumeric password.
  """
  # This variable contains the list of allowable characters for the
  # password. Note that the number 0 and the letter 'O' have been
  # removed to avoid confusion between the two. The same is True
  # of 'I', 1, and 'l'.
  allowable_characters = \
    'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  # Zero-based count of characters in the allowable list:
  len_ = php.strlen(allowable_characters) - 1
  # Declare the password as a blank string.
  pass_ = ''
  # Loop the number of times specified by length.
  for i in range(length):
    # Each iteration, pick a random character from the
    # allowable string and append it to the password:
    pass_ += allowable_characters[php.mt_rand(0, len_)]
  return pass_


def role_permissions(roles=[], reset=False):
  """
   Determine the permissions for one or more roles.
  
   @param roles
     An array whose keys are the role IDs of interest, such as user.roles.
   @param reset
     Optional parameter - if True data in the static variable is rebuilt.
  
   @return
     An array indexed by role ID. Each value is an array whose keys are the
     permission strings for the given role ID.
  """
  php.static(role_permissions, 'stored_permissions', {})
  if (reset):
    # Clear the data cached in the static variable.
    role_permissions.stored_permissions = {}
  role_permissions_ = fetch = []
  if (roles):
    for rid,name in roles.items():
      if (php.isset(role_permissions.stored_permissions[rid])):
        role_permissions_[rid] = role_permissions.stored_permissions[rid]
      else:
        # Add this rid to the list of those needing to be fetched.
        fetch.append( rid )
        # Prepare in case no permissions are returned.
        role_permissions.stored_permissions[rid] = {}
    if (fetch):
      # Get from the database permissions that were not in the static variable.
      # Only role IDs with at least one permission assigned will return rows.
      result = lib_database.query(\
        "SELECT r.rid, p.permission FROM {role} r " + \
        "INNER JOIN {role_permission} p ON p.rid = r.rid " + \
        "WHERE r.rid IN (" +  lib_database.placeholders(fetch)  + ")", fetch)
      while True:
        row = lib_database.fetch_array(result)
        if not row:
          break
        role_permissions.stored_permissions[row['rid']][row['permission']] = \
          True
      for rid in fetch:
        # For every rid, we know we at least assigned an empty array.
        role_permissions_[rid] = role_permissions.stored_permissions[rid]
  return role_permissions_


def access(string_, account=None, reset=False):
  """
   Determine whether the user has a given privilege.
  
   @param string
     The permission, such as "administer nodes", being checked for.
   @param account
     (optional) The account to check,
     if not given use currently logged in user.
   @param reset
     (optional) Resets the user's permissions cache, which will result in a
     recalculation of the user's permissions. This is necessary to support
     dynamically added user roles.
  
   @return
     Boolean True if the current user has the requested permission.
  
   All permission checks in Drupal should go through this function. This
   way, we guarantee consistent behavior, and ensure that the superuser
   can perform all actions.
  """
  php.static(access, 'perm', {})
  if (reset):
    access.perm = {}
  if (account is None):
    account = lib_bootstrap.user
  # User #1 has all privileges:
  if (account.uid == 1):
    return True
  # To reduce the number of SQL queries, we cache the user's permissions
  # in a static variable.
  if (not php.isset(access.perm[account.uid])):
    role_permissions = role_permissions(account.roles, reset)
    access.perms = {}
    for one_role in role_permissions:
      access.perms += one_role
    access.perm[account.uid] = access.perms
  return php.isset(access.perm[account.uid][string])


def is_blocked(name):
  """
   Checks for usernames blocked by user administration.
  
   @return boolean True for blocked users, False for active.
  """
  deny = lib_database.fetch_object(\
    lib_database.query(\
    "SELECT name FROM {users} WHERE status = 0 AND name = LOWER('%s')", \
    name))
  return deny


def hook_perm():
  """
   Implementation of hook_perm().
  """
  return {
    'administer permissions' : lib_common.t(\
      'Manage the permissions assigned to user roles + %warning', \
      {'%warning' : lib_common.t(\
      'Warning: Give to trusted roles only; ' + \
      'this permission has security implications.')}),
    'administer users' : lib_common.t(\
      'Manage or block users, and manage their role assignments.'),
    'access user profiles' : lib_common.t(\
      'View profiles of users on the site, ' + \
      'which may contain personal information.'),
    'change own username' : t('Select a different username.'),
  }


def hook_file_download(file):
  """
   Implementation of hook_file_download().
  
   Ensure that user pictures (avatars) are always downloadable.
  """
  if (php.strpos(file, lib_bootstrap.variable_get(\
      'user_picture_path', 'pictures') +  '/picture-') == 0):
    info = lib_plugin.plugins['image'].get_info(\
      lib_plugin.plugins['file'].create_path(file))
    return ('Content-type: ' +  info['mime_type'],)


def hook_search(op = 'search', keys = None, skip_access_check = False):
  """
   Implementation of hook_search().
  """
  if op == 'name':
    if (skip_access_check or access('access user profiles')):
      return lib_common.t('Users')
  elif op == 'search':
    if (access('access user profiles')):
      find = []
      # Replace wildcards with MySQL/PostgreSQL wildcards.
      keys = php.preg_replace('not \*+not ', '%', keys)
      if (access('administer users')):
        # Administrators can also search in the otherwise private email field.
        result = lib_database.pager_query(\
          "SELECT name, uid, mail FROM {users} " + \
          "WHERE LOWER(name) LIKE LOWER('%%%s%%') OR " + \
          "LOWER(mail) LIKE LOWER('%%%s%%')", 15, 0, None, keys, keys)
        while True:
          account = db_fetch_object(result)
          if not account:
            break
          find.append({
            'title' : account.name + ' ('  + account.mail + ')', \
            'link' : \
              lib_common.url('user/' + account.uid, {'absolute' : True})
          })
      else:
        result = lib_database.pager_query(\
          "SELECT name, uid FROM {users} " + \
          "WHERE LOWER(name) LIKE LOWER('%%%s%%')", 15, 0, None, keys)
        while True:
          account = db_fetch_object(result)
          if not account:
            break;
          find.append({
            'title' : account.name,
            'link' : lib_common.url('user/' +  account.uid, \
              {'absolute' : True})
          })
    return find



def hook_elements():
  """
   Implementation of hook_elements().
  """
  return {
    'user_profile_category' : [],
    'user_profile_item' : []
  }



def hook_user(type, edit, account, category=None):
  """
   Implementation of hook_user().
  """
  php.Reference.check(edit)
  php.Reference.check(account)
  if (type == 'view'):
    account.content['user_picture'] = {
      '#value' : lib_theme.theme('user_picture', account),
      '#weight' : -10
    }
    if (not php.isset(account.content, 'summary')):
      account.content['summary'] = {}
    account.content['summary'] += {
      '#type' : 'user_profile_category',
      '#attributes' : {'class' : 'user-member'},
      '#weight' : 5,
      '#title' : lib_common.t('History')
    }
    account.content['summary']['member_for'] = {
      '#type' : 'user_profile_item',
      '#title' : lib_theme.t('Member for'),
      '#value' : format_interval(php.time_() - account.created)
    }
  if (type == 'form' and category == 'account'):
    form_state = {}
    return edit_form(form_state, lib_common.arg(1), edit)
  if (type == 'validate' and category == 'account'):
    return _user_edit_validate(arg(1), edit)
  if (type == 'submit' and category == 'account'):
    return _user_edit_submit(arg(1), edit)
  if (type == 'categories'):
    return ({
      'name' : 'account',
      'title' : lib_common.t('Account settings'),
      'weight' : 1
    },)





def login_block():
  form = {
    '#action' : lib_common.url(php.GET['q'], \
      {'query' : drupal_get_destination()}),
    '#id' : 'user-login-form',
    '#validate' : login_default_validators(),
    '#submit' : ('user_login_submit',),
  }
  form['name'] = {
    '#type' : 'textfield',
    '#title' : t('Username'),
    '#maxlength' : USERNAME_MAX_LENGTH,
    '#size' : 15,
    '#required' : True,
  }
  form['pass'] = {
    '#type' : 'password',
    '#title' : lib_common.t('Password'),
    '#maxlength' : 60,
    '#size' : 15,
    '#required' : True
  }
  form['submit'] = {
    '#type' : 'submit',
    '#value' : lib_common.t('Log in')
  }
  items = {}
  if (lib_bootstrap.variable_get('user_register', 1)):
    items.append( lib_common.l(\
      lib_common.t('Create new account'), 'user/register', \
      {'attributes' : {'title' : t('Create a new user account.')}}) )
  items.append( lib_common.l(\
    t('Request new password'), \
    'user/password', {'attributes' : \
    {'title' : lib_common.t('Request new password via e-mail.')}}) )
  form['links'] = {'#value' : lib_theme.theme('item_list', items)}
  return form




def hook_block(op='list', delta='', edit=[]):
  """
   Implementation of hook_block().
  """
  if (op == 'list'):
    blocks = {
      'login' : {},
      'navigation' : {},
      'new' : {},
      'online' : {}
    }
    blocks['login']['info'] = lib_common.t('User login')
    # Not worth caching.
    blocks['login']['cache'] = BLOCK_NO_CACHE
    blocks['navigation']['info'] = lib_common.t('Navigation')
    # Menu blocks can't be cached because each menu item can have
    # a custom access callback. menu.inc manages its own caching.
    blocks['navigation']['cache'] = BLOCK_NO_CACHE
    blocks['new']['info'] = lib_common.t('Who\'s new')
    # Too dynamic to cache.
    blocks['online']['info'] = lib_common.t('Who\'s online')
    blocks['online']['cache'] = BLOCK_NO_CACHE
    return blocks
  elif (op == 'configure' and delta == 'new'):
    form['user_block_whois_new_count'] = {
      '#type' : 'select',
      '#title' : lib_common.t('Number of users to display'),
      '#default_value' : \
        lib_bootstrap.variable_get('user_block_whois_new_count', 5),
      '#options' : drupal_map_assoc((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    }
    return form
  elif (op == 'configure' and delta == 'online'):
    period = drupal_map_assoc(
      (30, 60, 120, 180, 300, 600, 900, 1800, 2700, 3600, 5400, 7200, \
      10800, 21600, 43200, 86400), 'format_interval')
    form['user_block_seconds_online'] = {
      '#type' : 'select',
      '#title' : lib_common.t('User activity'),
      '#default_value' : \
        lib_bootstrap.variable_get('user_block_seconds_online', 900),
      '#options' : period,
      '#description' : \
        lib.common.t('A user is considered online for ' + \
        'this long after they have last viewed a page.')
    }
    form['user_block_max_list_count'] = {'#type' : 'select', \
      '#title' : lib_common.t('User list length'), \
      '#default_value' : \
      lib_bootstrap.variable_get('user_block_max_list_count', 10), \
      '#options' : drupal_map_assoc(\
      (0, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100)), \
      '#description' : lib_common.t('Maximum number of ' + \
      'currently online users to display.')}
    return form
  elif (op == 'save' and delta == 'new'):
    lib_bootstrap.variable_set('user_block_whois_new_count', \
      edit['user_block_whois_new_count'])
  elif (op == 'save' and delta == 'online'):
    lib_bootstrap.variable_set('user_block_seconds_online', \
      edit['user_block_seconds_online'])
    lib_bootstrap.variable_set('user_block_max_list_count', \
      edit['user_block_max_list_count'])
  elif (op == 'view'):
    block = {}
    if delta == 'login':
      # For usability's sake, avoid showing two login forms on one page.
      if (lib_bootstrap.user.uid < 1 and not \
          (lib_path.arg(0) == 'user' and not php.is_numeric(lib_path.arg(1)))):
        block['subject'] = lib_common.t('User login')
        block['content'] = drupal_get_form('user_login_block')
      return block
    elif delta == 'navigation':
      menu = lib_menu.tree()
      if (menu):
        block['subject'] = (check_plain(lib_bootstrap.user.name) if \
          (user.uid > 0) else \
          lib_common.t('Navigation'))
        block['content'] = menu
      return block
    elif delta == 'new':
      if (access('access content')):
        # Retrieve a list of new users who have
        # subsequently accessed the site successfully.
        result = lib_database.query_range(\
          'SELECT uid, name FROM {users} ' + \
          'WHERE status != 0 AND access != 0 ' + \
          'ORDER BY created DESC', 0, \
          lib_common.variable_get('user_block_whois_new_count', 5))
        while True:
          account = lib_database.fetch_object(result)
          if not account:
            break
          items.append( account )
        output = lib_theme.theme('user_list', items)
        block['subject'] = lib_common.t('Who\'s new')
        block['content'] = output
      return block
    elif delta == 'online':
      if (access('access content')):
        # Count users active within the defined period.
        interval = time() - variable_get('user_block_seconds_online', 900)
        # Perform database queries to gather online user lists.
        # We use s.timestamp
        # rather than u.access because it is much faster.
        anonymous_count = sess_count(interval)
        authenticated_users = lib_database.query(\
          'SELECT DISTINCT u.uid, u.name, s.timestamp ' + \
          'FROM {users} u ' + \
          'INNER JOIN {sessions} s ON u.uid = s.uid ' + \
          'WHERE s.timestamp >= %d AND s.uid > 0 ' + \
          'ORDER BY s.timestamp DESC', interval)
        authenticated_count = 0
        max_users = lib_bootstrap.variable_get('user_block_max_list_count', 10)
        items = []
        while True:
          account = lib_database.fetch_object(authenticated_users)
          if (max_users > 0):
            items.append( account )
            max_users -= 1
          authenticated_count += 1
        # Format the output with proper grammar.
        if (anonymous_count == 1 and authenticated_count == 1):
          output = lib_common.t(\
            'There is currently %members and %visitors online.', \
            {'%members' : \
            format_plural(authenticated_count, '1 user', '@count users'), \
            '%visitors' : format_plural(anonymous_count, '1 guest', \
            '@count guests')})
        else:
          output = lib_common.t(\
            'There are currently %members and %visitors online.', \
            {'%members' : format_plural(authenticated_count, '1 user', \
            '@count users'), '%visitors' : \
            format_plural(anonymous_count, '1 guest', '@count guests')})
        # Display a list of currently online users.
        max_users = lib_bootstrap.variable_get('user_block_max_list_count', 10)
        if (authenticated_count and max_users):
          output += lib_theme.theme('user_list', items, \
            lib_common.t('Online users'))
        block['subject'] = lib_common.t('Who\'s online')
        block['content'] = output
      return block



def template_preprocess_user_picture(variables):
  """
   Process variables for user-picture.tpl.php.
  
   The variables array contains the following arguments:
   - account
  
   @see user-picture.tpl.php
  """
  php.Reference.check(variables)
  variables['picture'] = ''
  if (lib_bootstrap.variable_get('user_pictures', 0)):
    account = variables['account']
    if (not php.empty(account.picture) and php.file_exists(account.picture)):
      picture = lib_file.create_url(account.picture)
    elif (lib_bootstrap.variable_get('user_picture_default', '')):
      picture = variable_get('user_picture_default', '')
    if (php.isset(picture)):
      alt = lib_common.t("@user's picture", {'@user' : \
        (account.name if account.name else \
        lib_bootstrap.variable_get('anonymous', t('Anonymous')))})
      variables['picture'] = theme('image', picture, alt, alt, '', False)
      if (not empty(account.uid) and access('access user profiles')):
        attributes = {'attributes' : {'title' : t('View user profile.')}, \
          'html' : True}
        variables['picture'] = lib_common.l(variables['picture'], \
          "user/account.uid", attributes)




def theme_list(users, title=None):
  """
   Make a list of users.
  
   @param users
     An array with user objects. Should contain at least the name and uid.
   @param title
    (optional) Title to pass on to theme_item_list().
  
   @ingroup themeable
  """
  if (not php.empty(users)):
    for user in users:
      items.append( lib_theme.theme('username', user) )
  return lib_theme.theme('item_list', items, title)




def is_anonymous():
  # Menu administrators can see items for anonymous when administering.
  return not lib_bootstrap.user.uid or not php.empty(lib_bootstrap.menu_admin)


def is_logged_in():
  return bool(lib_bootstrap.user.uid)


def register_access():
  return is_anonymous() and lib_bootstrap.variable_get('user_register', 1)



def view_access(account):
  return account and account.uid and \
    (\
      # Always let users view their own profile.
      (lib_bootstrap.user.uid == account.uid) or \
      # Administrators can view all accounts.
      access('administer users') or \
      # The user is not blocked and logged in at least once.
      (account.access and account.status and access('access user profiles')) \
    )


"""
 Access callback for user account editing.
"""
def edit_access(account):
  return ((lib_bootstrap.user.uid == account.uid) or \
    access('administer users')) and account.uid > 0


def load_self(arg_):
  arg_[1] = load(lib_bootstrap.user.uid)
  return arg_


def hook_menu():
  """
   Implementation of hook_menu().
  """
  items = {}
  items['user/autocomplete'] = {
    'title' : 'User autocomplete',
    'page callback' : 'user_autocomplete',
    'access callback' : 'user_access',
    'access arguments' : ('access user profiles',),
    'type' : MENU_CALLBACK
  }
  # Registration and login pages.
  items['user'] = {
    'title' : 'User account',
    'page callback' : 'user_page',
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  items['user/login'] = {
    'title' : 'Log in',
    'access callback' : 'user_is_anonymous',
    'type' : MENU_DEFAULT_LOCAL_TASK
  }
  items['user/register'] = {
    'title' : 'Create new account',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_register',),
    'access callback' : 'user_register_access',
    'type' : MENU_LOCAL_TASK
  }
  items['user/password'] = {
    'title' : 'Request new password',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_pass',),
    'access callback' : 'user_is_anonymous',
    'type' : MENU_LOCAL_TASK
  }
  items['user/reset/%/%/%'] = {
    'title' : 'Reset password',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_pass_reset', 2, 3, 4),
    'access callback' : True,
    'type' : MENU_CALLBACK
  }
  # User administration pages.
  items['admin/user'] = {
    'title' : 'User management',
    'description' : \
      "Manage your site's users, groups and access to site features.",
    'position' : 'left',
    'page callback' : 'system_admin_menu_block_page',
    'access arguments' : ('access administration pages',)
  }
  items['admin/user/user'] = {
    'title' : 'Users',
    'description' : 'List, add, and edit users.',
    'page callback' : 'user_admin',
    'page arguments' : ('list',),
    'access arguments' : ('administer users',),
  }
  items['admin/user/user/list'] = {
    'title' : 'List',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -10
  }
  items['admin/user/user/create'] = {
    'title' : 'Add user',
    'page arguments' : ('create',),
    'access arguments' : ('administer users',),
    'type' : MENU_LOCAL_TASK
  }
  items['admin/user/settings'] = {
    'title' : 'User settings',
    'description' : \
      'Configure default behavior of users, including registration ' + \
      'requirements, e-mails, and user pictures.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_admin_settings',),
    'access arguments' : ('administer users',)
  }
  # Permission administration pages.
  items['admin/user/permissions'] = {
    'title' : 'Permissions',
    'description' : 'Determine access to features by ' + \
      'selecting permissions for roles.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_admin_perm',),
    'access arguments' : ('administer permissions',)
  }
  items['admin/user/roles'] = {
    'title' : 'Roles',
    'description' : 'List, edit, or add user roles.',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_admin_new_role',),
    'access arguments' : ('administer permissions',)
  }
  items['admin/user/roles/edit'] = {
    'title' : 'Edit role',
    'page arguments' : ('user_admin_role',),
    'access arguments' : ('administer permissions',),
    'type' : MENU_CALLBACK
  }
  items['logout'] = {
    'title' : 'Log out',
    'access callback' : 'user_is_logged_in',
    'page callback' : 'user_logout',
    'weight' : 10
  }
  items['user/%user_uid_optional'] = {
    'title' : 'My account',
    'title callback' : 'user_page_title',
    'title arguments' : (1,),
    'page callback' : 'user_view',
    'page arguments' : (1,),
    'access callback' : 'user_view_access',
    'access arguments' : (1,),
    'parent' : ''
  }
  items['user/%user/view'] = {
    'title' : 'View',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'weight' : -10
  }
  items['user/%user/delete'] = {
    'title' : 'Delete',
    'page callback' : 'drupal_get_form',
    'page arguments' : ('user_confirm_delete', 1),
    'access callback' : 'user_access',
    'access arguments' : ('administer users',),
    'type' : MENU_CALLBACK
  }
  items['user/%user_category/edit'] = {
    'title' : 'Edit',
    'page callback' : 'user_edit',
    'page arguments' : (1,),
    'access callback' : 'user_edit_access',
    'access arguments' : (1,),
    'type' : MENU_LOCAL_TASK,
    'load arguments' : ('%map', '%index')
  }
  items['user/%user_category/edit/account'] = {
    'title' : 'Account',
    'type' : MENU_DEFAULT_LOCAL_TASK,
    'load arguments' : ('%map', '%index')
  }
  empty_account = php.stdClass()
  categories = _user_categories(empty_account)
  if (categories and (php.count(categories) > 1)):
    for key,category in categories.items():
      # 'account' is already handled by the MENU_DEFAULT_LOCAL_TASK.
      if (category['name'] != 'account'):
        items['user/%user_category/edit/' +  category['name']] = {
          'title callback' : 'check_plain',
          'title arguments' : (category['title'],),
          'page callback' : 'user_edit',
          'page arguments' : (1, 3),
          'access callback' : (category['access callback'] if \
            php.isset(category['access callback']) else 'user_edit_access'),
          'access arguments' : (category['access arguments'] if \
            php.isset(category['access arguments']) else (1,)),
          'type' : MENU_LOCAL_TASK,
          'weight' : category['weight'],
          'load arguments' : ('%map', '%index'),
          'tab_parent' : 'user/%/edit'
        }
  return items



def hook_init():
  lib_common.drupal_add_css(lib_path.drupal_get_path('module', 'user') + \
    '/user.css', 'module')



def uid_optional_load(arg):
  return load((arg_ if php.isset(arg_) else lib_bootstrap.user.uid))



def category_load(uid, map_, index):
  """
   Return a user object after checking if any profile category in
   the path exists.
  """
  php.static(category_load, 'user_categories')
  php.static(category_load, 'accounts')
  php.Reference.check(map_)
  # Cache account - this load function will get called for each profile tab.
  if (not php.isset(category_load.accounts[uid])):
    category_load.accounts[uid] = load(uid)
  valid = True
  account = category_load.accounts[uid]
  if account:
    # Since the path is like user/%/edit/category_name, the category name will
    # be at a position 2 beyond the index corresponding to the % wildcard.
    category_index = index + 2
    # Valid categories may contain slashes, and hence need to be imploded.
    category_path = php.implode('/', php.array_slice(map_, category_index))
    if (category_path):
      # Check that the requested category exists.
      valid = False
      if (not php.isset(category_load.user_categories)):
        empty_account = php.stdClass()
        category_load.user_categories = _categories(empty_account)
      for category in category_load.user_categories:
        if (category['name'] == category_path):
          valid = True
          # Truncate the map array in case the category name had slashes.
          map_ = php.array_slice(map_, 0, category_index)
          # Assign the imploded category name to the last map element.
          map_[category_index] = category_path
          break
  return (account if valid else False)



def uid_optional_to_arg(arg_):
  """
   Returns the user id of the currently logged in user.
  """
  # Give back the current user uid when called from eg. tracker, aka.
  # with an empty arg. Also use the current user uid when called from
  # the menu with a % for the current account link.
  return (lib_bootstrap.user.uid if (php.empty(arg_) or arg_ == '%') else arg_)



def page_title(account):
  """
   Menu item title callback - use the user name if it's not the current user.
  """
  if (account.uid == lib_bootstrap.user.uid):
    return lib_common.t('My account')
  return account.name



def get_authmaps(authname=None):
  """
   Discover which external authentication module(s) authenticated a username.
  
   @param authname
     A username used by an external authentication module.
   @return
     An associative array with module as key and username as value.
  """
  result = lib_database.query(\
    "SELECT authname, module FROM {authmap} WHERE authname = '%s'", authname)
  authmaps = []
  has_rows = False
  while True:
    authmap = lib_database.fetch_object(result)
    if not authmap:
      break
    authmaps[authmap.module] = authmap.authname
    has_rows = True
  return (authmaps if has_rows else 0)



def set_authmaps(account, authmaps):
  """
   Save mappings of which external authentication module(s) authenticated
   a user. Maps external usernames to user ids in the users table.
  
   @param account
     A user object.
   @param authmaps
     An associative array with a compound key and the username as the value.
     The key is made up of 'authname_' plus the name of the
     external authentication
     module.
   @see user_external_login_register()
  """
  for key,value in authmaps.items():
    module = explode('_', key, 2)
    if (value):
      lib_database.query(\
        "UPDATE {authmap} SET authname = '%s' " + \
        "WHERE uid = %d AND module = '%s'", value, account.uid, module[1])
      if (not lib_database.affected_rows()):
        lib_database.query(\
          "INSERT INTO {authmap} (authname, uid, module) " + \
          "VALUES ('%s', %d, '%s')", value, account.uid, module[1])
    else:
      lib_database.query(\
        "DELETE FROM {authmap} WHERE uid = %d AND module = '%s'", \
        account.uid, module[1])



def login(form_state):
  """
   Form builder; the main user login form.
  
   @ingroup forms
  """
  php.Reference.check(form_state)
  # If we are already logged on, go to the user page instead.
  if (lib_bootstrap.user.uid):
    drupal_goto('user/' + lib_bootstrap.user.uid)
  # Display login form:
  form['name'] = {
    '#type' : 'textfield',
    '#title' : lib_common.t('Username'),
    '#size' : 60,
    '#maxlength' : USERNAME_MAX_LENGTH,
    '#required' : True,
    '#attributes' : {'tabindex' : '1'}
  }
  form['name']['#description'] = lib_common.t('Enter your @s username.', \
    {'@s' : lib_bootstrap.variable_get('site_name', 'Drupal')})
  form['pass'] = {
    '#type' : 'password',
    '#title' : lib_common.t('Password'),
    '#description' : lib_common.t(\
      'Enter the password that accompanies your username.'),
    '#required' : True,
    '#attributes' : {'tabindex' : '2'}
  }
  form['#validate'] = login_default_validators()
  form['submit'] = {'#type' : 'submit', '#value' : lib_common.t('Log in'), \
    '#weight' : 2, '#attributes' : {'tabindex' : '3'}}
  return form



def login_default_validators():
  """
   Set up a series for validators which check for blocked users,
   then authenticate against local database, then return an error if
   authentication fails. Distributed authentication modules are welcome
   to use hook_form_alter() to change this series in order to
   authenticate against their user database instead of the local users
   table.
  
   We use three validators instead of one since external authentication
   modules usually only need to alter the second validator.
  
   @see user_login_name_validate()
   @see user_login_authenticate_validate()
   @see user_login_final_validate()
   @return array
     A simple list of validate functions.
  """
  return ('user_login_name_validate', \
    'user_login_authenticate_validate', 'user_login_final_validate')



def login_name_validate(form, form_state):
  """
   A FAPI validate handler. Sets an error if supplied username
   has been blocked.
  """
  if (php.isset(form_state['values']['name']) and \
      is_blocked(form_state['values']['name'])):
    # Blocked in user administration.
    form_set_error('name', lib_common.t(\
      'The username %name has not been activated or is blocked.', \
      {'%name' : form_state['values']['name']}))


def login_authenticate_validate(form, form_state):
  """
   A validate handler on the login form. Check supplied username/password
   against local users table. If successful, sets the global user object.
  """
  authenticate(form_state['values'])



def login_final_validate(form, form_state):
  """
   A validate handler on the login form. Should be the last validator. Sets an
   error if user has not been authenticated yet.
  """
  php.Reference.check(form_state)
  if (not lib_bootstrap.user.uid):
    form_set_error('name', \
      lib_common.t(\
      'Sorry, unrecognized username or password. ' + \
      '<a href="@password">Have you forgotten your password?</a>', \
      {'@password' : url('user/password')}))
    watchdog('user', 'Login attempt failed for %user.', \
      {'%user' : form_state['values']['name']})



def authenticate(form_values=[]):
  """
   Try to log in the user locally.
  
   @param form_values
     Form values with at least 'name' and 'pass' keys, as well as anything else
     which should be passed along to hook_user op 'login'.
  
   @return
    A user object, if successful.
  """
  password = php.trim(form_values['pass'])
  # Name and pass keys are required.
  if (not php.empty(form_values['name']) and not php.empty(password)):
    account = lib_database.fetch_object(\
      lib_database.query(\
      "SELECT * FROM {users} WHERE name = '%s' AND status = 1", \
      form_values['name']))
    if (account):
      # Allow alternate password hashing schemes.
      if (check_password(password, account)):
        if (needs_new_hash(account)):
           new_hash = hash_password(password)
           if (new_hash):
             lib_database.query(\
               "UPDATE {users} SET pass = '%s' WHERE uid = %d", \
               new_hash, account.uid)
        account = load({'uid' : account.uid, 'status' : 1})
        lib_bootstrap.user = account
        authenticate_finalize(form_values)
        return lib_bootstrap.user



def authenticate_finalize(edit):
  """
   Finalize the login process. Must be called when logging in a user.
  
   The function records a watchdog message about the new session, saves the
   login timestamp, calls hook_user op 'login' and generates a new session.
  
   param edit
     This array is passed to hook_user op login.
  """
  php.Reference.check(edit)
  watchdog('user', 'Session opened for %name.', \
    {'%name' : lib_bootstrap.user.name})
  # Update the user table timestamp noting user has logged in.
  # This is also used to invalidate one-time login links.
  lib_bootstrap.user.login = php.time_()
  lib_database.query("UPDATE {users} SET login = %d WHERE uid = %d", \
    lib_bootstrap.user.login, lib_bootstrap.user.uid)
  module_invoke('login', edit, lib_bootstrap.user)
  lib_session.regenerate()




def form_login_submit(form, form_state):
  """
   Submit handler for the login form. Redirects the user to a page.
  
   The user is redirected to the My Account page. Setting the destination in
   the query string (as done by the user login block) overrides the redirect.
  """
  php.Reference.check(form_state)
  if (lib_bootstrap.user.uid):
    form_state['redirect'] = 'user/' +  lib_bootstrap.user.uid
    return



def external_login_register(name, module):
  """
   Helper function for authentication modules. Either login in or registers
   the current user, based on username. Either way, the global user object is
   populated based on name.
  """
  lib_bootstrap.user = load({'name' : name})
  if (not php.isset(lib_bootstrap.user.uid)):
    # Register this new user.
    userinfo = {
      'name' : name,
      'pass' : password(),
      'init' : name,
      'status' : 1,
      'access' : php.time_()
    }
    account = save('', userinfo)
    # Terminate if an error occured during user_save().
    if (not account):
      drupal_set_message(lib_common.t("Error saving user account."), 'error')
      return
    user_set_authmaps(account, {"authname_module" : name})
    user = account
    watchdog('user', 'New external user: %name using module %module.', \
      {'%name' : name, '%module' : module}, \
      WATCHDOG_NOTICE, lib_common.l(lib_common.t('edit'), \
      'user/' +  lib_bootstrap.user.uid  + '/edit'))




def user_pass_reset_url(account):
  timestamp = time()
  return url("user/reset/account.uid/timestamp/" +  user_pass_rehash(account.pass, timestamp, account.login), array('absolute' : True))
}

def user_pass_rehash(password, timestamp, login):
  return md5(timestamp +  password  + login)
}

def user_edit_form(&form_state, uid, edit, register = False):
  _user_password_dynamic_validation()
  admin = user_access('administer users')
  # Account information:
  form['account'] = array('#type' : 'fieldset',
    '#title' : t('Account information'),
    '#weight' : -10,
  )
  if (user_access('change own username') or admin or register):
    form['account']['name'] = array('#type' : 'textfield',
      '#title' : t('Username'),
      '#default_value' : edit['name'],
      '#maxlength' : USERNAME_MAX_LENGTH,
      '#description' : t('Spaces are allowed; punctuation is not allowed except for periods, hyphens, apostrophes, and underscores.'),
      '#required' : True,
    )
  }
  form['account']['mail'] = array('#type' : 'textfield',
    '#title' : t('E-mail address'),
    '#default_value' : edit['mail'],
    '#maxlength' : EMAIL_MAX_LENGTH,
    '#description' : t('A valid e-mail address. All e-mails from the system will be sent to this address. The e-mail address is not made public and will only be used if you wish to receive a new password or wish to receive certain news or notifications by e-mail.'),
    '#required' : True,
  )
  if (not register):
    form['account']['pass'] = array('#type' : 'password_confirm',
      '#description' : t('To change the current user password, enter the new password in both fields.'),
      '#size' : 25,
    )
  }
  elif (not variable_get('user_email_verification', True) or admin):
    form['account']['pass'] = array(
      '#type' : 'password_confirm',
      '#description' : t('Provide a password for the new account in both fields.'),
      '#required' : True,
      '#size' : 25,
    )
  }
  if (admin):
    form['account']['status'] = array(
      '#type' : 'radios',
      '#title' : t('Status'),
      '#default_value' : isset(edit['status']) ? edit['status'] : 1,
      '#options' : array(t('Blocked'), t('Active'))
    )
  }
  if (user_access('administer permissions')):
    roles = user_roles(True)
    # The disabled checkbox subelement for the 'authenticated user' role
    # must be generated separately and added to the checkboxes element,
    # because of a limitation in D6 FormAPI not supporting a single disabled
    # checkbox within a set of checkboxes.
    # TODO: This should be solved more elegantly. See issue #119038.
    checkbox_authenticated = array(
      '#type' : 'checkbox',
      '#title' : roles[DRUPAL_AUTHENTICATED_RID],
      '#default_value' : True,
      '#disabled' : True,
    )
    unset(roles[DRUPAL_AUTHENTICATED_RID])
    if (roles):
      default = empty(edit['roles']) ? array() : array_keys(edit['roles'])
      form['account']['roles'] = array(
        '#type' : 'checkboxes',
        '#title' : t('Roles'),
        '#default_value' : default,
        '#options' : roles,
        DRUPAL_AUTHENTICATED_RID : checkbox_authenticated,
      )
    }
  }

  # Signature:
  if (variable_get('user_signatures', 0) and module_exists('comment') and not register):
    form['signature_settings'] = array(
      '#type' : 'fieldset',
      '#title' : t('Signature settings'),
      '#weight' : 1,
    )
    form['signature_settings']['signature'] = array(
      '#type' : 'textarea',
      '#title' : t('Signature'),
      '#default_value' : edit['signature'],
      '#description' : t('Your signature will be publicly displayed at the end of your comments.'),
    )
  }

  # Picture/avatar:
  if (variable_get('user_pictures', 0) and not register):
    form['picture'] = array('#type' : 'fieldset', '#title' : t('Picture'), '#weight' : 1)
    picture = theme('user_picture', (object)edit)
    if (edit['picture']):
      form['picture']['current_picture'] = array('#value' : picture)
      form['picture']['picture_delete'] = array('#type' : 'checkbox', '#title' : t('Delete picture'), '#description' : t('Check this box to delete your current picture.'))
    }
    else:
      form['picture']['picture_delete'] = array('#type' : 'hidden')
    }
    form['picture']['picture_upload'] = array('#type' : 'file', '#title' : t('Upload picture'), '#size' : 48, '#description' : t('Your virtual face or picture. Maximum dimensions are %dimensions and the maximum size is %size kB.', array('%dimensions' : variable_get('user_picture_dimensions', '85x85'), '%size' : variable_get('user_picture_file_size', '30'))) . ' ' . variable_get('user_picture_guidelines', ''))
    form['#validate'][] = 'user_validate_picture'
  }
  form['#uid'] = uid
  return form
}

def _user_edit_validate(uid, &edit):
  user = user_load(array('uid' : uid))
  # Validate the username:
  if (user_access('change own username') or user_access('administer users') or not user.uid):
    if (error = user_validate_name(edit['name'])):
      form_set_error('name', error)
    }
    elif (db_result(db_query("SELECT COUNT(*) FROM {users} WHERE uid != %d AND LOWER(name) = LOWER('%s')", uid, edit['name'])) > 0):
      form_set_error('name', t('The name %name is already taken.', array('%name' : edit['name'])))
    }
  }

  # Validate the e-mail address:
  if (error = user_validate_mail(edit['mail'])):
    form_set_error('mail', error)
  }
  elif (db_result(db_query("SELECT COUNT(*) FROM {users} WHERE uid != %d AND LOWER(mail) = LOWER('%s')", uid, edit['mail'])) > 0):
    form_set_error('mail', t('The e-mail address %email is already registered + <a href="@password">Have you forgotten your password?</a>', array('%email' : edit['mail'], '@password' : url('user/password'))))
  }
}

def _user_edit_submit(uid, &edit):
  user = user_load(array('uid' : uid))
  # Delete picture if requested, and if no replacement picture was given.
  if (not empty(edit['picture_delete'])):
    if (user.picture and file_exists(user.picture)):
      file_delete(user.picture)
    }
    edit['picture'] = ''
  }
  if (isset(edit['roles'])):
    edit['roles'] = array_filter(edit['roles'])
  }
}
#
# Delete a user.
#
# @param edit An array of submitted form values.
# @param uid The user ID of the user to delete.
#
def user_delete(edit, uid):
  account = user_load(array('uid' : uid))
  sess_destroy_uid(uid)
  _user_mail_notify('status_deleted', account)
  db_query('DELETE FROM {users} WHERE uid = %d', uid)
  db_query('DELETE FROM {users_roles} WHERE uid = %d', uid)
  db_query('DELETE FROM {authmap} WHERE uid = %d', uid)
  variables = array('%name' : account.name, '%email' : '<' +  account.mail  + '>')
  watchdog('user', 'Deleted user: %name %email.', variables, WATCHDOG_NOTICE)
  module_invoke_all('user', 'delete', edit, account)
}
#
# Builds a structured array representing the profile content.
#
# @param account
#   A user object.
#
# @return
#   A structured array containing the individual elements of the profile.
#
def user_build_content(&account):
  edit = None
  user_module_invoke('view', edit, account)
  # Allow modules to modify the fully-built profile.
  drupal_alter('profile', account)
  return account.content
}
#
# Implementation of hook_mail().
#
def user_mail(key, &message, params):
  language = message['language']
  variables = user_mail_tokens(params['account'], language)
  message['subject'] += _user_mail_text(key +  '_subject', language, variables)
  message['body'][] = _user_mail_text(key +  '_body', language, variables)
}
#
# Returns a mail string for a variable name.
#
# Used by user_mail() and the settings forms to retrieve strings.
#
def _user_mail_text(key, language = None, variables = array()):
  langcode = isset(language) ? language.language : None
  if (admin_setting = variable_get('user_mail_' +  key, False)):
    # An admin setting overrides the default string.
    return strtr(admin_setting, variables)
  }
  else:
    # No override, return default string.
    switch (key):
      case 'register_no_approval_required_subject':
        return t('Account details for not username at not site', variables, langcode)
      case 'register_no_approval_required_body':
        return t("not username,\n\nThank you for registering at not site + You may now log in to not login_uri using the following username and password:\n\nusername: not username\npassword: not password\n\nYou may also log in by clicking on this link or copying and pasting it in your browser:\n\nnot login_url\n\nThis is a one-time login, so it can be used only once.\n\nAfter logging in, you will be redirected to not edit_uri so you can change your password.\n\n\n--  not site team", variables, langcode)
      case 'register_admin_created_subject':
        return t('An administrator created an account for you at not site', variables, langcode)
      case 'register_admin_created_body':
        return t("not username,\n\nA site administrator at not site has created an account for you + You may now log in to not login_uri using the following username and password:\n\nusername: not username\npassword: not password\n\nYou may also log in by clicking on this link or copying and pasting it in your browser:\n\nnot login_url\n\nThis is a one-time login, so it can be used only once.\n\nAfter logging in, you will be redirected to not edit_uri so you can change your password.\n\n\n--  not site team", variables, langcode)
      case 'register_pending_approval_subject':
      case 'register_pending_approval_admin_subject':
        return t('Account details for not username at not site (pending admin approval)', variables, langcode)
      case 'register_pending_approval_body':
        return t("not username,\n\nThank you for registering at not site + Your application for an account is currently pending approval. Once it has been approved, you will receive another e-mail containing information about how to log in, set your password, and other details.\n\n\n--  not site team", variables, langcode)
      case 'register_pending_approval_admin_body':
        return t("not username has applied for an account.\n\nnot edit_uri", variables, langcode)
      case 'password_reset_subject':
        return t('Replacement login information for not username at not site', variables, langcode)
      case 'password_reset_body':
        return t("not username,\n\nA request to reset the password for your account has been made at not site.\n\nYou may now log in to not uri_brief by clicking on this link or copying and pasting it in your browser:\n\nnot login_url\n\nThis is a one-time login, so it can be used only once + It expires after one day and nothing will happen if it's not used.\n\nAfter logging in, you will be redirected to not edit_uri so you can change your password.", variables, langcode)
      case 'status_activated_subject':
        return t('Account details for not username at not site (approved)', variables, langcode)
      case 'status_activated_body':
        return t("not username,\n\nYour account at not site has been activated.\n\nYou may now log in by clicking on this link or copying and pasting it in your browser:\n\nnot login_url\n\nThis is a one-time login, so it can be used only once.\n\nAfter logging in, you will be redirected to not edit_uri so you can change your password.\n\nOnce you have set your own password, you will be able to log in to not login_uri in the future using:\n\nusername: not username\n", variables, langcode)
      case 'status_blocked_subject':
        return t('Account details for not username at not site (blocked)', variables, langcode)
      case 'status_blocked_body':
        return t("not username,\n\nYour account on not site has been blocked.", variables, langcode)
      case 'status_deleted_subject':
        return t('Account details for not username at not site (deleted)', variables, langcode)
      case 'status_deleted_body':
        return t("not username,\n\nYour account on not site has been deleted.", variables, langcode)
    }
  }
}
# Administrative features ***********************************************/
#
# Retrieve an array of roles matching specified conditions.
#
# @param membersonly
#   Set this to True to exclude the 'anonymous' role.
# @param permission
#   A string containing a permission. If set, only roles containing that
#   permission are returned.
#
# @return
#   An associative array with the role id as the key and the role name as
#   value.
#
def user_roles(membersonly = False, permission = None):
  # System roles take the first two positions.
  roles = array(
    DRUPAL_ANONYMOUS_RID : None,
    DRUPAL_AUTHENTICATED_RID : None,
  )
  if (not empty(permission)):
    result = db_query("SELECT r.* FROM {role} r INNER JOIN {role_permission} p ON r.rid = p.rid WHERE p.permission = '%s' ORDER BY r.name", permission)
  }
  else:
    result = db_query('SELECT * FROM {role} ORDER BY name')
  }

  while (role = db_fetch_object(result)):
    switch (role.rid):
      # We only translate the built in role names
      case DRUPAL_ANONYMOUS_RID:
        if (not membersonly):
          roles[role.rid] = t(role.name)
        }
        break
      case DRUPAL_AUTHENTICATED_RID:
        roles[role.rid] = t(role.name)
        break
      default:
        roles[role.rid] = role.name
    }
  }

  # Filter to remove unmatched system roles.
  return array_filter(roles)
}
#
# Implementation of hook_user_operations().
#
def user_user_operations(form_state = array()):
  operations = array(
    'unblock' : array(
      'label' : t('Unblock the selected users'),
      'callback' : 'user_user_operations_unblock',
    ),
    'block' : array(
      'label' : t('Block the selected users'),
      'callback' : 'user_user_operations_block',
    ),
    'delete' : array(
      'label' : t('Delete the selected users'),
    ),
  )
  if (user_access('administer permissions')):
    roles = user_roles(True)
    unset(roles[DRUPAL_AUTHENTICATED_RID]);  // Can't edit authenticated role.

    add_roles = array()
    for key,value in roles.items():
      add_roles['add_role-' +  key] = value
    }

    remove_roles = array()
    for key,value in roles.items():
      remove_roles['remove_role-' +  key] = value
    }

    if (count(roles)):
      role_operations = array(
        t('Add a role to the selected users') : array(
          'label' : add_roles,
        ),
        t('Remove a role from the selected users') : array(
          'label' : remove_roles,
        ),
      )
      operations += role_operations
    }
  }

  # If the form has been posted, we need to insert the proper data for
  # role editing if necessary.
  if (not empty(form_state['submitted'])):
    operation_rid = explode('-', form_state['values']['operation'])
    operation = operation_rid[0]
    if (operation == 'add_role' or operation == 'remove_role'):
      rid = operation_rid[1]
      if (user_access('administer permissions')):
        operations[form_state['values']['operation']] = array(
          'callback' : 'user_multiple_role_edit',
          'callback arguments' : array(operation, rid),
        )
      }
      else:
        watchdog('security', 'Detected malicious attempt to alter protected user fields.', array(), WATCHDOG_WARNING)
        return
      }
    }
  }

  return operations
}
#
# Callback function for admin mass unblocking users.
#
def user_user_operations_unblock(accounts):
  for uid in accounts:
    account = user_load(array('uid' : (int)uid))
    # Skip unblocking user if they are already unblocked.
    if (account !== False and account.status == 0):
      user_save(account, array('status' : 1))
    }
  }
}
#
# Callback function for admin mass blocking users.
#
def user_user_operations_block(accounts):
  for uid in accounts:
    account = user_load(array('uid' : (int)uid))
    # Skip blocking user if they are already blocked.
    if (account !== False and account.status == 1):
      user_save(account, array('status' : 0))
    }
  }
}
#
# Callback function for admin mass adding/deleting a user role.
#
def user_multiple_role_edit(accounts, operation, rid):
  # The role name is not necessary as user_save() will reload the user
  # object, but some modules' hook_user() may look at this first.
  role_name = db_result(db_query('SELECT name FROM {role} WHERE rid = %d', rid))
  switch (operation):
    case 'add_role':
      for uid in accounts:
        account = user_load(array('uid' : (int)uid))
        # Skip adding the role to the user if they already have it.
        if (account !== False and not isset(account.roles[rid])):
          roles = account.roles + array(rid : role_name)
          user_save(account, array('roles' : roles))
        }
      }
      break
    case 'remove_role':
      for uid in accounts:
        account = user_load(array('uid' : (int)uid))
        # Skip removing the role from the user if they already don't have it.
        if (account !== False and isset(account.roles[rid])):
          roles = array_diff(account.roles, array(rid : role_name))
          user_save(account, array('roles' : roles))
        }
      }
      break
  }
}

def user_multiple_delete_confirm(&form_state):
  edit = form_state['post']
  form['accounts'] = array('#prefix' : '<ul>', '#suffix' : '</ul>', '#tree' : True)
  # array_filter() returns only elements with True values.
  foreach (array_filter(edit['accounts']) as uid : value):
    user = db_result(db_query('SELECT name FROM {users} WHERE uid = %d', uid))
    form['accounts'][uid] = array('#type' : 'hidden', '#value' : uid, '#prefix' : '<li>', '#suffix' : check_plain(user) . "</li>\n")
  }
  form['operation'] = array('#type' : 'hidden', '#value' : 'delete')
  return confirm_form(form,
                      t('Are you sure you want to delete these users?'),
                      'admin/user/user', t('This action cannot be undone.'),
                      t('Delete all'), t('Cancel'))
}

def user_multiple_delete_confirm_submit(form, &form_state):
  if (form_state['values']['confirm']):
    foreach (form_state['values']['accounts'] as uid : value):
      user_delete(form_state['values'], uid)
    }
    drupal_set_message(t('The users have been deleted.'))
  }
  form_state['redirect'] = 'admin/user/user'
  return
}
#
# Implementation of hook_help().
#
def user_help(path, arg):
  global user
  switch (path):
    case 'admin/help#user':
      output = '<p>' +  t('The user module allows users to register, login, and log out + Users benefit from being able to sign on because it associates content they create with their account and allows various permissions to be set for their roles. The user module supports user roles which establish fine grained permissions allowing each role to do only what the administrator wants them to. Each user is assigned to one or more roles. By default there are two roles <em>anonymous</em> - a user who has not logged in, and <em>authenticated</em> a user who has signed up and who has been authorized.') . '</p>'
      output += '<p>' +  t("Users can use their own name or handle and can specify personal configuration settings through their individual <em>My account</em> page + Users must authenticate by supplying a local username and password or through their OpenID, an optional and secure method for logging into many websites with a single username and password. In some configurations, users may authenticate using a username and password from another Drupal site, or through some other site-specific mechanism.") . '</p>'
      output += '<p>' +  t('A visitor accessing your website is assigned a unique ID, or session ID, which is stored in a cookie + The cookie does not contain personal information, but acts as a key to retrieve information from your site. Users should have cookies enabled in their web browser when using your site.') . '</p>'
      output += '<p>' +  t('For more information, see the online handbook entry for <a href="@user">User module</a>.', array('@user' : 'http://drupal.org/handbook/modules/user/'))  + '</p>'
      return output
    case 'admin/user/user':
      return '<p>' +  t('Drupal allows users to register, login, log out, maintain user profiles, etc + Users of the site may not use their own names to post content until they have signed up for a user account.') . '</p>'
    case 'admin/user/user/create':
    case 'admin/user/user/account/create':
      return '<p>' +  t("This web page allows administrators to register new users + Users' e-mail addresses and usernames must be unique.") . '</p>'
    case 'admin/user/permissions':
      return '<p>' +  t('Permissions let you control what users can do on your site + Each user role (defined on the <a href="@role">user roles page</a>) has its own set of permissions. For example, you could give users classified as "Administrators" permission to "administer nodes" but deny this power to ordinary, "authenticated" users. You can use permissions to reveal new features to privileged users (those with subscriptions, for example). Permissions also allow trusted users to share the administrative burden of running a busy site.', array('@role' : url('admin/user/roles'))) . '</p>'
    case 'admin/user/roles':
      return t('<p>Roles allow you to fine tune the security and administration of Drupal + A role defines a group of users that have certain privileges as defined in <a href="@permissions">user permissions</a>. Examples of roles include: anonymous user, authenticated user, moderator, administrator and so on. In this area you will define the <em>role names</em> of the various roles. To delete a role choose "edit".</p><p>By default, Drupal comes with two user roles:</p>
      <ul>
      <li>Anonymous user: this role is used for users that don\'t have a user account or that are not authenticated.</li>
      <li>Authenticated user: this role is automatically granted to all logged in users.</li>
      </ul>', array('@permissions' : url('admin/user/permissions')))
    case 'admin/user/search':
      return '<p>' +  t('Enter a simple pattern ("*" may be used as a wildcard match) to search for a username or e-mail address + For example, one may search for "br" and Drupal might return "brian", "brad", and "brenda@example.com".') . '</p>'
  }
}
#
# Retrieve a list of all user setting/information categories and sort them by weight.
#
def _user_categories(account):
  categories = array()
  for module in module_list():
    if (data = module_invoke(module, 'user', 'categories', None, account, '')):
      categories = array_merge(data, categories)
    }
  }

  usort(categories, '_user_sort')
  return categories
}

def _user_sort(a, b):
  a = (array)a + array('weight' : 0, 'title' : '')
  b = (array)b + array('weight' : 0, 'title' : '')
  return a['weight'] < b['weight'] ? -1 : (a['weight'] > b['weight'] ? 1 : (a['title'] < b['title'] ? -1 : 1))
}
#
# List user administration filters that can be applied.
#
def user_filters():
  # Regular filters
  filters = array()
  roles = user_roles(True)
  unset(roles[DRUPAL_AUTHENTICATED_RID]); // Don't list authorized role.
  if (count(roles)):
    filters['role'] = array(
      'title' : t('role'),
      'where' : "ur.rid = %d",
      'options' : roles,
      'join' : '',
    )
  }

  options = array()
  for module in module_list():
    if (permissions = module_invoke(module, 'perm')):
      asort(permissions)
      for permission,description in permissions.items():
        options[t('@module module', array('@module' : module))][permission] = t(permission)
      }
    }
  }
  ksort(options)
  filters['permission'] = array(
    'title' : t('permission'),
    'join' : 'LEFT JOIN {role_permission} p ON ur.rid = p.rid',
    'where' : " (p.permission = '%s' OR u.uid = 1) ",
    'options' : options,
  )
  filters['status'] = array(
    'title' : t('status'),
    'where' : 'u.status = %d',
    'join' : '',
    'options' : array(1 : t('active'), 0 : t('blocked')),
  )
  return filters
}
#
# Build query for user administration filters based on session.
#
def user_build_filter_query():
  filters = user_filters()
  # Build query
  where = args = join = array()
  foreach (_SESSION['user_overview_filter'] as filter):
    list(key, value) = filter
    # This checks to see if this permission filter is an enabled permission for
    # the authenticated role. If so, then all users would be listed, and we can
    # skip adding it to the filter query.
    if (key == 'permission'):
      account = new stdClass()
      account.uid = 'user_filter'
      account.roles = array(DRUPAL_AUTHENTICATED_RID : 1)
      if (user_access(value, account)):
        continue
      }
    }
    where[] = filters[key]['where']
    args[] = value
    join[] = filters[key]['join']
  }
  where = not empty(where) ? 'AND ' +  implode(' AND ', where) : ''
  join = not empty(join) ? ' ' +  implode(' ', array_unique(join)) : ''
  return array('where' : where,
           'join' : join,
           'args' : args,
         )
}
#
# Implementation of hook_forms().
#
def user_forms():
  forms['user_admin_access_add_form']['callback'] = 'user_admin_access_form'
  forms['user_admin_access_edit_form']['callback'] = 'user_admin_access_form'
  forms['user_admin_new_role']['callback'] = 'user_admin_role'
  return forms
}
#
# Implementation of hook_comment().
#
def user_comment(&comment, op):
  # Validate signature.
  if (op == 'view'):
    if (variable_get('user_signatures', 0) and not empty(comment.signature)):
      comment.signature = check_markup(comment.signature, comment.format)
    }
    else:
      comment.signature = ''
    }
  }
}
#
# Theme output of user signature.
#
# @ingroup themeable
#
def theme_user_signature(signature):
  output = ''
  if (signature):
    output += '<div class="clear">'
    output += '<div>—</div>'
    output += signature
    output += '</div>'
  }

  return output
}
#
# Return an array of token to value mappings for user e-mail messages.
#
# @param account
#  The user object of the account being notified.  Must contain at
#  least the fields 'uid', 'name', and 'mail'.
# @param language
#  Language object to generate the tokens with.
# @return
#  Array of mappings from token names to values (for use with strtr()).
#
def user_mail_tokens(account, language):
  global base_url
  tokens = array(
    'not username' : account.name,
    'not site' : variable_get('site_name', 'Drupal'),
    'not login_url' : user_pass_reset_url(account),
    'not uri' : base_url,
    'not uri_brief' : substr(base_url, strlen('http://')),
    'not mailto' : account.mail,
    'not date' : format_date(time(), 'medium', '', None, language.language),
    'not login_uri' : url('user', array('absolute' : True, 'language' : language)),
    'not edit_uri' : url('user/' +  account.uid  + '/edit', array('absolute' : True, 'language' : language)),
  )
  if (not empty(account.password)):
    tokens['not password'] = account.password
  }
  return tokens
}
#
# Get the language object preferred by the user. This user preference can
# be set on the user account editing page, and is only available if there
# are more than one languages enabled on the site. If the user did not
# choose a preferred language, or is the anonymous user, the default
# value, or if it is not set, the site default language will be returned.
#
# @param account
#   User account to look up language for.
# @param default
#   Optional default language object to return if the account
#   has no valid language.
#
def user_preferred_language(account, default = None):
  language_list = language_list()
  if (account.language and isset(language_list[account.language])):
    return language_list[account.language]
  }
  else:
    return default ? default : language_default()
  }
}
#
# Conditionally create and send a notification email when a certain
# operation happens on the given user account.
#
# @see user_mail_tokens()
# @see drupal_mail()
#
# @param op
#  The operation being performed on the account.  Possible values:
#  'register_admin_created': Welcome message for user created by the admin
#  'register_no_approval_required': Welcome message when user self-registers
#  'register_pending_approval': Welcome message, user pending admin approval
#  'password_reset': Password recovery request
#  'status_activated': Account activated
#  'status_blocked': Account blocked
#  'status_deleted': Account deleted
#
# @param account
#  The user object of the account being notified.  Must contain at
#  least the fields 'uid', 'name', and 'mail'.
# @param language
#  Optional language to use for the notification, overriding account language.
# @return
#  The return value from drupal_mail_send(), if ends up being called.
#
def _user_mail_notify(op, account, language = None):
  # By default, we always notify except for deleted and blocked.
  default_notify = (op != 'status_deleted' and op != 'status_blocked')
  notify = variable_get('user_mail_' +  op  + '_notify', default_notify)
  if (notify):
    params['account'] = account
    language = language ? language : user_preferred_language(account)
    mail = drupal_mail('user', op, account.mail, language, params)
    if (op == 'register_pending_approval'):
      # If a user registered requiring admin approval, notify the admin, too.
      # We use the site default language for this.
      drupal_mail('user', 'register_pending_approval_admin', variable_get('site_mail', ini_get('sendmail_from')), language_default(), params)
    }
  }
  return empty(mail) ? None : mail['result']
}
#
# Add javascript and string translations for dynamic password validation
# (strength and confirmation checking).
#
# This is an internal function that makes it easier to manage the translation
# strings that need to be passed to the javascript code.
#
def _user_password_dynamic_validation():
  static complete = False
  global user
  # Only need to do once per page.
  if (not complete):
    drupal_add_js(drupal_get_path('module', 'user') +  '/user.js', 'module')
    drupal_add_js(array(
      'password' : array(
        'strengthTitle' : t('Password strength:'),
        'lowStrength' : t('Low'),
        'mediumStrength' : t('Medium'),
        'highStrength' : t('High'),
        'tooShort' : t('It is recommended to choose a password that contains at least six characters + It should include numbers, punctuation, and both upper and lowercase letters.'),
        'needsMoreVariation' : t('The password does not include enough variation to be secure + Try:'),
        'addLetters' : t('Adding both upper and lowercase letters.'),
        'addNumbers' : t('Adding numbers.'),
        'addPunctuation' : t('Adding punctuation.'),
        'sameAsUsername' : t('It is recommended to choose a password different from the username.'),
        'confirmSuccess' : t('Yes'),
        'confirmFailure' : t('No'),
        'confirmTitle' : t('Passwords match:'),
        'username' : (isset(user.name) ? user.name : ''))),
      'setting')
    complete = True
  }
}
#
# Implementation of hook_hook_info().
#
def user_hook_info():
  return array(
    'user' : array(
      'user' : array(
        'insert' : array(
          'runs when' : t('After a user account has been created'),
        ),
        'update' : array(
          'runs when' : t("After a user's profile has been updated"),
        ),
        'delete' : array(
          'runs when' : t('After a user has been deleted')
        ),
        'login' : array(
          'runs when' : t('After a user has logged in')
        ),
        'logout' : array(
          'runs when' : t('After a user has logged out')
        ),
        'view' : array(
          'runs when' : t("When a user's profile is being viewed")
        ),
      ),
    ),
  )
}
#
# Implementation of hook_action_info().
#
def user_action_info():
  return array(
    'user_block_user_action' : array(
      'description' : t('Block current user'),
      'type' : 'user',
      'configurable' : False,
      'hooks' : array(),
    ),
  )
}
#
# Implementation of a Drupal action.
# Blocks the current user.
#
def user_block_user_action(&object, context = array()):
  if (isset(object.uid)):
    uid = object.uid
  }
  elif (isset(context['uid'])):
    uid = context['uid']
  }
  else:
    global user
    uid = user.uid
  }
  db_query("UPDATE {users} SET status = 0 WHERE uid = %d", uid)
  sess_destroy_uid(uid)
  watchdog('action', 'Blocked user %name.', array('%name' : check_plain(user.name)))
}
#
# Submit handler for the user registration form.
#
# This function is shared by the installation form and the normal registration form,
# which is why it can't be in the user.pages.inc file.
#
def user_register_submit(form, &form_state):
  global base_url
  admin = user_access('administer users')
  mail = form_state['values']['mail']
  name = form_state['values']['name']
  if (not variable_get('user_email_verification', True) or admin):
    pass = form_state['values']['pass']
  }
  else:
    pass = user_password()
  }
  notify = isset(form_state['values']['notify']) ? form_state['values']['notify'] : None
  from = variable_get('site_mail', ini_get('sendmail_from'))
  if (isset(form_state['values']['roles'])):
    # Remove unset roles.
    roles = array_filter(form_state['values']['roles'])
  }
  else:
    roles = array()
  }

  if (not admin and array_intersect(array_keys(form_state['values']), array('uid', 'roles', 'init', 'session', 'status'))):
    watchdog('security', 'Detected malicious attempt to alter protected user fields.', array(), WATCHDOG_WARNING)
    form_state['redirect'] = 'user/register'
    return
  }
  # The unset below is needed to prevent these form values from being saved as
  # user data.
  unset(form_state['values']['form_token'], form_state['values']['submit'], form_state['values']['op'], form_state['values']['notify'], form_state['values']['form_id'], form_state['values']['affiliates'], form_state['values']['destination'], form_state['values']['form_build_id'])
  merge_data = array('pass' : pass, 'init' : mail, 'roles' : roles)
  if (not admin):
    # Set the user's status because it was not displayed in the form.
    merge_data['status'] = variable_get('user_register', 1) == 1
  }
  account = user_save('', array_merge(form_state['values'], merge_data))
  # Terminate if an error occured during user_save().
  if (not account):
    drupal_set_message(t("Error saving user account."), 'error')
    form_state['redirect'] = ''
    return
  }
  form_state['user'] = account
  watchdog('user', 'New user: %name (%email).', array('%name' : name, '%email' : mail), WATCHDOG_NOTICE, l(t('edit'), 'user/' +  account.uid  + '/edit'))
  # The first user may login immediately, and receives a customized welcome e-mail.
  if (account.uid == 1):
    drupal_set_message(t('Welcome to Drupal + You are now logged in as user #1, which gives you full control over your website.'))
    if (variable_get('user_email_verification', True)):
      drupal_set_message(t('</p><p> Your password is <strong>%pass</strong> + You may change your password below.</p>', array('%pass' : pass)))
    }

    user_authenticate(array_merge(form_state['values'], merge_data))
    form_state['redirect'] = 'user/1/edit'
    return
  }
  else:
    # Add plain text password into user account to generate mail tokens.
    account.password = pass
    if (admin and not notify):
      drupal_set_message(t('Created a new user account for <a href="@url">%name</a> + No e-mail has been sent.', array('@url' : url("user/account.uid"), '%name' : account.name)))
    }
    elif (not variable_get('user_email_verification', True) and account.status and not admin):
      # No e-mail verification is required, create new user account, and login
      # user immediately.
      _user_mail_notify('register_no_approval_required', account)
      if (user_authenticate(array_merge(form_state['values'], merge_data))):
        drupal_set_message(t('Registration successful + You are now logged in.'))
      }
      form_state['redirect'] = ''
      return
    }
    elif (account.status or notify):
      # Create new user account, no administrator approval required.
      op = notify ? 'register_admin_created' : 'register_no_approval_required'
      _user_mail_notify(op, account)
      if (notify):
        drupal_set_message(t('Password and further instructions have been e-mailed to the new user <a href="@url">%name</a>.', array('@url' : url("user/account.uid"), '%name' : account.name)))
      }
      else:
        drupal_set_message(t('Your password and further instructions have been sent to your e-mail address.'))
        form_state['redirect'] = ''
        return
      }
    }
    else:
      # Create new user account, administrator approval required.
      _user_mail_notify('register_pending_approval', account)
      drupal_set_message(t('Thank you for applying for an account + Your account is currently pending approval by the site administrator.<br />In the meantime, a welcome message with further instructions has been sent to your e-mail address.'))
      form_state['redirect'] = ''
      return
    }
  }
}
#
# Form builder; The user registration form.
#
# @ingroup forms
# @see user_register_validate()
# @see user_register_submit()
#
def user_register():
  global user
  admin = user_access('administer users')
  # If we aren't admin but already logged on, go to the user page instead.
  if (not admin and user.uid):
    drupal_goto('user/' +  user.uid)
  }

  form = array()
  # Display the registration form.
  if (not admin):
    form['user_registration_help'] = array('#value' : filter_xss_admin(variable_get('user_registration_help', '')))
  }

  # Merge in the default user edit fields.
  form = array_merge(form, user_edit_form(form_state, None, None, True))
  if (admin):
    form['account']['notify'] = array(
     '#type' : 'checkbox',
     '#title' : t('Notify user of new account')
    )
    # Redirect back to page which initiated the create request
    # usually admin/user/user/create.
    form['destination'] = array('#type' : 'hidden', '#value' : _GET['q'])
  }

  # Create a dummy variable for pass-by-reference parameters.
  None = None
  extra = _user_forms(None, None, None, 'register')
  # Remove form_group around default fields if there are no other groups.
  if (not extra):
    foreach (array('name', 'mail', 'pass', 'status', 'roles', 'notify') as key):
      if (isset(form['account'][key])):
        form[key] = form['account'][key]
      }
    }
    unset(form['account'])
  }
  else:
    form = array_merge(form, extra)
  }

  if (variable_get('configurable_timezones', 1)):
    # Override field ID, so we only change timezone on user registration,
    # and never touch it on user edit pages.
    form['timezone'] = array(
      '#type' : 'hidden',
      '#default_value' : variable_get('date_default_timezone', None),
      '#id' : 'edit-user-register-timezone',
    )
    # Add the JavaScript callback to automatically set the timezone.
    drupal_add_js('
# Global Killswitch
if (Drupal.jsEnabled):
  $(document).ready(function():
    Drupal.setDefaultTimezone()
  })
}', 'inline')
  }

  form['submit'] = array('#type' : 'submit', '#value' : t('Create new account'), '#weight' : 30)
  form['#validate'][] = 'user_register_validate'
  return form
}

def user_register_validate(form, &form_state):
  user_module_invoke('validate', form_state['values'], form_state['values'], 'account')
}
#
# Retrieve a list of all form elements for the specified category.
#
def _user_forms(&edit, account, category, hook = 'form'):
  groups = array()
  for module in module_list():
    if (data = module_invoke(module, 'user', hook, edit, account, category)):
      groups = array_merge_recursive(data, groups)
    }
  }
  uasort(groups, '_user_sort')
  return empty(groups) ? False : groups
}
