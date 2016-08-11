from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules._common import STUDY_RULE_PRIORITY
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.common import relates_to_library_in_study

IBD_X10_WGS_1_INTERVAL_RULE_ID = "study_ibd_x10_wgs_1"
IBD_X10_WGS_1_INTERVAL_RULE_PRIORITY = STUDY_RULE_PRIORITY

IBD_X10_WGS_1_STUDY_ID = "4113"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    return relates_to_library_in_study(cookie.enrichments, IBD_X10_WGS_1_STUDY_ID)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    timestamp = cookie.enrichments.get_most_recent_from_source(IRODS_UPDATE_ENRICHMENT).timestamp
    context.rule_writer("Additional library in iRODS for study %s (IBD x10 WGS Phase 1) at %s: %s"
                        % (IBD_X10_WGS_1_STUDY_ID, timestamp, cookie.identifier))
    return False


_rule = Rule(_matches, _action, IBD_X10_WGS_1_INTERVAL_RULE_ID, IBD_X10_WGS_1_INTERVAL_RULE_PRIORITY)
register(_rule)
