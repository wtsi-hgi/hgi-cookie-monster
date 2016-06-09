import unittest
from datetime import datetime

from baton.json import DataObjectJSONEncoder
from baton.collections import IrodsMetadata
from baton.models import DataObject
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import Rule
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONEncoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.rules.creation_observed_but_incorrect_human_reference_rule import _rule, \
    KNOWN_UNINTERESTING_REFERENCES_PATH
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.constants.irods import IRODS_REFERENCE_KEY
from hgicookiemonster.tests._common import UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA, \
    create_creation_enrichment

with open(KNOWN_UNINTERESTING_REFERENCES_PATH, "r") as file:
    _VALID_REFERENCE = "/somewhere/references/%s/reference.fa" % file.readline().strip()

class TestCreationObservedByIncorrectHumanReferenceRule(unittest.TestCase):
    """
    Test for `creation_observed_but_incorrect_human_reference` rule.
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

    def test_no_match_when_created_but_no_reference_defined(self):
        self.cookie.enrichments.add(create_creation_enrichment(datetime(1, 1, 1)))
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_created_but_unknown_reference_defined(self):
        modification = DataObjectModification(IrodsMetadata({IRODS_REFERENCE_KEY: {"/reference/unknown/something.fa"}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertFalse(self.rule.matches(self.cookie))

    def test_no_match_when_created_but_multiple_references_defined(self):
        modification = DataObjectModification(
            IrodsMetadata({IRODS_REFERENCE_KEY: {_VALID_REFERENCE, "/reference/unknown/something.fa"}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertFalse(self.rule.matches(self.cookie))

    def test_match_when_created_and_reference_defined_in_update(self):
        modification = DataObjectModification(IrodsMetadata({IRODS_REFERENCE_KEY: {_VALID_REFERENCE}}))
        modification_as_metadata = Metadata(DataObjectModificationJSONEncoder().default(modification))
        self.cookie.enrichments.add([
            create_creation_enrichment(datetime(1, 1, 1)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), modification_as_metadata)
        ])
        self.assertTrue(self.rule.matches(self.cookie))

    def test_match_when_created_and_reference_defined_in_irods(self):
        data_object = DataObject("/path", metadata=IrodsMetadata({IRODS_REFERENCE_KEY: {_VALID_REFERENCE}}))
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
