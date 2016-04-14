from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority

from hgicookiemonster.enrichment_loaders.irods_loader import IRODS_SOURCE
from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor

INTERESTING_COOKIE = "interesting"


def _matches(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> bool:
    if IRODS_SOURCE not in cookie.get_enrichment_sources():
        return False
    return "not_interesting" in cookie.identifier


def _action(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> bool:
    resource_accessor.slack.post_message("This looks interesting: %s" % cookie.identifier)


_rule = Rule(_matches, _action, Priority.MAX_PRIORITY, "example_rule")
register(_rule)
