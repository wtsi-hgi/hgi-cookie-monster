import os
import tempfile
import unittest
from datetime import datetime

import hgicookiemonster
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.json_convert import RuleApplicationLogJSONEncoder
from cookiemonster.processor.models import Rule, RuleApplicationLog
from cookiemonster.processor.processing import RULE_APPLICATION
from hgicommon.collections import Metadata
from hgicookiemonster.rules.not_ignored_rule import _rule, NOT_IGNORED_RULE_ID
from hgicookiemonster.tests._common import create_creation_enrichment


class TestNotIgnoredRule(unittest.TestCase):
    """
    Test for `not_ignored` rule.
    """
    def setUp(self):
        self.rule = _rule  # type: Rule
        self.cookie = Cookie("/path")

    def test_match_when_no_enrichments(self):
        self.assertTrue(self.rule.matches(self.cookie))

    def test_match_when_irrelevant_enrichments(self):
        rule_application_log = RuleApplicationLog("other", False)
        rule_application_log_as_metadata = Metadata(RuleApplicationLogJSONEncoder().default(rule_application_log))
        self.cookie.enrichments.add(create_creation_enrichment(datetime(1, 1, 1)))
        self.cookie.enrichments.add(Enrichment(RULE_APPLICATION, datetime(2, 2, 2), rule_application_log_as_metadata))
        self.assertTrue(self.rule.matches(self.cookie))

    def test_match_when_rule_already_executed(self):
        rule_application_log = RuleApplicationLog(NOT_IGNORED_RULE_ID, False)
        rule_application_log_as_metadata = Metadata(RuleApplicationLogJSONEncoder().default(rule_application_log))
        self.cookie.enrichments.add(create_creation_enrichment(datetime(1, 1, 1)))
        self.cookie.enrichments.add(create_creation_enrichment(datetime(3, 3, 3)))
        self.cookie.enrichments.add(Enrichment(RULE_APPLICATION, datetime(2, 2, 2), rule_application_log_as_metadata))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_action(self):
        _, path = tempfile.mkstemp()
        # Be very bad and rebind a constant...
        hgicookiemonster.rules.not_ignored_rule.NOT_IGNORED_LIST_LOCATION = path

        cookie_1 = self.cookie
        cookie_2 = Cookie("/other/path")

        try:
            self.rule.execute_action(cookie_1)
            self.rule.execute_action(cookie_2)
            with open(path, "r") as file:
                written = file.readlines()
        finally:
            os.remove(path)

        self.assertEqual(len(written), 2)
        self.assertEqual(cookie_1.identifier, written[0].strip())
        self.assertEqual(cookie_2.identifier, written[1].strip())


if __name__ == "__main__":
    unittest.main()
