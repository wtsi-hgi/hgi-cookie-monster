from baton._baton.json import DataObjectJSONDecoder
from baton.models import DataObject
from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext
from hgicookiemonster.enrichment_loaders.irods_loader import IRODS_ENRICHMENT
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import has_irods_update_enrichment_followed_by_irods_enrichment, \
    study_with_id_in_most_recent_irods_update


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    if not has_irods_update_enrichment_followed_by_irods_enrichment(cookie):
        return False

    if not study_with_id_in_most_recent_irods_update("3543", cookie):
        return False

    irods_enrichment = cookie.get_most_recent_enrichment_from_source(IRODS_ENRICHMENT)
    assert irods_enrichment is not None

    data_object_as_dict = dict(irods_enrichment.metadata)
    data_object = DataObjectJSONDecoder().decode_parsed(data_object_as_dict)
    assert isinstance(data_object, DataObject)

    if "target" not in data_object.metadata:
        return False
    return "library" in data_object.metadata["target"]


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.get_most_recent_enrichment_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.slack.post("Additional library in iRODS for study 3543 (PAGE) at %s: %s" % (timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, Priority.MAX_PRIORITY, "study_3543")
register(_rule)
