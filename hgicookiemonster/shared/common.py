from cookiemonster.common.models import Cookie
from hgicookiemonster.enrichment_loaders._irods import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT


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

    if not (irods_update_enrichment.source == IRODS_UPDATE_ENRICHMENT and irods_enrichment.source == IRODS_ENRICHMENT):
        return False
