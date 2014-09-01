#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import mwclient
import datetime
import time
# pip install git+git://github.com/mwclient/mwclient.git
import calendergenerator

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")

termine = site.Pages["Termine"]
data = termine.edit()
#data = file("tests/2014.txt").read().decode("utf8")
parsed = calendergenerator.parse_wiki_page(data)

print calendergenerator.generate_wiki_section(parsed, "templates/termine_haupt.de.wiki", "de_de")
print "-"*20
print calendergenerator.generate_wiki_section(parsed, "templates/termine_haupt.en.wiki", "en_us")
print "-"*20
print calendergenerator.generate_wiki_section(parsed, "templates/termine_haupt.fr.wiki", "fr_fr")