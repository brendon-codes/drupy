#!/usr/bin/env python

"""
  Converts inc_* to lib* for modules

  @package pNamespaceConverter
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-07-08
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


import re
import sys
import os

prefix_find = 'inc_'
prefix_replace = 'lib_'

f = open(sys.argv[1], 'r+')
data = f.read()

i = os.listdir('includes')
for v in i:
  name, ext = v.split('.')
  if ext != 'py':
    continue
  pat = r'(?<![a-zA-Z0-9_\.])%s%s(?![a-zA-Z])' % (prefix_find,name)
  rep = r'%s%s' % (prefix_replace,name)
  data = re.sub(pat, rep, data)

f.truncate(0)
f.seek(0)
f.write(data)
f.close()

print "Success: %s" % sys.argv[1]


