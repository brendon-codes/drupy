

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


def get_import(filename):
  name = filename.replace('/', '.')
  mod = __import__(name)
  components = name.split('.')
  for comp in components[1:]:
      mod = getattr(mod, comp)
  return mod



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
