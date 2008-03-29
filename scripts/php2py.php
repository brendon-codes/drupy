#!/usr/bin/env php
<?PHP

$data = file_get_contents($_SERVER['argv'][1]);

//Do conversions
$data = p2p_null($data);
$data = p2p_false($data);
$data = p2p_true($data);
$data = p2p_and($data);
$data = p2p_or($data);
$data = p2p_funcs($data);
$data = p2p_comments_1($data);
$data = p2p_comments_2($data);
$data = p2p_comments_3($data);
$data = p2p_vars($data);
$data = p2p_dots($data);
$data = p2p_hashassign($data);

//write output
fwrite(STDOUT, $data);

function p2p_null($data) {
 $pat = "/null/i";
 $rep = "None";
 return preg_replace($pat, $rep, $data);
}

function p2p_false($data) {
 $pat = "/false/i";
 $rep = "False";
 return preg_replace($pat, $rep, $data);
}

function p2p_true($data) {
 $pat = "/true/i";
 $rep = "True";
 return preg_replace($pat, $rep, $data);
}

function p2p_and($data) {
 $pat = "/&&/i";
 $rep = "and";
 return preg_replace($pat, $rep, $data);
}

function p2p_or($data) {
 $pat = "/\|\|/i";
 $rep = "or";
 return preg_replace($pat, $rep, $data);
}

function p2p_comments_1($data) {
 $pat = "|^\s*\*/?|im";
 $rep = "#";
 return preg_replace($pat, $rep, $data);
}

function p2p_comments_2($data) {
 $pat = "|^\s*/\*+|im";
 $rep = "#";
 return preg_replace($pat, $rep, $data);
}

function p2p_comments_3($data) {
 $pat = "|^(\s*)//|im";
 $rep = "\\1#";
 return preg_replace($pat, $rep, $data);
}

function p2p_funcs($data) {
 $pat = "/^(\s*)function\s+([a-z_])/im";
 $rep = "\\1def \\2";
 return preg_replace($pat, $rep, $data);
}

function p2p_vars($data) {
 $pat = "/(?<!->)\\$(\w+)/i";
 $rep = "\\1";
 return preg_replace($pat, $rep, $data);
}

function p2p_dots($data) {
 $pat = "/->/";
 $rep = ".";
 return preg_replace($pat, $rep, $data);
}

function p2p_hashassign($data) {
 $pat = "/=>/";
 $rep = ":";
 return preg_replace($pat, $rep, $data);
}

?>