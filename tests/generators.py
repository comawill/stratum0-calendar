import unittest
import calendargenerator as cg
import tempfile
import os
import datetime


class TestGenerators(unittest.TestCase):
	def setUp(self):
		self.tempdir = tempfile.gettempdir()
		self.json_path = os.path.join(self.tempdir, "events.json")
		self.css_path = os.path.join(self.tempdir, "events.css")
		self.ics_path = os.path.join(self.tempdir, "events.ics")
		self.events = [cg.SingleDate("Event", "cat", (10, 10, 2014)),
			cg.SingleDateTime("Event 2", "cat2", (10, 12, 2014, 12, 00)),
			cg.SingleDateTimeRange("Event 3", "cat2", (10, 12, 2014, 12, 00, 14, 00)),
			cg.DateRange("Event 4", "cat2", (10, 12, 2014, 4, 1, 2015)),
			cg.DateTimeRange("Event 5", "cat1", (10, 12, 2014, 12, 00, 12, 12, 2014, 13, 00)),
			cg.WeekdayTimeGenerator("Event 6b", "cat5e", ("Mo", 13, 15), "12.12.2014 - 4.2.2015"),
			cg.WeekdayTimeRangeGenerator("Event 6b", "cat5e", ("Mo", 13, 15, 15, 45), "12.12.2014 - 4.2.2015"),
			cg.WeekdayTimeGenerator("Event 6", "cat5e", ("Mo", 13, 15), "12.12.2014 - 13.12.2014"),
			cg.SingleDate("Event -1", "cat", (6, 10, 2014)),
			cg.SingleDate("Event -1", "cat", (7, 10, 2014))]

	def test_GenerateJsonCSS(self):
		cg.generate_json_css(cg.expand_dates(self.events), self.json_path, self.css_path)
		os.remove(self.json_path)
		os.remove(self.css_path)

	def test_GenerateIcal(self):
		cg.generate_ical(self.events, self.ics_path)
		os.remove(self.ics_path)

	def test_GenerateWiki(self):
		now = cg.tz.localize(datetime.datetime(2014, 10, 10, 10, 10))
		cg.generate_wiki_section(cg.expand_dates(self.events), "templates/termine_haupt.de.wiki", cg.LANG_DE, now=now)
