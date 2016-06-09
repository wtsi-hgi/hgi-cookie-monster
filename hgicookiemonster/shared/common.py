from typing import Optional, Tuple

from baton._baton.json import DataObjectJSONDecoder

from cookiemonster.common.collections import EnrichmentCollection
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONDecoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.constants.irods import IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE, IRODS_STUDY_ID_KEY, \
    IRODS_TARGET_KEY, IRODS_TARGET_LIBRARY_VALUE


def was_creation_observed(enrichments: EnrichmentCollection) -> bool:
    """
    Whether the creation of the data object was observed, defined as having an iRODS update enrichment that shows the
    modification of replica number 0.
    :param enrichments: the enrichments to check for the creation with
    :return: whether the creation of the data object was observed
    """
    for enrichment in enrichments:
        if enrichment.source == IRODS_UPDATE_ENRICHMENT:
            modification = DataObjectModificationJSONDecoder().decode_parsed(enrichment.metadata)  # type: DataObjectModification
            if modification.modified_replicas.get_by_number(IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE) is not None:
                return True
    return False


def extract_latest_metadata_key_value_known_in_irods(enrichments: EnrichmentCollection, key: str) -> Optional[Tuple]:
    """
    Extracts the latest value in iRODS associated with the given metadata key from a given collection of enrichments.
    Values in both iRODS updates enrichments and iRODS enrichments are considered.
    :param enrichments: the enrichments
    :param key: the metadata key
    :return: the lastest value associated to the key else `None` if no value is known
    """
    value = None
    for enrichment in enrichments:
        irods_metadata = None
        if enrichment.source == IRODS_UPDATE_ENRICHMENT:
            modification = DataObjectModificationJSONDecoder().decode_parsed(dict(enrichment.metadata))
            irods_metadata = modification.modified_metadata
        if enrichment.source == IRODS_ENRICHMENT:
            data_object = DataObjectJSONDecoder().decode_parsed(dict(enrichment.metadata))
            irods_metadata = data_object.metadata

        if irods_metadata is not None:
            if key in irods_metadata:
                value = irods_metadata[key]

    return value


def relates_to_library_in_study(enrichments: EnrichmentCollection, study_id: str) -> bool:
    """
    Whether the enrichments indicate a relation to a library in the given study.
    :param enrichments: the enrichments
    :param study_id: the study of interest
    :return: whether the enrichments indicate to a library in the given study
    """
    extracted_study_id = extract_latest_metadata_key_value_known_in_irods(enrichments, IRODS_STUDY_ID_KEY)
    extracted_target = extract_latest_metadata_key_value_known_in_irods(enrichments, IRODS_TARGET_KEY)
    if extracted_study_id is None or extracted_target is None:
        return False
    return IRODS_TARGET_LIBRARY_VALUE in extracted_target and study_id in extracted_study_id
