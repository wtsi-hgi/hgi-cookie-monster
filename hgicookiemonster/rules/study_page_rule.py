from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import extract_latest_metadata_key_value_known_in_irods
from hgicookiemonster.shared.constants.irods import IRODS_TARGET_KEY, IRODS_TARGET_LIBRARY_VALUE, IRODS_STUDY_ID_KEY

STUDY_INTERVAL_RULE_ID = "page"
STUDY_INTERVAL_RULE_PRIORITY = Priority.MIN_PRIORITY

INTERVAL_STUDY_ID = "3543"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    study_id = extract_latest_metadata_key_value_known_in_irods(cookie.enrichments, IRODS_STUDY_ID_KEY)
    target = extract_latest_metadata_key_value_known_in_irods(cookie.enrichments, IRODS_TARGET_KEY)
    return IRODS_TARGET_LIBRARY_VALUE in target and INTERVAL_STUDY_ID in study_id


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.slack.post("Additional library in iRODS for study %s (PAGE) at %s: %s"
                       % (INTERVAL_STUDY_ID, timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, STUDY_INTERVAL_RULE_ID, STUDY_INTERVAL_RULE_PRIORITY)
register(_rule)
