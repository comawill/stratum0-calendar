# -.- coding: utf8 -.-

import unittest
import calendargenerator as cg


class TestSomeStuff(unittest.TestCase):
	def test_DayOfWeek(self):
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_DE), "Di")
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_EN), "Tue")
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_FR), "Mar")

	def test_to(self):
		self.assertEqual(cg.to_in_lang(cg.LANG_DE), "bis")
		self.assertEqual(cg.to_in_lang(cg.LANG_EN), "to")
		self.assertEqual(cg.to_in_lang("wrong string"), "--")
		self.assertEqual(cg.to_in_lang(cg.LANG_FR), u"à")


class TestUserInputError(unittest.TestCase):
	def test_wrong_date(self):
		content = """ == <context> ==
		| some party || 22.05.2015 - 20.05.2015 ||
		| some party || 22.05.2015 - 21.05.2015 ||
		| some party || 22.05.2015 20:00 - 22.05.2015 03:00 ||
		| some party || 22.05.2015 20:00 - 03:00 ||
		"""
		result = cg.parse_wiki_page(content)
		for entry in result:
			self.assertLessEqual(entry.start_datetime(), entry.end_datetime())
		self.assertEqual(len(result), 1)
