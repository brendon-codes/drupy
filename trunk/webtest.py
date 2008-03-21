#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable()
import os

print "Content-Type: text/plain\r\n\r\n"
print "<div>"
print "Page Loaded. Python CGI is working correctly."
print "</div>"
