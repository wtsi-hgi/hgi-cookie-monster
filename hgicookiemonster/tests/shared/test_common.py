import unittest
from datetime import datetime

from baton.json import DataObjectJSONEncoder
from baton.collections import IrodsMetadata, DataObjectReplicaCollection
from baton.models import DataObjectReplica, DataObject
from cookiemonster.common.collections import EnrichmentCollection
from cookiemonster.common.models import Enrichment
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONEncoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import was_creation_observed, extract_latest_metadata_key_value_known_in_irods
from hgicookiemonster.shared.constants.irods import IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE
from hgicookiemonster.tests._common import UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA, \
    UNINTERESTING_DATA_OBJECT_AS_METADATA

_METADATA_KEY = "key"


class TestWasCreationObserved(unittest.TestCase):
    """
    Tests for `was_creation_observed`.
    """
    def setUp(self):
        self.enrichment_collection = EnrichmentCollection()

    def test_no_enrichments(self):
        self.assertFalse(was_creation_observed(self.enrichment_collection))

    def test_unrelated_enrichment(self):
        self.enrichment_collection.add(Enrichment("other", datetime(1, 1, 1), Metadata()))
        self.assertFalse(was_creation_observed(self.enrichment_collection))

    def test_no_creation_observed(self):
        modified_replicas = DataObjectReplicaCollection(
            {DataObjectReplica(IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE + 1, "")})
        unrelated_modification = DataObjectModification(IrodsMetadata({"other": {"value"}}), modified_replicas)
        unrelated_modification_as_dict = DataObjectModificationJSONEncoder().default(unrelated_modification)
        self.enrichment_collection.add([
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), Metadata(unrelated_modification_as_dict)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA),
        ])
        self.assertFalse(was_creation_observed(self.enrichment_collection))

    def test_creation_observed(self):
        modified_replicas = DataObjectReplicaCollection(
            {DataObjectReplica(IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE, "")})
        modification = DataObjectModification(IrodsMetadata({"other": {"value"}}), modified_replicas)
        modification_as_dict = DataObjectModificationJSONEncoder().default(modification)
        self.enrichment_collection.add([
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), Metadata(modification_as_dict)),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA),
        ])
        self.assertTrue(was_creation_observed(self.enrichment_collection))


class TestExtractLatestMetadataKeyValueKnownInIrods(unittest.TestCase):
    """
    Tests for `extract_latest_metadata_key_value_known_in_irods`.
    """
    def setUp(self):
        self.enrichment_collection = EnrichmentCollection()
        interesting_modifications = [
            DataObjectModification(IrodsMetadata({_METADATA_KEY: {0}})),
            DataObjectModification(IrodsMetadata({_METADATA_KEY: {1}}))
        ]
        encoder = DataObjectModificationJSONEncoder()
        self.interesting_modifications_as_metadata = [
            Metadata(encoder.default(modification)) for modification in interesting_modifications
        ]

        interesting_data_objects = [
            DataObject("/path-1", metadata=IrodsMetadata({_METADATA_KEY: {2}})),
            DataObject("/path-2", metadata=IrodsMetadata({_METADATA_KEY: {3}}))
        ]
        encoder = DataObjectJSONEncoder()
        self.interesting_data_objects_as_metadata = [
            Metadata(encoder.default(data_object)) for data_object in interesting_data_objects
        ]

    def test_no_enrichments(self):
        self.assertIsNone(extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY))

    def test_no_irods_related_enrichments(self):
        self.enrichment_collection.add(Enrichment("other", datetime(1, 1, 1), Metadata()))
        self.assertIsNone(extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY))

    def test_not_in_irods_update_enrichment(self):
        enrichment = Enrichment(
            IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), Metadata(UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA))
        self.enrichment_collection.add(enrichment)
        self.assertIsNone(extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY))

    def test_not_in_irods_enrichment(self):
        enrichment = Enrichment(IRODS_ENRICHMENT, datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_AS_METADATA)
        self.enrichment_collection.add(enrichment)
        self.assertIsNone(extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY))

    def test_not_in_irods_enrichment_or_irods_update(self):
        enrichments = [
            Enrichment(IRODS_ENRICHMENT, datetime(1, 1, 1), UNINTERESTING_DATA_OBJECT_AS_METADATA),
            Enrichment(
                IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2),
                Metadata(UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA))
        ]
        self.enrichment_collection.add(enrichments)
        self.assertIsNone(extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY))

    def test_in_irods_update_enrichments(self):
        enrichments = [
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), self.interesting_modifications_as_metadata[0]),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), self.interesting_modifications_as_metadata[1]),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA),
        ]
        self.enrichment_collection.add(enrichments)
        value = extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY)
        self.assertEqual(len(list(value)), 1)
        self.assertIn(1, value)

    def test_in_irods_enrichments(self):
        enrichments = [
            Enrichment(IRODS_ENRICHMENT, datetime(1, 1, 1), self.interesting_data_objects_as_metadata[0]),
            Enrichment(IRODS_ENRICHMENT, datetime(2, 2, 2), self.interesting_data_objects_as_metadata[1]),
            Enrichment(IRODS_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_AS_METADATA),
        ]
        self.enrichment_collection.add(enrichments)
        value = extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY)
        self.assertEqual(len(list(value)), 1)
        self.assertIn(3, value)

    def test_in_irods_enrichments_and_irods_update_enrichments_when_most_recent_from_irods_enrichment(self):
        enrichments = [
            Enrichment(IRODS_ENRICHMENT, datetime(1, 1, 1), self.interesting_data_objects_as_metadata[0]),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(2, 2, 2), self.interesting_modifications_as_metadata[0]),
            Enrichment(IRODS_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_AS_METADATA),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(4, 4, 4), self.interesting_modifications_as_metadata[1]),
            Enrichment(IRODS_ENRICHMENT, datetime(5, 5, 5), self.interesting_data_objects_as_metadata[1])
        ]
        self.enrichment_collection.add(enrichments)
        value = extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY)
        self.assertEqual(len(list(value)), 1)
        self.assertIn(3, value)

    def test_in_irods_enrichments_and_irods_update_enrichments_when_most_recent_from_irods_update_enrichment(self):
        enrichments = [
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(1, 1, 1), self.interesting_modifications_as_metadata[0]),
            Enrichment(IRODS_ENRICHMENT, datetime(2, 2, 2), self.interesting_data_objects_as_metadata[0]),
            Enrichment(IRODS_ENRICHMENT, datetime(3, 3, 3), UNINTERESTING_DATA_OBJECT_AS_METADATA),
            Enrichment(IRODS_ENRICHMENT, datetime(4, 4, 4), self.interesting_data_objects_as_metadata[1]),
            Enrichment(IRODS_UPDATE_ENRICHMENT, datetime(5, 5, 5), self.interesting_modifications_as_metadata[1])
        ]
        self.enrichment_collection.add(enrichments)
        value = extract_latest_metadata_key_value_known_in_irods(self.enrichment_collection, _METADATA_KEY)
        self.assertEqual(len(list(value)), 1)
        self.assertIn(1, value)


if __name__ == "__main__":
    unittest.main()
