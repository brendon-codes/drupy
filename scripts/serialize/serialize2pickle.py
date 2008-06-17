#!/usr/bin/env python


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file serialize2pickle.py
#  Converts Drupal php serialization fields to Python Pickle fields
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-06-17
# @version 0.1
# @depends PHPUnserialize.py
# @license: 
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import PHPUnserialize
from includes import bootstrap
from includes import database
from lib.drupy.DrupyPHP import *

bootstrap.drupal_bootstrap(bootstrap.DRUPAL_BOOTSTRAP_DATABASE)

tables = (
  {
    'select' : ("SELECT variable.value, variable.name FROM variable"),
    'update' : ("UPDATE variable SET variable.value = '%(value)s' WHERE variable.name = '%(name)s'")
  }
)

res = database.db_query("SELECT * FROM variable")
while True:
  r = database.db_fetch_object(res)
  if not r:
    break
  print r.value
