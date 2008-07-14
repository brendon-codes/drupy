#!/usr/bin/env python

"""
 @package Drupy
 @see http://drupy.net
 @note Drupy is a port of the Drupal project.
  The Drupal project can be found at http://drupal.org
 @file serialize2pickle.py
  Converts Drupal php serialization fields to Python Pickle fields
 @author Brendon Crawford
 @copyright 2008 Brendon Crawford
 @contact message144 at users dot sourceforge dot net
 @created 2008-06-17
 @version 0.1
 @depends PHPUnserialize.py
 @license: 

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import PHPUnserialize
from includes import bootstrap as inc_bootstrap
from includes import database as inc_database
import pickle
import copy
from lib.drupy.DrupyPHP import *

#
# List of tables
#
tables = (
  {
    'select' : "SELECT system.info, system.name FROM system WHERE system.type = 'theme'",
    'update' : "UPDATE system SET system.info = '%(info)s' WHERE system.name = '%(name)s'",
    'key' : 'info'
  },
)

inc_bootstrap.drupal_bootstrap(inc_bootstrap.DRUPAL_BOOTSTRAP_DATABASE)
u = PHPUnserialize.PHPUnserialize()
i = 0

for t in tables:
  s_res = inc_database.db_query(t['select'])
  while True:
    s_row = inc_database.db_fetch_assoc(s_res)
    if not s_row:
      break
    try:
      udata = u.unserialize(s_row[t['key']])
    except PHPUnserialize.InvalidObject:
      continue
    out = copy.deepcopy(s_row)
    for ok,ov in out.items():
      if ok == t['key']:
        out[ok] = inc_database.db_escape_string(pickle.dumps(udata))
      else:
        out[ok] = inc_database.db_escape_string(ov)
    u_query = t['update'] % out
    inc_database.db_query(u_query)
    i += 1


print "%s records processed" % i
exit(0)
