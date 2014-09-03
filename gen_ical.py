#!/usr/bin/env python
import icalendar as ical
import re
import calendargenerator
import mwclient
import sys
import datetime

if __name__ == "__main__":
	cal = ical.Calendar()
	timezone = ical.cal.Timezone()
	timezone.add('TZID', 'Europe/Berlin')
	timezone.add('x-lic-location', 'Europe/Vienna')

	tzs = ical.TimezoneStandard()
	tzs.add('tzname', 'MEZ')
	tzs.add('dtstart', datetime.datetime(1996, 10, 27, 3, 0, 0))
	tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
	tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
	tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))
	
	tzd = ical.TimezoneDaylight()
	tzd.add('tzname', 'MESZ')
	tzd.add('dtstart', datetime.datetime(1981, 3, 29, 2, 0, 0))
	tzs.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
	tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
	tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

	timezone.add_component(tzs)
	timezone.add_component(tzd)
	cal.add_component(timezone)



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