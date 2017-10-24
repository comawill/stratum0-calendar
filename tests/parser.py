# -*- coding: utf8 -.-
import unittest
import calendargenerator as cg
import datetime


class TestUrls(unittest.TestCase):
	def setUp(self):
		pass

	def test_internUrlTitle(self):
		url_date = cg.SingleDate("abc [[test_url|test_title]]", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date.getPlainName(), "abc test_title")

	def test_internUrl(self):
		url_date = cg.SingleDate("abc [[test_url]]", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date.getPlainName(), "abc test_url")

	def test_internUmlautUrl(self):
		url_date = cg.SingleDate(u"[[test_ürl]]", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getURL(), u"https://stratum0.org/wiki/test_%C3%BCrl")
		self.assertEqual(url_date.getPlainName(), u"test_ürl")

		url_date2 = cg.SingleDate(u"[[test_ürlä]]", "cat", [20, 9, 2014])
		self.assertEqual(url_date2.getURL(), u"https://stratum0.org/wiki/test_%C3%BCrl%C3%A4")
		self.assertEqual(url_date2.getPlainName(), u"test_ürlä")

	def test_externUrl(self):
		url_date = cg.SingleDate("abc [https://stratum0.net/ title]", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.net/")
		self.assertEqual(url_date.getPlainName(), "abc title")

	def test_multiURL(self):
		url_date = cg.SingleDate("[https://events.ccc.de/congress/2014/ 31C3] ([https://events.ccc.de/congress/2014/wiki/Assembly:Stratum_0 Assembly])", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "31C3 (Assembly)")
		self.assertEqual(url_date.getURL(), "https://events.ccc.de/congress/2014/")

	def test_firstUrl(self):
		url_date = cg.SingleDate("abc [https://stratum0.net/ title] [[test_url|test_title]]", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.net/")
		self.assertEqual(url_date.getPlainName(), "abc title test_title")

		url_date2 = cg.SingleDate("abc [[test_url|test_title]] [https://stratum0.net/ title]", "cat", [20, 9, 2014])
		self.assertEqual(url_date2.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date2.getPlainName(), "abc test_title title")


class TestPlainName(unittest.TestCase):
	def setUp(self):
		pass

	def test_emph(self):
		url_date = cg.SingleDate("abc ''def''", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "abc def")

	def test_double_emph(self):
		url_date = cg.SingleDate("abc ''def'' ''ghi''", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "abc def ghi")

	def test_bold_emph(self):
		url_date = cg.SingleDate("abc '''def''' ''ghi''", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "abc def ghi")

	def test_bold(self):
		url_date = cg.SingleDate("abc '''def'''", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "abc def")

	def test_double_bold(self):
		url_date = cg.SingleDate("abc '''def''' '''ghi'''", "cat", [20, 9, 2014])
		self.assertEqual(url_date.getPlainName(), "abc def ghi")


class TestWikiParser(unittest.TestCase):
	def setUp(self):
		pass

	def test_parseWiki(self):
		now = cg.tz.localize(datetime.datetime(2014, 10, 10, 10, 10))
		result = cg.parse_wiki_page(open("tests/wiki/general.wiki").read())
		for entry in result:
			if isinstance(entry, cg.Generator):
				for subentry in entry.entries:
					self.assertLessEqual(subentry.start_datetime(), subentry.end_datetime())
			else:
				self.assertLessEqual(entry.start_datetime(), entry.end_datetime())

		cg.generate_wiki_section(cg.expand_dates(result), "templates/termine_haupt.de.wiki", cg.LANG_DE, now=now)
		cg.generate_ical(result, "/dev/null")
		self.assertEqual(len(result), 13)

	def test_parseWiki_wrongWeekday(self):
		now = cg.tz.localize(datetime.datetime(2014, 10, 10, 10, 10))
		result = cg.parse_wiki_page(open("tests/wiki/wrong_weekday.wiki").read())
		self.assertEqual(len(result), 1)
		self.assertEqual(len(cg.expand_dates(result)), 0)
		cg.generate_wiki_section(cg.expand_dates(result), "templates/termine_haupt.de.wiki", cg.LANG_DE, now=now)
		cg.generate_ical(result, "/dev/null")

	def test_parseWiki_wrongTime(self):
		now = cg.tz.localize(datetime.datetime(2014, 10, 10, 10, 10))
		result = cg.parse_wiki_page(open("tests/wiki/wrong_time.wiki").read())
		self.assertEqual(len(result), 1)
		cg.generate_wiki_section(cg.expand_dates(result), "templates/termine_haupt.de.wiki", cg.LANG_DE, now=now)
		cg.generate_ical(result, "/dev/null")
