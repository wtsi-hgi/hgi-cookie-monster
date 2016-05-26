from cookiemonster.common.models import Cookie
from cookiemonster.retriever.source.irods.json import DataObjectModificationJSONDecoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT


def study_id_3543_in_latest_irods_update(cookie: Cookie) -> bool:
    """
    Decides whether the Cookie shows that metadata was added in the iRODS update to indicate that the updated iRODS
    entity belongs to the study with ID 3543 (PAGE).
    :param cookie: the cookie
    :return: whether the last iRODS update shows that the related iRODS entity is part of the PAGE study
    """
    irods_update_enrichment = cookie.get_most_recent_enrichment_from_source(IRODS_UPDATE_ENRICHMENT)

    if irods_update_enrichment is None:
        return False

    data_object_modification = DataObjectModificationJSONDecoder().decode(
        irods_update_enrichment.metadata)  # type: DataObjectModification
    modified_metadata = data_object_modification.modified_metadata

    if "study_id" not in modified_metadata:
        return False

    return "3543" in modified_metadata["study_id"]
