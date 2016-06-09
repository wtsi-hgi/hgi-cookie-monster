import unittest
from datetime import datetime

from baton.collections import IrodsMetadata
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import Rule
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.rules.study_interval_rule import INTERVAL_STUDY_ID
from hgicookiemonster.rules.study_interval_rule import _rule
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.constants.irods import IRODS_STUDY_ID_KEY, IRODS_TARGET_KEY, IRODS_TARGET_LIBRARY_VALUE
from hgicookiemonster.tests._common import UNINTERESTING_DATA_OBJECT_AS_METADATA, \
    create_data_object_modification_as_metadata, create_data_object_as_metadata


class TestStudyIntervalRule(unittest.TestCase):
    """
    Test for `study_interval` rule.
    """
    def setUp(self):
        self.rule = _rule  # type: Rule
        self.cookie = Cookie("test")

    def test_no_match_when_no_enrichments(self):
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_no_study_id_or_target(self):
        enrichment = Enrichment("other", datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_AS_METADATA)
        self.cookie.enrichments.add(enrichment)
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_other_study_id_and_other_target(self):
        metadata = create_data_object_modification_as_metadata(IrodsMetadata({
            IRODS_STUDY_ID_KEY: {"other_value"},
            IRODS_TARGET_KEY: {"other_value"},
        }))
        enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), metadata)
        self.cookie.enrichments.add(enrichment)
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_other_study_id_and_correct_target(self):
        metadata = create_data_object_modification_as_metadata(IrodsMetadata({
            IRODS_STUDY_ID_KEY: {"other_value"},
            IRODS_TARGET_KEY: {IRODS_TARGET_LIBRARY_VALUE},
        }))
        enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), metadata)
        self.cookie.enrichments.add(enrichment)
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_correct_study_id_and_other_target(self):
        metadata = create_data_object_modification_as_metadata(IrodsMetadata({
            IRODS_STUDY_ID_KEY: {INTERVAL_STUDY_ID},
            IRODS_TARGET_KEY: {"other_value"},
        }))
        self.cookie.enrichments.add(Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), metadata))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_correct_study_id_and_correct_target_in_same_enrichment(self):
        metadata = create_data_object_modification_as_metadata(IrodsMetadata({
            IRODS_STUDY_ID_KEY: {INTERVAL_STUDY_ID},
            IRODS_TARGET_KEY: {IRODS_TARGET_LIBRARY_VALUE},
        }))
        self.cookie.enrichments.add(Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), metadata))
        self.assertTrue(self.rule.matches(self.cookie))

    def test_no_match_when_correct_study_id_and_correct_target_in_different_enrichments(self):
        modification_metadata = create_data_object_modification_as_metadata(IrodsMetadata({
            IRODS_TARGET_KEY: {IRODS_TARGET_LIBRARY_VALUE}
        }))
        data_object_metadata = create_data_object_as_metadata(metadata=IrodsMetadata({
            IRODS_STUDY_ID_KEY: {INTERVAL_STUDY_ID}
        }))
        self.cookie.enrichments.add([
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), modification_metadata),
            Enrichment(IRODS_ENRICHMENT, datetime(2, 2, 2), data_object_metadata)
        ])
        self.assertTrue(self.rule.matches(self.cookie))


if __name__ == "__main__":
    unittest.main()
