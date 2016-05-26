import unittest
from datetime import datetime

from cookiemonster.common.models import Cookie, Enrichment
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import has_irods_update_enrichment_followed_by_irods_enrichment


class TestHasIrodsUpdateEnrichmentFollowedByIrodsEnrichment(unittest.TestCase):
    """
    Tests for `has_irods_update_enrichment_followed_by_irods_enrichment`.
    """
    def setUp(self):
        self.cookie = Cookie("my_identifier")
        self.irods_enrichment = Enrichment(IRODS_ENRICHMENT, datetime(10, 10, 10), Metadata())
        self.irods_update_enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(10, 10, 10), Metadata())

    def test_no_enrichments(self):
        self.assertFalse(has_irods_update_enrichment_followed_by_irods_enrichment(self.cookie))

    def test_only_irods_enrichment(self):
        self.cookie.enrich(self.irods_enrichment)
        self.assertFalse(has_irods_update_enrichment_followed_by_irods_enrichment(self.cookie))

    def test_only_irods_enrichment_followed_by_irods_update_enrichment(self):
        self.irods_enrichment.timestamp = self.irods_enrichment.timestamp.replace(year=5)
        assert self.irods_enrichment.timestamp < self.irods_update_enrichment.timestamp
        self.cookie.enrich(self.irods_enrichment)
        self.cookie.enrich(self.irods_update_enrichment)
        self.assertFalse(has_irods_update_enrichment_followed_by_irods_enrichment(self.cookie))

    def test_irods_update_enrichment_followed_by_irods_enrichment(self):
        self.irods_update_enrichment.timestamp = self.irods_update_enrichment.timestamp.replace(year=5)
        assert self.irods_update_enrichment.timestamp < self.irods_enrichment.timestamp
        self.cookie.enrich(self.irods_enrichment)
        self.cookie.enrich(self.irods_update_enrichment)
        self.assertTrue(has_irods_update_enrichment_followed_by_irods_enrichment(self.cookie))

    def test_irods_update_enrichment_followed_by_irods_enrichment_when_not_latest(self):
        self.irods_update_enrichment.timestamp = self.irods_update_enrichment.timestamp.replace(year=5)
        assert self.irods_update_enrichment.timestamp < self.irods_enrichment.timestamp
        self.cookie.enrich(self.irods_enrichment)
        self.cookie.enrich(self.irods_update_enrichment)
        self.cookie.enrich(Enrichment("other", datetime(1, 1, 1), Metadata()))
        self.assertTrue(has_irods_update_enrichment_followed_by_irods_enrichment(self.cookie))

if __name__ == "__main__":
    unittest.main()
