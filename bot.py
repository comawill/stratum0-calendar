#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
import config
# pip install git+git://github.com/mwclient/mwclient.git
import calendergenerator

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]
hauptseite = site.Pages["Hauptseite"]

entries = calendergenerator.parse_wiki_page(termine.edit())

old = hauptseite.edit(section=2)
text = calendergenerator.generate_wiki_section(entries)

if old != text:
	rev = termine.revisions(limit = 1, prop = 'timestamp|user|comment').next()
	changed = datetime.datetime.fromtimestamp(time.mktime(rev["timestamp"]))
	now = datetime.datetime.utcnow()
	comment = u"Automatisches Update (irgendwas wird sich schon verändert haben)"
	if now-changed < datetime.timedelta(minutes=15):
		comment = u"%s hat Termine aktualisiert (%s) " % (rev["user"] ,rev["comment"])
	print "update!"
	print comment.encode("utf8")
	print
	print text.encode("utf8")
	
	site.login(config.user, config.password)
	hauptseite.save(text, comment, minor=True)