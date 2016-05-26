from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.data_source import register

from hgicookiemonster.context import HgiContext
from hgicookiemonster.enrichment_loaders._irods import load_enrichment_from_irods, IRODS_ENRICHMENT
from hgicookiemonster.shared.study_3543 import study_id_3543_in_latest_irods_update


def _can_enrich(cookie: Cookie, context: HgiContext) -> bool:
    return cookie.enrichments[-1].source != IRODS_ENRICHMENT and study_id_3543_in_latest_irods_update(cookie)


_enrichment_loader = EnrichmentLoader(_can_enrich, load_enrichment_from_irods, priority=0, name=IRODS_ENRICHMENT)
register(_enrichment_loader)
