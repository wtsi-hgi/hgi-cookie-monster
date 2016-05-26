from cookiemonster.common.models import Cookie
from cookiemonster.retriever.source.irods.json import DataObjectModificationJSONDecoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT

IRODS_STUDY_ID_KEY = "study_id"


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


def study_with_id_in_latest_irods_update(id: str, cookie: Cookie) -> bool:
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

    data_object_modification = DataObjectModificationJSONDecoder().decode(
        irods_update_enrichment.metadata)  # type: DataObjectModification
    modified_metadata = data_object_modification.modified_metadata

    if IRODS_STUDY_ID_KEY not in modified_metadata:
        return False

    return id in modified_metadata[IRODS_STUDY_ID_KEY]
