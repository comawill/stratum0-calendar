#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
import config
import calendargenerator
import os
import requests

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]
comment = None
entries = calendargenerator.parse_wiki_page(termine.edit())
expanded_entries = calendargenerator.expand_dates(entries)

def update(entries, page, purge_page, templatefile, lang):
	global comment
	page_data = site.Pages[page]
	old = page_data.edit()
	text = calendargenerator.generate_wiki_section(entries, templatefile, lang)
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
		if config.write_wiki:
			page_data.save(text, comment, minor=True)
			try:
				site.Pages[purge_page].purge()
			except mwclient.errors.HTTPRedirectError:
				pass
		else:
			print "no write"

update(expanded_entries, "Template:Termine/de", "Hauptseite", os.path.join(os.path.dirname(__file__), "templates/termine_haupt.de.wiki"), calendargenerator.LANG_DE)
update(expanded_entries, "Template:Termine/en", "English", os.path.join(os.path.dirname(__file__), "templates/termine_haupt.en.wiki"), calendargenerator.LANG_EN)
update(expanded_entries, "Template:Termine/fr", u"Français", os.path.join(os.path.dirname(__file__), "templates/termine_haupt.fr.wiki"), calendargenerator.LANG_FR)

calendargenerator.generate_ical(entries, config.ical)
calendargenerator.generate_json_css(expanded_entries, config.json, config.css)