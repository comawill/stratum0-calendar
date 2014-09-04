import unittest
import calendargenerator as cg
class TestUrls(unittest.TestCase):
	def setUp(self):
		pass

	def test_internUrlTitle(self):
		url_date = cg.SingleDate("abc [[test_url|test_title]]", "cat", [20,9,2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date.getPlainName(), "abc test_title")
	
	def test_internUrl(self):
		url_date = cg.SingleDate("abc [[test_url]]", "cat", [20,9,2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date.getPlainName(), "abc test_url")

	def test_externUrl(self):
		url_date = cg.SingleDate("abc [https://stratum0.net/ title]", "cat", [20,9,2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.net/")
		self.assertEqual(url_date.getPlainName(), "abc title")

	def test_firstUrl(self):
		url_date = cg.SingleDate("abc [https://stratum0.net/ title] [[test_url|test_title]]", "cat", [20,9,2014])
		self.assertEqual(url_date.getURL(), "https://stratum0.net/")
		self.assertEqual(url_date.getPlainName(), "abc title test_title")
		
		url_date2 = cg.SingleDate("abc [[test_url|test_title]] [https://stratum0.net/ title]", "cat", [20,9,2014])
		self.assertEqual(url_date2.getURL(), "https://stratum0.org/wiki/test_url")
		self.assertEqual(url_date2.getPlainName(), "abc test_title title")


class TestPlainName(unittest.TestCase):
	def setUp(self):
		pass

	def test_emph(self):
		url_date = cg.SingleDate("abc ''def''", "cat", [20,9,2014])
		self.assertEqual(url_date.getPlainName(), "abc def")
	
	def test_double_emph(self):
		url_date = cg.SingleDate("abc ''def'' ''ghi''", "cat", [20,9,2014])
		self.assertEqual(url_date.getPlainName(), "abc def ghi")
	

