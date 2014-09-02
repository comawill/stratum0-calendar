#!/usr/bin/env python
import icalendar as ical
import re
import calendargenerator
import mwclient
import sys

if __name__ == "__main__":
	cal = ical.Calendar()
	cal.add('version', '2.0')
	cal.add('prodid', '-//willenbot')
	cal.add('x-wr-calname', 'Stratum 0')

	site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")
	termine = site.Pages["Termine"]
		
	entries = calendargenerator.parse_wiki_page(termine.edit())

	for entry in entries:
		cal.add_component(entry.getIcal())

	if len(sys.argv) > 1:
		f = file(sys.argv[1], "w")
		f.write(cal.to_ical())
		f.close()
	else:
		print cal.to_ical()