
#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file DrupyHelper.py
#  A PHP session abstraction layer for Python
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-05-25
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


#
# Sets user-level session storage functions
# @param Func open_
# @param Func close_
# @param Func read_
# @param Func write_
# @param Func destroy_
# @param Func gc_
# @return Bool
#
def session_set_save_handler(open_, close_, read_, write_, destroy_, gc_):
  pass


#
# Initialize session data
# @return Bool
#
def session_start():
  pass


#
# Get and/or set the current session name
# @param Str name
# @return Str
#
def session_name(name = "DrupySession"):
  pass


