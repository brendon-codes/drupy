import cgi
import cgitb; cgitb.enable()
import os

global _SERVER

_SERVER = os.environ