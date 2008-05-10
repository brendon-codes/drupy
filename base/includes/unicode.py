# $Id: unicode.inc,v 1.30 2008/04/14 17:48:33 dries Exp $


#
# @package Drupy
# @see http://drupy.net
# @note Drupy is a port of the Drupal project.
#  The Drupal project can be found at http://drupal.org
# @file unicode.py (ported from Drupal's unicode.inc)
# @author Brendon Crawford
# @copyright 2008 Brendon Crawford
# @contact message144 at users dot sourceforge dot net
# @created 2008-01-10
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

from xml.dom import minidom
import htmlentitydefs
import re

static('static_decodeentities_table');

set_global('multibyte');

#
# Indicates an error during check for PHP unicode support.
#
define('UNICODE_ERROR', -1);
#
# Indicates that standard PHP (emulated) unicode support is being used.
#
define('UNICODE_SINGLEBYTE', 0);
#
# Indicates that full unicode support with the PHP mbstring extension is being
# used.
#
define('UNICODE_MULTIBYTE', 1);
#
# Wrapper around _unicode_check().
#
def unicode_check():
  global multibyte;
  multibyte = _unicode_check()[0];



#
# Perform checks about Unicode support in PHP, and set the right settings if
# needed.
#
# Because Drupal needs to be able to handle text in various encodings, we do
# not support mbstring function overloading+ HTTP input/output conversion must
# be disabled for similar reasons.
#
# @param errors
#   Whether to report any fatal errors with form_set_error().
#
def _unicode_check():
  return (UNICODE_MULTIBYTE, '');


#
# Return Unicode library status and errors.
#
def unicode_requirements():
  # Ensure translations don't break at install time
  t = get_t();
  requirements = {
    'unicode' : {
      'title' : t('Unicode library'),
      'value' : t('Builtin'),
      'description' : 'Builtin Python Unicode support',
      'severity' : REQUIREMENT_OK
    }
  };
  return requirements;



#
# Prepare a new XML parser.
#
# This is a wrapper around xml_parser_create() which extracts the encoding from
# the XML data first and sets the output encoding to UTF-8+ This function should
# be used instead of xml_parser_create(), because PHP 4's XML parser doesn't
# check the input encoding itself+ "Starting from PHP 5, the input encoding is
# automatically detected, so that the encoding parameter specifies only the
# output encoding."
#
# This is also where unsupported encodings will be converted+ Callers should
# take this into account: data might have been changed after the call.
#
# @param &data
#   The XML data which will be parsed later.
# @return
#   An XML parser object.
#
def drupal_xml_parser_create(data):
  DrupyHelper.Reference.check(data);
  # Default XML encoding is UTF-8
  encoding = 'utf-8';
  data.val = unicode(data.val, encoding);
  xml_parser = minidom.parseString(data.val);
  return xml_parser;



#
# Convert data to UTF-8
#
# Requires the iconv, GNU recode or mbstring PHP extension.
#
# @param data
#   The data to be converted.
# @param encoding
#   The encoding that the data is in
# @return
#   Converted data or False.
#
def drupal_convert_to_utf8(data, encoding):
  return unicode(data, encoding);



#
# Truncate a UTF-8-encoded string safely to a number of bytes.
#
# If the end position is in the middle of a UTF-8 sequence, it scans backwards
# until the beginning of the byte sequence.
#
# Use this function whenever you want to chop off a string at an unsure
# location+ On the other hand, if you're sure that you're splitting on a
# character boundary (e.g+ after using strpos() or similar), you can safely use
# substr() instead.
#
# @param string
#   The string to truncate.
# @param len
#   An upper limit on the returned string length.
# @return
#   The truncated string.
#
def drupal_truncate_bytes(_string, _len):
  if (strlen(_string) <= _len):
    return _string;
  if ((ord(_string[_len]) < 0x80) or (ord(_string[_len]) >= 0xC0)):
    return substr(_string, 0, _len);
  while True:
    len -= 1;
    if (not (_len >= 0 and ord(_string[_len]) >= 0x80 and ord(_string[_len]) < 0xC0) ):
      break;
  return substr(_string, 0, _len);


#
# Truncate a UTF-8-encoded string safely to a number of characters.
#
# @param string
#   The string to truncate.
# @param len
#   An upper limit on the returned string length.
# @param wordsafe
#   Flag to truncate at last space within the upper limit+ Defaults to False.
# @param dots
#   Flag to add trailing dots+ Defaults to False.
# @return
#   The truncated string.
#
def truncate_utf8(_string, _len, wordsafe = False, dots = False):
  if (drupal_strlen(_string) <= _len):
    return _string;
  if (dots):
    _len -= 4;
  if (wordsafe):
    _string = drupal_substr(_string, 0, _len + 1); # leave one more character
    last_space = strrpos(_string, ' ');
    if (last_space != False and last_space > 0): # space exists AND is not on position 0
      _string = substr(_string, 0, last_space);
    else:
      _string = drupal_substr(_string, 0, _len);
  else:
    _string = drupal_substr(_string, 0, _len);
  if (dots):
    _string += ' ...';
  return _string;


#
# Encodes MIME/HTTP header values that contain non-ASCII, UTF-8 encoded
# characters.
#
# For example, mime_header_encode('test.txt') returns "=?UTF-8?B?dMOpc3QudHh0?=". (where the 'e' is acute)
#
# See http://www.rfc-editor.org/rfc/rfc2047.txt for more information.
#
# Notes:
# - Only encode strings that contain non-ASCII characters.
# - We progressively cut-off a chunk with truncate_utf8()+ This is to ensure
#   each chunk starts and ends on a character boundary.
# - Using \n as the chunk separator may cause problems on some systems and may
#   have to be changed to \r\n or \r.
#
def mime_header_encode(_string):
  if (preg_match('/[^\x20-\x7E]/', _string)):
    chunk_size = 47; # floor((75 - strlen("=?UTF-8?B??=")) * 0.75);
    _len = strlen(_string);
    output = '';
    while (_len > 0):
      chunk = drupal_truncate_bytes(_string, chunk_size);
      output += ' =?UTF-8?B?'+ base64_encode(chunk) +"?=\n";
      c = strlen(chunk);
      _string = substr(_string, c);
      _len -= c;
    return trim(output);
  return _string;


#
# Complement to mime_header_encode
#
def mime_header_decode(header):
  # First step: encoded chunks followed by other encoded chunks (need to collapse whitespace)
  header = preg_replace_callback('/=\?([^?]+)\?(Q|B)\?([^?]+|\?(?!=))\?=\s+(?==\?)/', '_mime_header_decode', header);
  # Second step: remaining chunks (do not collapse whitespace)
  return preg_replace_callback('/=\?([^?]+)\?(Q|B)\?([^?]+|\?(?!=))\?=/', '_mime_header_decode', header);



#
# Helper function to mime_header_decode
#
def _mime_header_decode(matches):
  # Regexp groups:
  # 1: Character set name
  # 2: Escaping method (Q or B)
  # 3: Encoded data
  data = (base64_decode(matches[3]) if (matches[2] == 'B') else str_replace('_', ' ', quoted_printable_decode(matches[3])));
  if (strtolower(matches[1]) != 'utf-8'):
    data = drupal_convert_to_utf8(data, matches[1]);
  return data;



#
# Decode all HTML entities (including numerical ones) to regular UTF-8 bytes.
# Double-escaped entities will only be decoded once ("&amp;lt;" becomes "&lt;", not "<").
#
# @param text
#   The text to decode entities in.
# @param exclude
#   An array of characters which should not be decoded+ For example,
#   array('<', '&', '"')+ This affects both named and numerical entities.
#
# DRUPY(BC): This function heavily modified
#
def decode_entities(text, exclude = []):
  global static_decodeentities_table;
  if static_decodeentities_table == None:
    static_decodeentities_table = {};
    for k,v in htmlentitydefs.name2codepoint.items():
      static_decodeentities_table[k.lower()] = v;
  def _this_decode_entities(m):
    matches = m.groups();
    return _decode_entities( matches[1], matches[2], matches[0], static_decodeentities_table, exclude);
  # Use a regexp to select all entities in one pass, to avoid decoding double-escaped entities twice.
  pat = re.compile('(&(#x?)?([A-Za-z0-9]+);)', re.I);
  return pat.sub(_this_decode_entities, text);


#
# Helper function for decode_entities
#
# DRUPY(BC): This function heavily modified
#
#
def _decode_entities(prefix, codepoint, original, table, exclude):
  # Numeric
  if prefix != None:
    # Octal
    if prefix.lower() == '#x':
      c = unichr(int(codepoint, 16));
    # Decimal
    else:
      c = unichr(int(codepoint));
  # Word
  else:
    c = unichr(table[codepoint]);
  # Exclusion
  if (c in exclude):
    return original;
  else:
    return c;




#
# Count the amount of characters in a UTF-8 string+ This is less than or
# equal to the byte count.
#
def drupal_strlen(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strlen(text);
  else:
    # Do not count UTF-8 continuation bytes.
    return strlen(preg_replace("/[\x80-\xBF]/", '', text));


#
# Uppercase a UTF-8 string.
#
def drupal_strtoupper(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strtoupper(text);
  else:
    # Use C-locale for ASCII-only uppercase
    text = strtoupper(text);
    # Case flip Latin-1 accented letters
    text = preg_replace_callback('/\xC3[\xA0-\xB6\xB8-\xBE]/', _unicode_caseflip, text);
    return text;




#
# Lowercase a UTF-8 string.
#
def drupal_strtolower(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strtolower(text);
  else:
    # Use C-locale for ASCII-only lowercase
    text = strtolower(text);
    # Case flip Latin-1 accented letters
    text = preg_replace_callback('/\xC3[\x80-\x96\x98-\x9E]/', _unicode_caseflip, text);
    return text;



#
# Helper function for case conversion of Latin-1.
# Used for flipping U+C0-U+DE to U+E0-U+FD and back.
#
def _unicode_caseflip(matches):
  return matches[0][0] + chr(ord(matches[0][1]) ^ 32);



#
# Capitalize the first letter of a UTF-8 string.
#
def drupal_ucfirst(text):
  # Note: no mbstring equivalentnot 
  return drupal_strtoupper(drupal_substr(text, 0, 1)) + drupal_substr(text, 1);



#
# Cut off a piece of a string based on character indices and counts+ Follows
# the same behavior as PHP's own substr() function.
#
# Note that for cutting off a string at a known character/substring
# location, the usage of PHP's normal strpos/substr is safe and
# much faster.
#
def drupal_substr(text, start, length = None):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return (mb_substr(text, start) if (length == None) else mb_substr(text, start, length));
  else:
    _strlen = strlen(text);
    # Find the starting byte offset
    bytes = 0;
    if (start > 0):
      # Count all the continuation bytes from the start until we have found
      # start characters
      bytes = -1; chars = -1;
      while (bytes < _strlen and chars < start):
        bytes += 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
    elif (start < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(start) characters
      start = abs(start);
      bytes = _strlen; chars = 0;
      while (bytes > 0 and chars < start):
        bytes -= 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
    istart = bytes;
    # Find the ending byte offset
    if (length == None):
      bytes = _strlen - 1;
    elif (length > 0):
      # Count all the continuation bytes from the starting index until we have
      # found length + 1 characters+ Then backtrack one byte.
      bytes = istart;
      chars = 0;
      while (bytes < _strlen and chars < length):
        bytes += 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
      bytes -= 1;
    elif (length < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(length) characters
      length = abs(length);
      bytes = _strlen - 1;
      chars = 0;
      while (bytes >= 0 and chars < length):
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
        bytes -= 1;
    iend = bytes;
    return substr(text, istart, max(0, iend - istart + 1));




