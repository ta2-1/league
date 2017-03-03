#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import site
import sys

ALLDIRS = [
    '/home/taras/.virtualenvs/kortov-net/lib/python2.7/site-packages',
    '/home/taras/projects/kortov-net',
]

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add each new site-packages directory.
for directory in ALLDIRS:
    site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = []

for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

