#!/usr/bin/env python

from includes import bootstrap
from includes import database
from lib.drupy.DrupyPHP import *

bootstrap.drupal_bootstrap(bootstrap.DRUPAL_BOOTSTRAP_DATABASE)

res = database.db_query("SELECT * FROM variable")

print database.db_fetch_object(res).valu
