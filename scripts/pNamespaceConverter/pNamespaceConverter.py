#!/usr/bin/env python


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The drupal project can be found at http://drupal.org
# @file pNamespaceConverter
#  This should be run after an initial php2py conversion to bring the PHP
#  functions into a namespace
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-06-19
# @version 0.1
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


import re
import sys
from lib.drupy import DrupyPHP

f = open(sys.argv[1], 'r+')
data = f.read()

for k,v in vars(DrupyPHP).items():
  t = type(v).__name__
  # Module
  if (t == 'module'):
    continue
  # Function
  elif (t == 'function'):
    pat = r'(?<![a-zA-Z0-9_\.])(%s)(?=\()' % k
  # Variable
  else:
    pat = r'(?<![a-zA-Z0-9_\.])(%s)(?![a-zA-Z])' % k
  rep = r'p.\1'
  data = re.sub(pat, rep, data)


f.truncate(0)
f.seek(0)
f.write(data)
f.close()

print "Success"


