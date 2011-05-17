#!/usr/bin/env python
# $Id: garland.info,v 1.6 2008/02/18 19:19:48 dries Exp $

"""
  Garland theme info file

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's themes/garland/garland.info
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-01-10
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

name = "Garland"
description = \
  "Tableless, recolorable, multi-column, fluid width theme (default)."
version = .1
core = "7.x"
engine = "drupytemplate"
stylesheets = {
  'all' : "style.css",
  'print' : "print.css"
}

