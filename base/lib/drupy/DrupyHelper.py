

#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file DrupyHelper.py
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-02-27
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

import os
import cgi


#
# Converts a filename to import path
# @param filename
# @return Str
#
def import_file(filename):
  name = filename.replace('/', '.')
  if name[-3:] == '.py':
    name = name[:-3]
  mod = __import__(name, globals(), locals(), ['*'], -1)
  return mod


#
# Debug HTTP output message
# @param Str data
#
def output(should_die, *data):
  print "Content-Type: text/plain; Charset=UTF-8;\r\n\r\n"
  print data
  if should_die:
    exit()
  else:
    return True


#
# Reference class
#
class Reference:
  def __init__(self):
    self.val = None
  #
  # Enforces a reference
  # @param Object data
  # @raise Exception 
  # @return Bool
  #
  @staticmethod
  def check(data):
    if not isinstance(data, Reference) or not hasattr(data, 'val'):
      raise Exception, "Argument must be an object and must contain a 'val' property."
    else:
      return True




