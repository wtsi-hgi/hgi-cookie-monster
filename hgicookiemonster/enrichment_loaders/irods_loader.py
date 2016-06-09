from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.data_source import register

from hgicookiemonster.context import HgiContext
from hgicookiemonster.enrichment_loaders._irods import load_enrichment_from_irods, IRODS_ENRICHMENT


def _can_enrich(cookie: Cookie, context: HgiContext) -> bool:
    """Enrich from iRODS if not enriched from there before."""
    return IRODS_ENRICHMENT not in [enrichment.source for enrichment in cookie.enrichments]


_enrichment_loader = EnrichmentLoader(_can_enrich, load_enrichment_from_irods, IRODS_ENRICHMENT, priority=0)
register(_enrichment_loader)
