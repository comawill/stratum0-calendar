# -.- coding: utf8 -.-

import unittest
import calendergenerator as cg
class TestSomeStuff(unittest.TestCase):
	def test_DayOfWeek(self):
		self.assertEqual(cg.day_of_week_str(1, "de_DE"), "Di")
		self.assertEqual(cg.day_of_week_str(1, "en_US"), "Tue")
		self.assertEqual(cg.day_of_week_str(1, "fr_FR"), "Mar")
	
	def test_to(self):
		self.assertEqual(cg.to_in_lang("de_DE"), "bis")
		self.assertEqual(cg.to_in_lang("en_US"), "to")
		self.assertEqual(cg.to_in_lang("en_EN"), "to")
		self.assertEqual(cg.to_in_lang("fr_FR"), u"à")
		

