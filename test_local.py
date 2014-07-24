#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
# pip install git+git://github.com/mwclient/mwclient.git
import calendergenerator

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]

parsed = calendergenerator.parse_wiki_page(termine.edit())

print calendergenerator.generate_wiki_section(parsed)