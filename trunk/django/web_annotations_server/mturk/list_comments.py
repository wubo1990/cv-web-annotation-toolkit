#!/usr/bin/python

import os
from optparse import OptionParser

usage = "usage: %prog -s SETTINGS | --settings=SETTINGS"
parser = OptionParser(usage)
parser.add_option('-s', '--settings', dest='settings', metavar='SETTINGS',
                  help="The Django settings module to use")
(options, args) = parser.parse_args()
if not options.settings:
    parser.error("You must specify a settings module")

os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

from mturk.models import *

for iT,T in enumerate(SubmittedTask.objects.filter(session=13)):
	print iT,T.get_parsed().comments
