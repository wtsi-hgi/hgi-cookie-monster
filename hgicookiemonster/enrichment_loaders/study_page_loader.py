from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.data_source import register

from hgicookiemonster.context import HgiContext
from hgicookiemonster.enrichment_loaders._irods import load_enrichment_from_irods, IRODS_ENRICHMENT
from hgicookiemonster.shared.common import study_with_id_in_most_recent_irods_update



def _can_enrich(cookie: Cookie, context: HgiContext) -> bool:
    return cookie.enrichments[-1].source != IRODS_ENRICHMENT and study_with_id_in_most_recent_irods_update("3543", cookie)


_enrichment_loader = EnrichmentLoader(_can_enrich, load_enrichment_from_irods, priority=0, id=IRODS_ENRICHMENT)
register(_enrichment_loader)
