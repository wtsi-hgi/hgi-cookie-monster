from datetime import datetime

from baton._baton.json import DataObjectJSONEncoder
from baton.api import connect_to_irods_with_baton
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.models import EnrichmentLoader
from hgicommon.collections import Metadata
from hgicommon.data_source import register

from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor

IRODS_SOURCE = "irods"


def _can_enrich(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> bool:

    if cookie.enrichments[-1] != IRODS_SOURCE:
        return True


def _load_enrichment(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> Enrichment:
    _irods = connect_to_irods_with_baton(resource_accessor.config.baton.binaries_location)
    data_object = _irods.data_object.get_by_path(cookie.identifier)[0]
    data_object_as_json = DataObjectJSONEncoder().default(data_object)
    resource_accessor.slack.post_message("Added more information about %s from iRODS")
    return Enrichment(IRODS_SOURCE, datetime.now(), Metadata(data_object_as_json))


_enrichment_loader = EnrichmentLoader(_can_enrich, _load_enrichment, priority=0)
register(_enrichment_loader)
