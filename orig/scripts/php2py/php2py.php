#!/usr/bin/env php
<?PHP
# $Id: bootstrap.inc,v 1.208 2008/04/14 17:48:33 dries Exp $

/**
 * @package Drupy
 * @see http://drupy.net
 * @note Drupy is a port of the Drupal project.
 *  The drupal project can be found at http://drupal.org
 * @file php2py.php
 *  Helps convert PHP syntax to python
 * @author Brendon Crawford
 * @copyright 2008 Brendon Crawford
 * @contact message144 at users dot sourceforge dot net
 * @created 2008-01-10
 * @version 0.1
 * @license: 
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 */


$rules = array(
  // semicolon
  array(
    "/;\s*$/im",
    ""
  ),
  // brace open
  array(
    "/(\)|else)\s*\{/i",
    "\\1:"
  ),
  // not
  array(
    "/!(?!=)/i",
    "not "
  ),
  //triple equals
  array(
    "/===/",
    "=="
  ),
  // comments 1
  array(
    "|^\s*\*/?|im",
    "#"
  ),
  // comments 2
  array(
    "|^\s*/\*+|im",
    "#"
  ),
  // comments 3
  array(
    "|^(\s*)//|im",
    "\\1#"
  ),
  //concat equals
  array(
    "/\.=/",
    "+="
  ),
  // concat pre
  array(
    "/^(\s*)([^#]+?)(\S)\s+\.(?![\f\t\040]*[\r\n])/im",
    "\\1\\2\\3 + "
  ),
  //concat post
  array(
    "/^(\s*)([^#]+?)\.[\f\t\040]+(\S)/im",
    "\\1\\2 + \\3"
  ),
  // elseif
  array(
    "/else\s*if/i",
    "elif"
  ),
  // null
  array(
    "/null/i",
    "None"
  ),
  // false
  array(
    "/false/i",
    "False"
  ),
  // true
  array(
    "/true/i",
    "True"
  ),
  // and
  array(
    "/&&/i",
    "and"
  ),
  // or
  array(
    "/\|\|/i",
    "or"
  ),
  // funcs
  array(
    "/^(\s*)function\s+([a-z_])/im",
    "\\1def \\2"
  ),
  // vars
  array(
    "/(?<!->)\\$(\w+)/i",
    "\\1"
  ),
  // dots
  array(
    "/->/",
    "."
  ),
  // foreach key,val
  array(
    "/foreach\s*\(\s*([a-z0-9\(\)\._]+)\s+as\s+([a-z0-9_]+)\s*=>\s*([a-z0-9_]+)\s*\)/i",
    "for \\2,\\3 in \\1.items()"
  ),
  // foreach
  array(
    "/foreach\s*\(\s*([a-z0-9\(\)\._]+)\s+as\s+([a-z0-9_]+)\s*\)/i",
    "for \\2 in \\1"
  ),
  // hash
  array(
    "/=>/",
    ":"
  )
);


$data = file_get_contents($_SERVER['argv'][1]);
foreach ($rules as $rule) $data = preg_replace($rule[0], $rule[1], $data);
fwrite(STDOUT, $data);

?>
