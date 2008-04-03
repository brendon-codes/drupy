#!/usr/bin/env php
<?PHP

$rules = array(
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
  // concat pre
  array(
    "/(\S)\s+\./i",
    "\\1 +"
  ),
  //concat post
  array(
    "/\.\s+(\S)/i",
    "+ \\1"
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