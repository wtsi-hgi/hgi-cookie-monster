from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules._common import STUDY_RULE_PRIORITY
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import relates_to_library_in_study

STUDY_POMAK_RULE_ID = "study_pomak"
STUDY_POMAK_RULE_PRIORITY = STUDY_RULE_PRIORITY

POMAK_STUDY_ID = "3597"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    return relates_to_library_in_study(cookie.enrichments, POMAK_STUDY_ID)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.rule_writer("Additional library in iRODS for study %s (POMAK) at %s: %s"
                        % (POMAK_STUDY_ID, timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, STUDY_POMAK_RULE_ID, STUDY_POMAK_RULE_PRIORITY)
register(_rule)
