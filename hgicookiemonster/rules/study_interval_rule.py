from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import has_irods_update_enrichment_followed_by_irods_enrichment, \
    study_with_id_in_most_recent_irods_update, tagged_as_library_in_irods


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    if not has_irods_update_enrichment_followed_by_irods_enrichment(cookie):
        return False

    if not study_with_id_in_most_recent_irods_update("3765", cookie):
        return False

    return tagged_as_library_in_irods(cookie)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.get_most_recent_enrichment_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.slack.post("Additional library in iRODS for study 3765 (INTERVAL) at %s: %s" % (timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, "interval", Priority.MAX_PRIORITY)
register(_rule)
