import os
import sys
from django.conf.urls.defaults import *

plugins = []
apps = []

def default_apps():
    return [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites'
    ]


def find_apps():
    global plugins
    global apps
    plugins = []
    apps = default_apps()
    tmps = []
    dirs = os.listdir("%s/plugins" % os.getcwd())
    for d in dirs:
        f = "%s/plugins/%s" % (os.getcwd(), d)
        if os.path.isdir(f):
            apps.append("drupy.plugins.%s" % d)
            tmps.append(d)
    importers = __import__('plugins', globals, [], tmps)
    for t in tmps:
        plugins.append(getattr(importers, t))
    return True


def get_patterns():
    global plugins
    pats = []
    for p in plugins:
        if hasattr(p, 'hook_menu'):
            pat = getattr(p, 'hook_menu')()
            for hook_pat in pat:
                pats.append(hook_pat)
    pats = tuple(pats)
    return patterns('', *pats)


find_apps()
urlpatterns = get_patterns()
