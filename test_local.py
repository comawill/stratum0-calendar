#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
import calendargenerator

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]
data = termine.edit()
#data = file("tests/2014.txt").read().decode("utf8")
parsed = calendargenerator.parse_wiki_page(data)

print calendargenerator.generate_wiki_section(parsed, "templates/termine_haupt.de.wiki", calendargenerator.LANG_DE)
print "-"*20
print calendargenerator.generate_wiki_section(parsed, "templates/termine_haupt.en.wiki", calendargenerator.LANG_EN)
print "-"*20
print calendargenerator.generate_wiki_section(parsed, "templates/termine_haupt.fr.wiki", calendargenerator.LANG_FR)