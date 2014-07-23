#!/usr/bin/env python
import icalendar as ical
import re
import calendergenerator
import mwclient


cal = ical.Calendar()
cal.add('version', '2.0')
cal.add('prodid', '-//willenbot')
cal.add('x-wr-calname', 'Stratum 0')

site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")
termine = site.Pages["Termine"]
	
entries = calendergenerator.parse_wiki_page(termine.edit())

for entry in entries:
	cal.add_component(entry.getIcal())

print cal.to_ical()