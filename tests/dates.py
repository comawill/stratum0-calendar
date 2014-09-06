import unittest
import calendargenerator as cg
import datetime

class TestDateOrder(unittest.TestCase):
	def setUp(self):
		self.datetime1 = cg.tz.localize(datetime.datetime(2010, 4, 1, 12, 22))
		self.datetime2 = cg.tz.localize(datetime.datetime(2020, 4, 1, 12, 22))

		self.sd1 = cg.SingleDate("name", "cat", [20,8,2014])
		self.sd2 = cg.SingleDate("name", "cat", [21,8,2014])
		self.sd3 = cg.SingleDate("name", "cat", [21,8,2014])

		self.sdt1 = cg.SingleDateTime("name", "cat", [22,8,2014,12,00])
		self.sdt2 = cg.SingleDateTime("name", "cat", [23,8,2014,14,00])
		
		self.sdt3 = cg.SingleDateTime("name", "cat", [20,8,2014,12,00])
		self.sdt4 = cg.SingleDateTime("name", "cat", [20,8,2014,15,00])
		
		self.sdtr1 = cg.SingleDateTimeRange("name", "cat", [24,8,2014,12,00, 14,00])
		self.sdtr2 = cg.SingleDateTimeRange("name", "cat", [24,9,2014,13,00, 15,00])
		
		self.sdtr3 = cg.SingleDateTimeRange("name", "cat", [24,8,2014,12,00, 14,00])
		self.sdtr4 = cg.SingleDateTimeRange("name", "cat", [24,8,2014,12,00, 15,00])

		self.dr1 = cg.DateRange("name", "cat", [20,8,2014,21,8,2014])
		self.dr2 = cg.DateRange("name", "cat", [20,9,2014,21,9,2014])
		
		self.dtr1 = cg.DateTimeRange("name", "cat", [20,8,2014,12,00, 21,8,2014,14,00])
		self.dtr2 = cg.DateTimeRange("name", "cat", [20,9,2014,13,00, 21,8,2014,15,00])

	def test_compareDatetime(self):
		self.assertTrue(self.sd1 > self.datetime1)
		self.assertTrue(self.sd1 >= self.datetime1)
		self.assertTrue(self.sd1 < self.datetime2)
		self.assertTrue(self.sd1 <= self.datetime2)

	def test_compareSingleDateSingleDateTime(self):
		self.assertTrue(self.sd1 > self.sdt3)
		self.assertTrue(self.sdt3 < self.sd1)

	def test_SingleDate(self):

		self.assertEqual(self.sd1.getMediawikiEntry(), "* Mi, 20.08.: name")
		self.assertEqual(self.sd1.getMediawikiEntry(lang=cg.LANG_EN), "* Wed, 20.08.: name")
		self.assertEqual(self.sd1.getMediawikiName(), "name")
		
		self.assertTrue(self.sd1 < self.sd2)
		self.assertTrue(self.sd1 <= self.sd2)
		self.assertFalse(self.sd1 >= self.sd2)
		self.assertFalse(self.sd1 == self.sd2)
		self.assertTrue(self.sd2 > self.sd1)
		self.assertTrue(self.sd2 >= self.sd1)
		self.assertFalse(self.sd2 <= self.sd1)
		
		self.assertTrue(self.sd2 == self.sd3)
		self.assertTrue(self.sd2 <= self.sd3)
		self.assertTrue(self.sd2 >= self.sd3)

	def test_SingleDateTime(self):
		
		self.assertEqual(self.sdt1.getMediawikiEntry(), "* Fr, 22.08. 12:00: name")
		self.assertEqual(self.sdt1.getMediawikiEntry(lang=cg.LANG_EN), "* Fri, 22.08. 12:00: name")
		self.assertEqual(self.sdt1.getMediawikiName(), "name")
		
		self.assertTrue(self.sdt1 < self.sdt2)
		self.assertTrue(self.sdt2 > self.sdt1)
	
	def test_SingleDateTime2(self):
		self.assertTrue(self.sdt3 < self.sdt4)
		self.assertTrue(self.sdt4 > self.sdt3)


	def test_SingleDateTimeRange(self):

		self.assertEqual(self.sdtr1.getMediawikiEntry(), "* So, 24.08. 12:00 - 14:00: name")
		self.assertEqual(self.sdtr1.getMediawikiEntry(lang=cg.LANG_EN), "* Sun, 24.08. 12:00 - 14:00: name")
		self.assertEqual(self.sdtr1.getMediawikiName(), "name")
		
		self.assertTrue(self.sdtr1 < self.sdtr2)
		self.assertTrue(self.sdtr2 > self.sdtr1)
	
	def test_SingleDateTimeRange(self):

		self.assertTrue(self.sdtr3 < self.sdtr4)
		self.assertTrue(self.sdtr4 > self.sdtr3)


	def test_DateRange(self):

		self.assertEqual(self.dr1.getMediawikiEntry(), "* Mi, 20.08. bis Do, 21.08.: name")
		self.assertEqual(self.dr1.getMediawikiEntry(lang=cg.LANG_EN), "* Wed, 20.08. to Thu, 21.08.: name")
		self.assertEqual(self.dr1.getMediawikiName(), "name")
		
		self.assertTrue(self.dr1 < self.dr2)
		self.assertTrue(self.dr2 > self.dr1)

	def test_DateTimeRange(self):
		
		self.assertEqual(self.dtr1.getMediawikiEntry(), "* Mi, 20.08. 12:00 bis Do, 21.08. 14:00: name")
		self.assertEqual(self.dtr1.getMediawikiEntry(lang=cg.LANG_EN), "* Wed, 20.08. 12:00 to Thu, 21.08. 14:00: name")
		self.assertEqual(self.dtr1.getMediawikiName(), "name")
		
		self.assertTrue(self.dtr1 < self.dtr2)
		self.assertTrue(self.dtr2 > self.dtr1)

	def test_WeekdayMidnight(self):
		generator = cg.WeekdayTimeRangeGenerator("name", "cat", ("do", 23, 0, 3, 14), ("1.1.2014 - 31.12.2014"))
		self.assertTrue((generator.entries[0].end_datetime() - generator.entries[0].start_datetime()).total_seconds() > 0)
	

	def test_BrokenWeekdayRange(self):
		generator = cg.WeekdayTimeRangeGenerator("name", "cat", ("do", 23, 0, 3, 14), ("1.1.2014  31.12.2014"))
	
	def test_BrokenWeekdayRange2(self):
		generator = cg.WeekdayTimeRangeGenerator("name", "cat", ("Do+2", 23, 0, 3, 14), ("1.1.2014 - 31.12.2014"))

