from typing import Optional, Tuple

from baton._baton.json import DataObjectJSONDecoder

from cookiemonster.common.collections import EnrichmentCollection
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONDecoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT


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
            if modification.modified_replicas.get_by_number(0) is not None:
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







# def study_with_id_in_most_recent_irods_update(id: str, cookie: Cookie) -> bool:
#     """
#     Decides whether the Cookie shows that metadata was added in the iRODS update to indicate that the updated iRODS
#     entity belongs to the study with the given ID.
#     :param id: the ID of the study of interest
#     :param cookie: the cookie
#     :return: whether the last iRODS update shows that the related iRODS entity is part of the study with the given ID
#     """
#     irods_update_enrichment = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT)
#
#     if irods_update_enrichment is None:
#         return False
#
#     assert isinstance(irods_update_enrichment.metadata, Metadata)
#     data_object_modification = DataObjectModificationJSONDecoder().decode_parsed(
#         irods_update_enrichment.metadata)  # type: DataObjectModification
#     modified_metadata = data_object_modification.modified_metadata
#
#     if IRODS_STUDY_ID_KEY not in modified_metadata:
#         return False
#
#     return id in modified_metadata[IRODS_STUDY_ID_KEY]
#
#
# def tagged_as_library_in_irods(cookie: Cookie) -> bool:
#     """
#     Whether the entity the cookie relates to has been tagged as a library in iRODS via the "target" metadata key.
#
#     The cookie must have at least one enrichment from iRODS; only the most recent enrichment from this source will be
#     used.
#     :param cookie: the cookie of interest
#     :return: whether the cookie indicates the entity is tagged as a library in iRODS
#     """
#     irods_enrichment = cookie.enrichments.get_most_recent_from_source(IRODS_ENRICHMENT)
#     assert irods_enrichment is not None
#
#     data_object_as_dict = dict(irods_enrichment.metadata)
#     data_object = DataObjectJSONDecoder().decode_parsed(data_object_as_dict)
#     assert isinstance(data_object, DataObject)
#
#     if IRODS_TARGET_KEY not in data_object.metadata:
#         return False
#     return IRODS_TARGET_LIBRARY_VALUE in data_object.metadata[IRODS_TARGET_KEY]
