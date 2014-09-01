# -.- coding: utf8 -.-

import unittest
import calendergenerator as cg
class TestSomeStuff(unittest.TestCase):
	def test_DayOfWeek(self):
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_DE), "Di")
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_EN), "Tue")
		self.assertEqual(cg.day_of_week_str(1, cg.LANG_FR), "Mar")
	
	def test_to(self):
		self.assertEqual(cg.to_in_lang(cg.LANG_DE), "bis")
		self.assertEqual(cg.to_in_lang(cg.LANG_EN), "to")
		self.assertEqual(cg.to_in_lang(cg.LANG_FR), u"à")
		

