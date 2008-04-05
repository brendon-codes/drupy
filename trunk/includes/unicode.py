# Id: unicode.inc,v 1.29 2007/12/28 12:02:50 dries Exp $

from xml.dom import minidom


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
  multibyte ,= _unicode_check();



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
# For example, mime_header_encode('tést.txt') returns "=?UTF-8?B?dMOpc3QudHh0?=".
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
def mime_header_encode(string):
  if (preg_match('/[^\x20-\x7E]/', string)):
    chunk_size = 47; // floor((75 - strlen("=?UTF-8?B??=")) * 0.75);
    len = strlen(string);
    output = '';
    while (len > 0):
      chunk = drupal_truncate_bytes(string, chunk_size);
      output += ' =?UTF-8?B?'+ base64_encode(chunk) +"?=\n";
      c = strlen(chunk);
      string = substr(string, c);
      len -= c;
    }
    return trim(output);
  }
  return string;
}
#
# Complement to mime_header_encode
#
def mime_header_decode(header):
  # First step: encoded chunks followed by other encoded chunks (need to collapse whitespace)
  header = preg_replace_callback('/=\?([^?]+)\?(Q|B)\?([^?]+|\?(?!=))\?=\s+(?==\?)/', '_mime_header_decode', header);
  # Second step: remaining chunks (do not collapse whitespace)
  return preg_replace_callback('/=\?([^?]+)\?(Q|B)\?([^?]+|\?(?!=))\?=/', '_mime_header_decode', header);
}
#
# Helper function to mime_header_decode
#
def _mime_header_decode(matches):
  # Regexp groups:
  # 1: Character set name
  # 2: Escaping method (Q or B)
  # 3: Encoded data
  data = (matches[2] == 'B') ? base64_decode(matches[3]) : str_replace('_', ' ', quoted_printable_decode(matches[3]));
  if (strtolower(matches[1]) != 'utf-8'):
    data = drupal_convert_to_utf8(data, matches[1]);
  }
  return data;
}
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
def decode_entities(text, exclude = array()):
  static table;
  # We store named entities in a table for quick processing.
  if (not isset(table)):
    # Get all named HTML entities.
    table = array_flip(get_html_translation_table(HTML_ENTITIES));
    # PHP gives us ISO-8859-1 data, we need UTF-8.
    table = array_map('utf8_encode', table);
    # Add apostrophe (XML)
    table['&apos;'] = "'";
  }
  newtable = array_diff(table, exclude);

  # Use a regexp to select all entities in one pass, to avoid decoding double-escaped entities twice.
  return preg_replace('/&(#x?)?([A-Za-z0-9]+);/e', '_decode_entities("1", "2", "0", newtable, exclude)', text);
}
#
# Helper function for decode_entities
#
def _decode_entities(prefix, codepoint, original, &table, &exclude):
  # Named entity
  if (not prefix):
    if (isset(table[original])):
      return table[original];
    }
    else:
      return original;
    }
  }
  # Hexadecimal numerical entity
  if (prefix == '#x'):
    codepoint = base_convert(codepoint, 16, 10);
  }
  # Decimal numerical entity (strip leading zeros to avoid PHP octal notation)
  else:
    codepoint = preg_replace('/^0+/', '', codepoint);
  }
  # Encode codepoint as UTF-8 bytes
  if (codepoint < 0x80):
    str = chr(codepoint);
  }
  elif (codepoint < 0x800):
    str = chr(0xC0 | (codepoint >> 6)) + chr(0x80 | (codepoint & 0x3F));
  }
  elif (codepoint < 0x10000):
    str = chr(0xE0 | ( codepoint >> 12)) + chr(0x80 | ((codepoint >> 6) & 0x3F)) + chr(0x80 | ( codepoint       & 0x3F));
  }
  elif (codepoint < 0x200000):
    str = chr(0xF0 | ( codepoint >> 18)) + chr(0x80 | ((codepoint >> 12) & 0x3F)) + chr(0x80 | ((codepoint >> 6)  & 0x3F)) + chr(0x80 | ( codepoint        & 0x3F));
  }
  # Check for excluded characters
  if (in_array(str, exclude)):
    return original;
  }
  else:
    return str;
  }
}
#
# Count the amount of characters in a UTF-8 string+ This is less than or
# equal to the byte count.
#
def drupal_strlen(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strlen(text);
  }
  else:
    # Do not count UTF-8 continuation bytes.
    return strlen(preg_replace("/[\x80-\xBF]/", '', text));
  }
}
#
# Uppercase a UTF-8 string.
#
def drupal_strtoupper(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strtoupper(text);
  }
  else:
    # Use C-locale for ASCII-only uppercase
    text = strtoupper(text);
    # Case flip Latin-1 accented letters
    text = preg_replace_callback('/\xC3[\xA0-\xB6\xB8-\xBE]/', '_unicode_caseflip', text);
    return text;
  }
}
#
# Lowercase a UTF-8 string.
#
def drupal_strtolower(text):
  global multibyte;
  if (multibyte == UNICODE_MULTIBYTE):
    return mb_strtolower(text);
  }
  else:
    # Use C-locale for ASCII-only lowercase
    text = strtolower(text);
    # Case flip Latin-1 accented letters
    text = preg_replace_callback('/\xC3[\x80-\x96\x98-\x9E]/', '_unicode_caseflip', text);
    return text;
  }
}
#
# Helper function for case conversion of Latin-1.
# Used for flipping U+C0-U+DE to U+E0-U+FD and back.
#
def _unicode_caseflip(matches):
  return matches[0][0] + chr(ord(matches[0][1]) ^ 32);
}
#
# Capitalize the first letter of a UTF-8 string.
#
def drupal_ucfirst(text):
  # Note: no mbstring equivalentnot 
  return drupal_strtoupper(drupal_substr(text, 0, 1)) + drupal_substr(text, 1);
}
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
    return length === None ? mb_substr(text, start) : mb_substr(text, start, length);
  }
  else:
    strlen = strlen(text);
    # Find the starting byte offset
    bytes = 0;
    if (start > 0):
      # Count all the continuation bytes from the start until we have found
      # start characters
      bytes = -1; chars = -1;
      while (bytes < strlen and chars < start):
        bytes++;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars++;
        }
      }
    }
    elif (start < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(start) characters
      start = abs(start);
      bytes = strlen; chars = 0;
      while (bytes > 0 and chars < start):
        bytes--;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars++;
        }
      }
    }
    istart = bytes;

    # Find the ending byte offset
    if (length === None):
      bytes = strlen - 1;
    }
    elif (length > 0):
      # Count all the continuation bytes from the starting index until we have
      # found length + 1 characters+ Then backtrack one byte.
      bytes = istart; chars = 0;
      while (bytes < strlen and chars < length):
        bytes++;
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars++;
        }
      }
      bytes--;
    }
    elif (length < 0):
      # Count all the continuation bytes from the end until we have found
      # abs(length) characters
      length = abs(length);
      bytes = strlen - 1; chars = 0;
      while (bytes >= 0 and chars < length):
        c = ord(text[bytes]);
        if (c < 0x80 or c >= 0xC0):
          chars++;
        }
        bytes--;
      }
    }
    iend = bytes;

    return substr(text, istart, max(0, iend - istart + 1));
  }
}


