from datetime import datetime
from threading import BoundedSemaphore

from baton._baton.api import connect_to_irods_with_baton
from baton._baton.json import DataObjectJSONEncoder
from cookiemonster.common.models import Cookie, Enrichment
from hgicommon.collections import Metadata
from hgicookiemonster.context import HgiContext

IRODS_ENRICHMENT = "irods"
MAX_IRODS_CONNECTIONS = 20      # TODO: This should be a setting...

_irods_connections = BoundedSemaphore(MAX_IRODS_CONNECTIONS)


def load_enrichment_from_irods(cookie: Cookie, context: HgiContext) -> Enrichment:
    with _irods_connections:
        _irods = connect_to_irods_with_baton(context.config.baton.binaries_location)
        data_object = _irods.data_object.get_by_path(cookie.identifier)
        data_object_as_json = DataObjectJSONEncoder().default(data_object)
        return Enrichment(IRODS_ENRICHMENT, datetime.now(), Metadata(data_object_as_json))
