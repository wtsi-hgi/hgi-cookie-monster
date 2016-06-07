from baton._baton.json import DataObjectJSONDecoder
from baton.models import DataObject

from cookiemonster.common.models import Cookie
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONDecoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT

IRODS_STUDY_ID_KEY = "study_id"

IRODS_TARGET_KEY = "target"
IRODS_TARGET_LIBRARY_VALUE = "library"


def has_irods_update_enrichment_followed_by_irods_enrichment(cookie: Cookie) -> bool:
    """
    Gets whether the cookie was last enriched by an iRODS update, preceded by an enrichment due to an iRODS update.
    :param cookie: the cookie to examine
    :return: whether the last two enrichments have been from iRODS update and then iRODS
    """
    if len(cookie.enrichments) < 2:
        return False

    irods_update_enrichment = cookie.enrichments[-2]
    irods_enrichment = cookie.enrichments[-1]

    return irods_update_enrichment.source == IRODS_UPDATE_ENRICHMENT and irods_enrichment.source == IRODS_ENRICHMENT


def study_with_id_in_most_recent_irods_update(id: str, cookie: Cookie) -> bool:
    """
    Decides whether the Cookie shows that metadata was added in the iRODS update to indicate that the updated iRODS
    entity belongs to the study with the given ID.
    :param id: the ID of the study of interest
    :param cookie: the cookie
    :return: whether the last iRODS update shows that the related iRODS entity is part of the study with the given ID
    """
    irods_update_enrichment = cookie.get_most_recent_enrichment_from_source(IRODS_UPDATE_ENRICHMENT)

    if irods_update_enrichment is None:
        return False

    assert isinstance(irods_update_enrichment.metadata, Metadata)
    data_object_modification = DataObjectModificationJSONDecoder().decode_parsed(
        irods_update_enrichment.metadata)  # type: DataObjectModification
    modified_metadata = data_object_modification.modified_metadata

    if IRODS_STUDY_ID_KEY not in modified_metadata:
        return False

    return id in modified_metadata[IRODS_STUDY_ID_KEY]


def tagged_as_library_in_irods(cookie: Cookie) -> bool:
    """
    Whether the entity the cookie relates to has been tagged as a library in iRODS via the "target" metadata key.

    The cookie must have at least one enrichment from iRODS; only the most recent enrichment from this source will be
    used.
    :param cookie: the cookie of interest
    :return: whether the cookie indicates the entity is tagged as a library in iRODS
    """
    irods_enrichment = cookie.get_most_recent_enrichment_from_source(IRODS_ENRICHMENT)
    assert irods_enrichment is not None

    data_object_as_dict = dict(irods_enrichment.metadata)
    data_object = DataObjectJSONDecoder().decode_parsed(data_object_as_dict)
    assert isinstance(data_object, DataObject)

    if IRODS_TARGET_KEY not in data_object.metadata:
        return False
    return IRODS_TARGET_LIBRARY_VALUE in data_object.metadata[IRODS_TARGET_KEY]
