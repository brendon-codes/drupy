#!/usr/bin/env python
# $Id: cache-install.inc,v 1.2 2007/08/07 08:39:35 goba Exp $

"""
  Stub of cache functions for use during installation

  A stub cache implementation to be used during the installation
  process when database access is not yet available. Because Drupal's
  caching system never requires that cached data be present, these
  stub functions can short-circuit the process and sidestep the
  need for any persistent storage. Obviously, using this cache
  implementation during normal operations would have a negative impact
  on performance.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/cache.inc
  @author Fernando P. García
  @copyright 2008 Fernando P. García
  @contact fernando at develcuy dot com
  @created 2008-09-18
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

def get(key, table = 'cache'):
  return FALSE



def set(cid, data, table = 'cache', expire = CACHE_PERMANENT, headers = NULL):
  return



def clear_all(cid = NULL, table = NULL, wildcard = FALSE):
  return



  
