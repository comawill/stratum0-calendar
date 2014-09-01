#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
import config
import calendergenerator

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]
comment = None
entries = calendergenerator.parse_wiki_page(termine.edit())

def update(entries, page, templatefile, lang):
	global comment
	page_data = site.Pages[page]
	old = page_data.edit()
	text = calendergenerator.generate_wiki_section(entries, templatefile, lang)
	if old != text:
		print "updating %s" % page
		if not comment:
			rev = termine.revisions(limit = 1, prop = 'timestamp|user|comment').next()
			changed = datetime.datetime.fromtimestamp(time.mktime(rev["timestamp"]))
			now = datetime.datetime.utcnow()
			comment = u"Automatisches Update (irgendwas wird sich schon verändert haben)"
			if now-changed < datetime.timedelta(minutes=15):
				comment = u"%s hat Termine aktualisiert (%s) " % (rev["user"] ,rev["comment"])
		print comment.encode("utf8")
		if not site.logged_in:
			site.login(config.user, config.password)
		page_data.save(text, comment, minor=True)

update(entries, "Template:Termine/de", "templates/termine_haupt.de.wiki", "de_DE")
update(entries, "Template:Termine/en", "templates/termine_haupt.en.wiki", "en_US")
update(entries, "Template:Termine/fr", "templates/termine_haupt.fr.wiki", "fr_CA")