from datetime import datetime
from cookiemonster import EnrichmentLoader, Cookie, Enrichment
from hgicommon.collections import Metadata
from hgicommon.mixable import Priority
from hgicommon.data_source import register


def _can_enrich(cookie: Cookie) -> bool:
    return False


def _load_enrichment(cookie: Cookie) -> Enrichment:
    return Enrichment("my_source_name", datetime.now(), Metadata())


_enrichment_loader = EnrichmentLoader(_can_enrich, _load_enrichment, Priority.MAX_PRIORITY)
register(_enrichment_loader)