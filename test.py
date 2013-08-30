import unittest
from parser.Parser import Parser

class TestParser(unittest.TestCase):
	def setUp(self):
		self.parser = Parser("STATEMENT FOR TEST")

	# Expect tests
	def test_expect_word(self):
		self.assertEqual(self.parser.expect("STATEMENT"), None)

	def test_expect_words(self):
		self.assertEqual(self.parser.expect("STATEMENT","FOR","TEST"), None)

	def test_not_expected_word(self):
		self.assertRaises(Exception, self.parser.expect, "WRONG_STATEMENT")

	def test_not_expected_words(self):
		self.assertRaises(Exception, self.parser.expect, ("NOT","EXPECTED","WORDS"))

	def test_one_not_expected_word(self):
		self.assertRaises(Exception, self.parser.expect, ("STATEMENT", "WRONG","FOR","TEST"))

	def test_one_wrong_expected_word(self):
		self.assertRaises(Exception, self.parser.expect, ("STATEMENT", "WRONG","TEST"))

	# Expect optional tests
	def test_expectOptional_word(self):
		self.assertTrue(self.parser.expectOptional("STATEMENT"))

	def test_expectOptional_words(self):
		self.assertTrue(self.parser.expectOptional("STATEMENT","FOR","TEST"))

	def test_not_expectOptional_word(self):
		self.assertFalse(self.parser.expectOptional("WRONG_STATEMENT"))

	def test_not_expectOptional_words(self):
		self.assertFalse(self.parser.expectOptional("NOT","EXPECTED","WORDS"))

	def test_one_not_expectOptional_word(self):
		self.assertRaises(Exception, self.parser.expectOptional, ("WRONG", "STATEMENT","FOR","TEST"))

	def test_first_fine_other_not_expectOptional_word(self):
		self.assertRaises(Exception, self.parser.expectOptional, ("STATEMENT","WRONG","FOR","TEST"))


if __name__ == '__main__':
	unittest.main()