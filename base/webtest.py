#!/usr/bin/env python

import os
from beaker import session

sess = session.SessionObject(os.environ, type='file', data_dir='/tmp/cookies')._session()

if not sess.has_key('foo'):
  sess['foo'] = 1
else:
  sess['foo'] += 1
sess.save()

print sess.cookie
print "Content-Type: text/plain\r\n\r\n"
print "Page Loaded."
print sess
