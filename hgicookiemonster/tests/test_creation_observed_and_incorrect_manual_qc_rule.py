import unittest
from datetime import datetime

from baton.collections import IrodsMetadata
from baton.json import DataObjectJSONEncoder
from baton.models import DataObject
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import Rule
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONEncoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.rules.creation_observed_and_incorrect_manual_qc_rule import _rule, INCORRECT_MANUAL_QC_VALUE
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.constants.irods import IRODS_MANUAL_QC_KEY
from hgicookiemonster.tests._common import UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA, \
    create_creation_enrichment


class TestCreationObservedAndIncorrectManualQCRule(unittest.TestCase):
    """
    Test for `creation_observed_and_incorrect_manual_qc` rule.
    """
    def setUp(self):
        self.rule = _rule  # type: Rule
        self.cookie = Cookie("test")

    def test_no_match_when_no_enrichments(self):
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_unrelated_enrichment(self):
        self.cookie.enrichments.add(Enrichment("other", datetime(1, 1, 1), Metadata()))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_no_creation_observed(self):
        self.cookie.enrichments.add(
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_created_but_no_manual_qc_defined(self):
        self.cookie.enrichments.add(create_creation_enrichment(datetime(1, 1, 1)))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_created_but_unknown_manual_qc(self):
        modification = DataObjectModification(IrodsMetadata({IRODS_MANUAL_QC_KEY: {"unknown"}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_created_but_multiple_manual_qc_values_defined(self):
        modification = DataObjectModification(
            IrodsMetadata({IRODS_MANUAL_QC_KEY: {INCORRECT_MANUAL_QC_VALUE, "unknown"}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertFalse(self.rule.matches(self.cookie))

    def test_match_when_created_and_manual_qc_in_update(self):
        modification = DataObjectModification(IrodsMetadata({IRODS_MANUAL_QC_KEY: {INCORRECT_MANUAL_QC_VALUE}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertTrue(self.rule.matches(self.cookie))

    def test_match_when_created_and_manual_qc_in_irods(self):
        data_object = DataObject("/path", metadata=IrodsMetadata({IRODS_MANUAL_QC_KEY: {INCORRECT_MANUAL_QC_VALUE}}))
        data_object_as_metadata = Metadata(DataObjectJSONEncoder().default(data_object))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_ENRICHMENT, datetime(2, 2, 2), data_object_as_metadata)
        ])
        self.assertTrue(self.rule.matches(self.cookie))

    def test_action(self):
        self.assertTrue(self.rule.execute_action(Cookie("")))


if __name__ == "__main__":
    unittest.main()
