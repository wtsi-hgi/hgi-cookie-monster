from datetime import datetime

from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.collections import Metadata
from hgicommon.data_source import register
from hgicommon.mixable import Priority

from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor


def _can_enrich(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> bool:
    return False


def _load_enrichment(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> Enrichment:
    return Enrichment("my_source_name", datetime.now(), Metadata())


_enrichment_loader = EnrichmentLoader(_can_enrich, _load_enrichment, Priority.MAX_PRIORITY)
register(_enrichment_loader)
