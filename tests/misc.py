# -.- coding: utf8 -.-

import unittest
import calendergenerator as cg
class TestSomeStuff(unittest.TestCase):
	def test_DayOfWeek(self):
		self.assertEqual(cg.day_of_week_str(1, "de_de"), "Di")
		self.assertEqual(cg.day_of_week_str(1, "en_us"), "Tue")
		self.assertEqual(cg.day_of_week_str(1, "fr_fr"), "Mar")
	
	def test_to(self):
		self.assertEqual(cg.to_in_lang("de_de"), "bis")
		self.assertEqual(cg.to_in_lang("en_us"), "to")
		self.assertEqual(cg.to_in_lang("en_en"), "to")
		self.assertEqual(cg.to_in_lang("fr_fr"), u"à")
		

