from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules.creation_observed_and_incorrect_human_reference_rule import \
    CREATION_OBSERVED_AND_INCORRECT_HUMAN_REFERENCE_RULE_PRIORITY
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import relates_to_library_in_study

STUDY_INTERVAL_RULE_ID = "study_page"
STUDY_INTERVAL_RULE_PRIORITY = CREATION_OBSERVED_AND_INCORRECT_HUMAN_REFERENCE_RULE_PRIORITY + 1

PAGE_STUDY_ID = "3543"


def _matches(cookie: Cookie, context: PAGE_STUDY_ID) -> bool:
    return relates_to_library_in_study(cookie.enrichments, PAGE_STUDY_ID)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.slack.post("Additional library in iRODS for study %s (PAGE) at %s: %s"
                       % (PAGE_STUDY_ID, timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, STUDY_INTERVAL_RULE_ID, STUDY_INTERVAL_RULE_PRIORITY)
register(_rule)
