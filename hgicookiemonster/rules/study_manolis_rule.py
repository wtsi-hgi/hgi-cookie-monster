from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules._common import STUDY_RULE_PRIORITY
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import relates_to_library_in_study

STUDY_MANOLIS_RULE_ID = "study_manolis"
STUDY_MANOLIS_RULE_PRIORITY = STUDY_RULE_PRIORITY

MANOLIS_STUDY_ID = "3596"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    return relates_to_library_in_study(cookie.enrichments, MANOLIS_STUDY_ID)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.slack.post("Additional library in iRODS for study %s (MANOLIS) at %s: %s"
                       % (MANOLIS_STUDY_ID, timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, STUDY_MANOLIS_RULE_ID, STUDY_MANOLIS_RULE_PRIORITY)
register(_rule)
