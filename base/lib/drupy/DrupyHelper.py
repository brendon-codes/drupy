#!/usr/bin/env python

"""
 @package Drupy
 @see http://drupy.net
 @note Drupy is a port of the Drupal project.
  The Drupal project can be found at http://drupal.org
 @file DrupyHelper.py
 @author Brendon Crawford
 @copyright 2008 Brendon Crawford
 @contact message144 at users dot sourceforge dot net
 @created 2008-02-27
 @version 0.1
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

import os
import cgi
import cgitb
import sys

def output(should_die, *data):
  """
   Debug HTTP output message
   @param data Str
  """
  print "Content-Type: text/plain; Charset=UTF-8;\r\n\r\n"
  print data
  if should_die:
    exit()
  else:
    return True

