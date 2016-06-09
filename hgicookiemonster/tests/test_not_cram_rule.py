import unittest

from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicookiemonster.rules.not_cram_rule import _rule


class TestNotCramRule(unittest.TestCase):
    """
    Test for `not_cram` rule.
    """
    def setUp(self):
        self.rule = _rule  # type: Rule

    def test_no_match_when_cram_file_extension(self):
        self.assertFalse(self.rule.matches(Cookie("/test/test.cram")))

    def test_no_match_when_cram_file_extension_in_upper_case(self):
        self.assertFalse(self.rule.matches(Cookie("/test/test.CRAM")))

    def test_match_when_no_file_extension(self):
        self.assertTrue(self.rule.matches(Cookie("/test/test")))

    def test_match_when_other_file_extension(self):
        self.assertTrue(self.rule.matches(Cookie("/test/test.json")))

    def test_match_when_cram_in_file_name(self):
        self.assertTrue(self.rule.matches(Cookie("/test/test.cram.json")))

    def test_action(self):
        self.assertTrue(self.rule.execute_action(Cookie("")))


if __name__ == "__main__":
    unittest.main()
