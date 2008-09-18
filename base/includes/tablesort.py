#!/usr/bin/env python
# Id: tablesort.inc,v 1.48 2008/04/14 17:48:33 dries Exp 


"""
  Functions to aid in the creation of sortable tables.

  All tables created with a call to lib_theme.theme('table') have the option of having
  column headers that the user can click on to sort the table by that column.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/tablesort.inc
  @author Fernando P. Garcia
  @copyright 2008 Fernando P. Garcia
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

__version__ = "$Revision: 1 "

from lib.drupy import DrupyPHP as php
from includes import common as lib_common
from includes import unicode as lib_unicode
from includes import theme as lib_theme

def tablesort_init(header):
  """
   Initialize the table sort context.
  """
  ts = tablesort_get_order(header)
  ts['sort'] = tablesort_get_sort(header)
  ts['query_string'] = tablesort_get_querystring()
  return ts



def tablesort_sql(header, before = ''):
  """
   Create an SQL sort clause.

   This def produces the ORDER BY clause to insert in your SQL queries,
   assuring that the returned database table rows match the sort order chosen
   by the user.

   @param header
     An array of column headers in the format described in theme_table().
   @param before
     An SQL string to insert after ORDER BY and before the table sorting code.
     Useful for sorting by important attributes like "sticky" first.
   @return
     An SQL string to append to the end of a query.

   @ingroup database
  """
  ts = tablesort_init(header)
  if ts['sql']:
    # Based on code from db_escape_table(), but this can also contain a dot.
    field = php.php.preg_replace('/[^A-Za-z0-9_.]+/', '', ts['sql'])
    # Sort order can only be ASC or DESC.
    sort = lib_unicode.drupal_strtoupper(ts['sort'])
    sort = (sort if php.in_array(sort, ['ASC', 'DESC']) else '')
    return " ORDER BY before field sort"


def tablesort_header(cell, header, ts):
  """
   Format a column header.

   If the cell in question is the column header for the current sort criterion,
   it gets special formatting. All possible sort criteria become links.

   @param cell
     The cell to format.
   @param header
     An array of column headers in the format described in theme_table().
   @param ts
     The current table sort context as returned from tablesort_init().
   @return
     A properly formatted cell, ready for _theme_table_cell().
  """
  # Special formatting for the currently sorted column header.
  if php.is_array(cell) and php.isset(cell['field']):
    title = t('sort by @s', {'@s': cell['data']})
    if cell['data'] == ts['name']:
      ts['sort'] = ('desc' if (ts['sort'] == 'asc') else 'asc')
      if php.isset(cell['class']):
        cell['class'] += ' active'
      else:
        cell['class'] = 'active'
      image = lib_theme.theme('tablesort_indicator', ts['sort'])
    else:
      # If the user clicks a different header, we want to sort ascending initially.
      ts['sort'] = 'asc'
      image = ''
    if not php.empty(ts['query_string']):
      ts['query_string'] = '&' + ts['query_string']
    cell['data'] = l(
      cell['data'] + image, php.GET['q'], {
        'attributes':
          {
            'title': title,
            'query':
              'sort=' + ts['sort'] + '&order=' + rawurlencode(cell['data']) +
              ts['query_string'],
            'html': TRUE
          }
      }
    )
    php.unset(cell['field'], cell['sort'])
  return cell



def tablesort_cell(cell, header, ts, i):
  """
   Format a table cell.

   Adds a class attribute to all cells in the currently active column.

   @param cell
     The cell to format.
   @param header
     An array of column headers in the format described in theme_table().
   @param ts
     The current table sort context as returned from tablesort_init().
   @param i
     The index of the cell's table column.
   @return
     A properly formatted cell, ready for _theme_table_cell().
  """
  if php.isset(header[i]['data']) and header[i]['data'] == ts['name'] and not php.empty(header[i]['field']):
    if php.is_array(cell):
      if php.isset(cell['class']):
        cell['class'] += ' active'
      else:
        cell['class'] = 'active'
    else:
      cell = {'data': cell, 'class': 'active'}
  return cell



def tablesort_get_querystring():
  """
   Compose a query string to append to table sorting requests.

   @return
     A query string that consists of all components of the current page request
     except for those pertaining to table sorting.
  """
  return lib_common.drupal_query_string_encode(
    _REQUEST, php.array_merge(['q', 'sort', 'order'], php.array_keys(_COOKIE)))



def tablesort_get_order(headers):
  """
   Determine the current sort criterion.

   @param headers
     An array of column headers in the format described in theme_table().
   @return
     An associative array describing the criterion, containing the keys:
     - "name": The localized title of the table column.
     - "sql": The name of the database field to sort on.
  """
  order = php.GET['order'] if php.isset(php.GET['order']) else ''
  for header in headers:
    if php.isset(header['data']) and order == header['data']:
      return {
        'name': header['data'],
        'sql': header['field'] if php.isset(header['field']) else ''
      }
    if php.isset(header['sort']) and (header['sort'] == 'asc' or header['sort'] == 'desc'):
      default = {
        'name': header['data'],
        'sql': header['field'] if php.isset(header['field']) else ''
      }
  if php.isset(default):
    return default
  else:
    # The first column specified is initial 'order by' field unless otherwise specified
    if php.is_array(headers[0]):
      headers[0] += {'data': None, 'field': None}
      return {'name': headers[0]['data'], 'sql': headers[0]['field']}
    else:
      return {'name': headers[0]}



def tablesort_get_sort(headers):
  """
   Determine the current sort direction.

   @param headers
     An array of column headers in the format described in theme_table().
   @return
     The current sort direction ("asc" or "desc").
  """
  if php.isset(php.GET['sort']):
    return 'desc' if (php.GET['sort'] == 'desc')  else 'asc';
  # User has not specified a sort. Use default if specified; otherwise use "asc".
  else:
    for header in headers:
      if php.is_array(header) and php.array_key_exists('sort', header):
        return header['sort']
  return 'asc'

