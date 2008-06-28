#!/usr/bin/env python

# Id: language.inc,v 1.16 2008/04/14 17:48:33 dries Exp $

"""
  Multiple language handling functionality.

  @package includes
  @see <a href='http://drupy.net'>Drupy Homepage</a>
  @see <a href='http://drupal.org'>Drupal Homepage</a>
  @note Drupy is a port of the Drupal project.
  @note This file was ported from Drupal's includes/language.inc
  @author Brendon Crawford
  @copyright 2008 Brendon Crawford
  @contact message144 at users dot sourceforge dot net
  @created 2008-06-07
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

from lib.drupy import DrupyPHP as p
import bootstrap as inc_bootstrap


def language_initialize():
  """
    Choose a language for the page, based on language negotiation settings.
  """
  # Configured presentation language mode.
  mode = variable_get('language_negotiation', inc_bootstrap.LANGUAGE_NEGOTIATION_NONE)
  # Get a list of enabled languages.
  languages = inc_bootstrap.language_list('enabled')
  languages = languages[1]
  if mode == inc_bootstrap.LANGUAGE_NEGOTIATION_NONE:
    return language_default()
  elif mode == inc_bootstrap.LANGUAGE_NEGOTIATION_DOMAIN:
    for language in languages:
      parts = p.parse_url(language.domain)
      if (not p.empty(parts['host']) and (_SERVER['p.SERVER_NAME'] == parts['host'])):
        return language
    return language_default()
  elif mode == inc_bootstrap.LANGUAGE_NEGOTIATION_PATH_DEFAULT or \
      mode == inc_bootstrap.LANGUAGE_NEGOTIATION_PATH:
    # _GET['q'] might not be available at this time, because
    # path initialization runs after the language bootstrap phase.
    args =  (p.explode('/', _GET['q']) if p.isset(_GET, 'q') else [])
    prefix = p.array_shift(args)
    # Search prefix within enabled languages.
    for language in languages:
      if (not p.empty(language.prefix) and language.prefix == prefix):
        # Rebuild p.GET['q'] with the language removed.
        p.GET['q'] = p.implode('/', args)
        return language
    if (mode == LANGUAGE_NEGOTIATION_PATH_DEFAULT):
      # If we did not found the language by prefix, choose the default.
      return language_default()
  # User language.
  if (inc_bootstrap.user.uid and p.isset(languages[inc_bootstrap.user.language])):
    return languages[inc_bootstrap.user.language]
  # Browser accept-language parsing.
  language = language_from_browser()
  if (language):
    return language
  # Fall back on the default if everything else fails.
  return language_default()



def language_from_browser():
  """
   Identify language from the Accept-language HTTP p.header we got.
  """
  # Specified by the user via the browser's Accept Language setting
  # Samples: "hu, en-us;q=0.66, en;q=0.33", "hu,en-us;q=0.5"
  browser_langs = []
  if (p.isset(p.SERVER, 'HTTP_ACCEPT_LANGUAGE')):
    browser_accept = p.explode(",", p.SERVER['HTTP_ACCEPT_LANGUAGE'])
    for i in range(p.count(browser_accept)):
      # The language part is either a code or a code with a quality.
      # We cannot do anything with a * code, so it is skipped.
      # If the quality is missing, it is assumed to be 1 according to the RFC.
      if (p.preg_match("not ([a-z-]+)(;q=([0-9\\.]+))?not ", p.trim(browser_accept[i]), found)):
        browser_langs[found[1]] = (float(found[3]) if p.isset(found, 3) else 1.0)
  # Order the codes by quality
  arsort(browser_langs)
  # Try to find the first preferred language we have
  languages = language_list('enabled')
  for langcode,q in browser_langs.items():
    if (p.isset(languages['1'], langcode)):
      return languages['1'][langcode]



def language_url_rewrite(path, options):
  """
   Rewrite URL's with language based prefix. Parameters are the same
   as those of the url() function.
  """
  # Only modify relative (insite) URLs.
  if (not options['external']):
    # Language can be passed as an option, or we go for current language.
    if (not p.isset(options, 'language')):
      options['language'] = inc_bootstrap.language_
    lang_type = variable_get('language_negotiation', inc_bootstrap.LANGUAGE_NEGOTIATION_NONE)
    if lang_type == inc_bootstrap.LANGUAGE_NEGOTIATION_NONE:
      # No language dependent path allowed in this mode.
      del(options['language'])
      return
    elif lang_type == inc_bootstrap.LANGUAGE_NEGOTIATION_DOMAIN:
      if (options['language'].domain):
        # Ask for an absolute URL with our modified base_url.
        options['absolute'] = True
        options['base_url'] = options['language'].domain
      return
    elif lang_type == inc_bootstrap.LANGUAGE_NEGOTIATION_PATH_DEFAULT:
      default = language_default()
      if (options['language'].language == default.language):
        return
    if lang_type == inc_bootstrap.LANGUAGE_NEGOTIATION_PATH:
      if (not p.empty(options['language'].prefix)):
        options['prefix'] = options['language'].prefix +  '/'
      return



