#!/usr/bin/env python

"""
  Dynamic import functions.

  @package drupy
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-06-27
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

import os
import cgi
import cgitb
import sys


def import_file(filename):
  """
   Converts a filename to import path
   @param filename
   @return Str
  """
  name = filename.replace('/', '.')
  if name[-3:] == '.py':
    name = name[:-3]
  mod = __import__(name, globals(), locals(), ['*'], -1)
  return mod


def getFunction(plugin_, function_):
  """
  Gets fiunction object from plugin
  
  @param plugin_ Module
  @param function_ Str
  @return Function
  """
  return getattr(plugin_, function_)



def exists(filename):
  """
    Checks for existance of drupy plugin
    
    @param filename Str
    @return Bool
  """
  return os.path.exists('%s/__init__.py' % filename)


def plugins():
  """
   Get loaded plugins
   @return List
  """
  mods = sys.modules
  out = {}
  for k,v in mods.items():
    if v is not None:
      out[k] = v
  return out




