#!/usr/bin/env python
# $Id: session.inc,v 1.50 2008/08/12 10:28:33 dries Exp $

"""
  User session handling functions.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/session.inc
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-05-25
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

def open_(save_path, session_name):
  return True

def close():
  return True

def read(key):
  global user
  # Write and Close handlers are called after destructing objects
  # since PHP 5.0.5
  # Thus destructors can use sessions but session handler can't use objects.
  # So we are moving session closure before destructing objects.
  register_shutdown_function('session_write_close')
  # Handle the case of first time visitors and clients that don't
  # store cookies (eg. web crawlers).
  if (not php.isset(_COOKIE, php.session_name())):
    user = drupal_anonymous_user()
    return ''
  # Otherwise, if the session is still active, we have a record of 
  # the client's session in the database.
  user = db_fetch_object(db_query("SELECT u.*, s.* FROM {users} u " + \
    "INNER JOIN {sessions} s ON u.uid = s.uid WHERE s.sid = '%s'", key))
  # We found the client's session record and they are an authenticated user
  if (user and user.uid > 0):
    # This is done to unserialize the data member of user
    user = drupal_unpack(user)
    # Add roles element to user
    user.roles = array()
    user.roles[DRUPAL_AUTHENTICATED_RID] = 'authenticated user'
    result = db_query("SELECT r.rid, r.name FROM {role} r " + 
      "INNER JOIN {users_roles} ur ON ur.rid = r.rid WHERE ur.uid = %d", \
      user.uid)
    while True:
      role = db_fetch_object(result)
      if role == None:
        break
      user.roles[role.rid] = role.name
  # We didn't find the client's record (session has expired), or they are an anonymous user.
  else:
    session = (user.session if php.isset(user.session) else '')
    user = drupal_anonymous_user(session)
  return user.session



def write(key, value):
  global user
  # If saving of session data is disabled or if the client
  # doesn't have a session,
  # and one isn't being created ($value), do nothing.
  # This keeps crawlers out of
  # the session table. This reduces memory and server load,
  # and gives more useful
  # statistics. We can't eliminate anonymous session table rows
  # without breaking
  # the "Who's Online" block.
  if (not session_save_session() or \
      (php.empty(php.COOKIE[php.session_name()]) and php.empty(value))):
    return True
  result = db_result(db_query("SELECT COUNT(*) FROM {sessions} " + \
    "WHERE sid = '%s'", key))
  lib_database.query(\
    "UPDATE {sessions} SET " + \
    "uid = %d, cache = %d, hostname = '%s', " + \
    "session = '%s', timestamp = %d WHERE sid = '%s'", \
    user.uid, (user.cache if php.isset(user.cache) else ''), \
    ip_address(), value, php.time_(), key)
  if (lib_database.affected_rows()):
    # Last access time is updated no more frequently than once every 180 seconds.
    # This reduces contention in the users table.
    if (user.uid and drupy_time() - user.access > \
        variable_get('session_write_interval', 180)):
      db_query("UPDATE {users} SET access = %d WHERE uid = %d", \
        php.time_(), user.uid)
  else:
    # If this query fails, another parallel request probably got here first.
    # In that case, any session data generated in this request is discarded.
    lib_databae.query(\
      "INSERT INTO {sessions} " + \
      "(sid, uid, cache, hostname, session, timestamp) " + \
      "VALUES ('%s', %d, %d, '%s', '%s', %d)", \
      key, user.uid, (user.cache if php.isset(user.cache) else ''), \
      ip_address(), value, php.time_())
  return True



def regenerate():
  """
   Called when an anonymous user becomes authenticated or vice-versa.
  """
  old_session_id = session_id()
  session_regenerate_id()
  db_query("UPDATE {sessions} SET sid = '%s' WHERE sid = '%s'", \
    session_id(), old_session_id)


def count(timestamp = 0, anonymous = True):
  """
   Counts how many users have sessions. Can count either anonymous 
   sessions, authenticated sessions, or both.
  
   @param int timestamp
     A Unix timestamp representing a point of time in the past.
     The default is 0, which counts all existing sessions.
   @param boolean anonymous
     True counts only anonymous users.
     False counts only authenticated users.
   @return  int
     The number of users with sessions.
  """
  query = (' AND uid = 0' if anonymous else ' AND uid > 0')
  return db_result(db_query('SELECT COUNT(sid) AS count FROM {sessions} ' + \
    'WHERE timestamp >= %d' +  query, timestamp))


def destroy_sid(sid):
  """
   Called by PHP session handling with the PHP session ID to
   end a user's session.
  
   @param  string sid
     the session id
  """
  db_query("DELETE FROM {sessions} WHERE sid = '%s'", sid)



def destroy_uid(uid):
  """
   End a specific user's session
  
   @param  string uid
     the user id
  """
  db_query('DELETE FROM {sessions} WHERE uid = %d', uid)




def gc(lifetime):
  # Be sure to adjust 'php_value session.gc_maxlifetime' to a large enough
  # value. For example, if you want user sessions to stay in your database
  # for three weeks before deleting them, you need to set gc_maxlifetime
  # to '1814400'. At that value, only after a user doesn't log in after
  # three weeks (1814400 seconds) will his/her session be removed.
  db_query("DELETE FROM {sessions} WHERE timestamp < %d", time() - lifetime)
  return True



def save_session(status = None):
  """
   Determine whether to save session data of the current request.
  
   This function allows the caller to temporarily disable
   writing of session data,
   should the request end while performing potentially dangerous
   operations, such as
   manipulating the global user object.
   See http://drupal.org/node/218104 for usage
  
   @param status
     Disables writing of session data when False,
     (re-)enables writing when True.
   @return
     False if writing session data has been disabled. Otherwise, True.
  """
  php.static(session_save_session, 'save_session', True)
  if status != None:
    session_save_session.save_session = status
  return session_save_session.save_session

#
# Aliases
#
sess_name = php.session_name





