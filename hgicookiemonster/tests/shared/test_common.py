import unittest
from datetime import datetime

from baton.collections import IrodsMetadata
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.retriever.source.irods.json import DataObjectModificationJSONEncoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import has_irods_update_enrichment_followed_by_irods_enrichment, \
    study_with_id_in_most_recent_irods_update, IRODS_STUDY_ID_KEY


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


class TestStudyWithIdInLatestIrodsUpdate(unittest.TestCase):
    """
    Tests for `study_with_id_in_latest_irods_update`.
    """
    @staticmethod
    def _create_irods_update_metadata_for_metadata_modification(modified_metadata: IrodsMetadata) -> Metadata:
        """
        Creates metadata for an iRODS update when the given data object metadata is modified.
        :param modified_metadata: the modified metadata
        :return: representation of metadata modification when retrieved via iRODS update
        """
        data_object_modification = DataObjectModification(modified_metadata)
        data_object_modification_as_dict = DataObjectModificationJSONEncoder().default(data_object_modification)
        return Metadata(data_object_modification_as_dict)

    def setUp(self):
        self.study_id = "123"
        self.cookie = Cookie("my_identifier")
        self.other_enrichment = Enrichment(IRODS_ENRICHMENT, datetime(10, 10, 10), Metadata())
        self.irods_update_enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(10, 10, 10), Metadata())

    def test_no_enrichments(self):
        self.assertFalse(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))

    def test_no_irods_update_enrichments(self):
        self.cookie.enrich(self.other_enrichment)
        self.cookie.enrich(self.other_enrichment)
        self.assertFalse(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))

    def test_irods_update_with_metadata_but_no_study_id_key(self):
        self.irods_update_enrichment.metadata = self._create_irods_update_metadata_for_metadata_modification(
            IrodsMetadata({"other_key": {self.study_id}}))
        self.cookie.enrich(self.irods_update_enrichment)
        self.assertFalse(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))

    def test_irods_update_with_other_study_id_key(self):
        self.irods_update_enrichment.metadata = self._create_irods_update_metadata_for_metadata_modification(
            IrodsMetadata({IRODS_STUDY_ID_KEY: {"%s2" % self.study_id}}))
        self.cookie.enrich(self.irods_update_enrichment)
        self.assertFalse(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))

    def test_irods_update_with_study_id_key(self):
        self.irods_update_enrichment.metadata = self._create_irods_update_metadata_for_metadata_modification(
            IrodsMetadata({IRODS_STUDY_ID_KEY: {self.study_id}}))
        self.cookie.enrich(self.irods_update_enrichment)
        self.assertTrue(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))

    def test_irods_update_with_study_id_key_but_not_in_latest_irods_update(self):
        self.irods_update_enrichment.metadata = self._create_irods_update_metadata_for_metadata_modification(
            IrodsMetadata({IRODS_STUDY_ID_KEY: {self.study_id}}))

        more_recent_enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(20, 10, 10), Metadata())
        more_recent_enrichment.metadata = self._create_irods_update_metadata_for_metadata_modification(
            IrodsMetadata({IRODS_STUDY_ID_KEY: {"corrected_id"}}))

        self.cookie.enrich(self.irods_update_enrichment)
        self.cookie.enrich(more_recent_enrichment)
        self.assertFalse(study_with_id_in_most_recent_irods_update(self.study_id, self.cookie))


if __name__ == "__main__":
    unittest.main()
