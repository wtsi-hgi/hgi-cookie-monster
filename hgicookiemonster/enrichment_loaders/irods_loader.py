from datetime import datetime
from threading import Semaphore, BoundedSemaphore

from baton._baton.json import DataObjectJSONEncoder
from baton.api import connect_to_irods_with_baton
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.collections import Metadata
from hgicommon.data_source import register

from hgicookiemonster.context import HgiContext

IRODS_SOURCE = "irods"
MAX_IRODS_CONNECTIONS = 20      # TODO: This should be a setting...

_irods_connections = BoundedSemaphore(MAX_IRODS_CONNECTIONS)


def _can_enrich(cookie: Cookie, context: HgiContext) -> bool:
    if cookie.enrichments[-1].source == IRODS_SOURCE:
        return False
    return cookie.identifier.endswith(".bam") or cookie.identifier.endswith(".cram")


def _load_enrichment(cookie: Cookie, context: HgiContext) -> Enrichment:
    with _irods_connections:
        _irods = connect_to_irods_with_baton(context.config.baton.binaries_location)
        data_object = _irods.data_object.get_by_path(cookie.identifier)
        data_object_as_json = DataObjectJSONEncoder().default(data_object)
        return Enrichment(IRODS_SOURCE, datetime.now(), Metadata(data_object_as_json))


_enrichment_loader = EnrichmentLoader(_can_enrich, _load_enrichment, priority=0, name=IRODS_SOURCE)
register(_enrichment_loader)
