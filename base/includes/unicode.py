#!/usr/bin/env python

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

from lib.drupy import DrupyPHP as p
from xml.dom import minidom
import htmlentitydefs
import re


#
# Globals
#
multibyte = None

#
# Indicates an error during check for PHP unicode support.
#
UNICODE_ERROR = -1

#
# Indicates that standard PHP (emulated) unicode support is being used.
#
UNICODE_SINGLEBYTE = 0

#
# Indicates that full unicode support with the PHP mbstring extension is being
# used.
#
UNICODE_MULTIBYTE = 1

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
  p.Reference.check(data);
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
def drupal_truncate_bytes(string_, len_):
  if (strlen(string_) <= len_):
    return string_;
  if ((ord(string_[len_]) < 0x80) or (ord(string_[len_]) >= 0xC0)):
    return substr(string_, 0, len_);
  while True:
    len -= 1;
    if (not (len_ >= 0 and ord(string_[len_]) >= 0x80 and ord(string_[len_]) < 0xC0) ):
      break;
  return substr(string_, 0, len_);


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
def truncate_utf8(string_, len_, wordsafe = False, dots = False):
  if (drupal_strlen(string_) <= len_):
    return string_;
  if (dots):
    len_ -= 4;
  if (wordsafe):
    string_ = drupal_substr(string_, 0, len_ + 1); # leave one more character
    last_space = strrpos(string_, ' ');
    if (last_space != False and last_space > 0): # space exists AND is not on position 0
      string_ = substr(string_, 0, last_space);
    else:
      string_ = drupal_substr(string_, 0, len_);
  else:
    string_ = drupal_substr(string_, 0, len_);
  if (dots):
    string_ += ' ...';
  return string_;


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
def mime_header_encode(string_):
  if (preg_match('/[^\x20-\x7E]/', string_)):
    chunk_size = 47; # floor((75 - strlen("=?UTF-8?B??=")) * 0.75);
    len_ = strlen(string_);
    output = '';
    while (len_ > 0):
      chunk = drupal_truncate_bytes(string_, chunk_size);
      output += ' =?UTF-8?B?'+ base64_encode(chunk) +"?=\n";
      c = strlen(chunk);
      string_ = substr(string_, c);
      len_ -= c;
    return trim(output);
  return string_;


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
  static(decode_entities, 'table', {})
  if empty(decode_entities.table):
    for k,v in htmlentitydefs.name2codepoint.items():
      decode_entities.table[k.lower()] = v;
  def _this_decode_entities(m):
    matches = m.groups();
    return _decode_entities( matches[1], matches[2], matches[0], decode_entities.table, exclude);
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
    strlen_ = strlen(text);
    # Find the starting byte offset
    bytes = 0;
    if (start > 0):
      # Count all the continuation bytes from the start until we have found
      # start characters
      bytes = -1; chars = -1;
      while (bytes < strlen_ and chars < start):
        bytes += 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
    elif (start < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(start) characters
      start = abs(start);
      bytes = strlen_; chars = 0;
      while (bytes > 0 and chars < start):
        bytes -= 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
    istart = bytes;
    # Find the ending byte offset
    if (length == None):
      bytes = strlen_ - 1;
    elif (length > 0):
      # Count all the continuation bytes from the starting index until we have
      # found length + 1 characters+ Then backtrack one byte.
      bytes = istart;
      chars = 0;
      while (bytes < strlen_ and chars < length):
        bytes += 1;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
      bytes -= 1;
    elif (length < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(length) characters
      length = abs(length);
      bytes = strlen_ - 1;
      chars = 0;
      while (bytes >= 0 and chars < length):
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars += 1;
        bytes -= 1;
    iend = bytes;
    return substr(text, istart, max(0, iend - istart + 1));




