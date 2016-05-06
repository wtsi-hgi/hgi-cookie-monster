from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority

from hgicookiemonster.enrichment_loaders.irods_loader_disabled import IRODS_SOURCE
from hgicookiemonster.context import HgiContext

INTERESTING_COOKIE = "interesting"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    if IRODS_SOURCE not in cookie.get_enrichment_sources():
        return False
    return "not_interesting" in cookie.identifier


def _action(cookie: Cookie, context: HgiContext) -> bool:
    context.slack.post("This looks interesting: %s" % cookie.identifier)


_rule = Rule(_matches, _action, Priority.MAX_PRIORITY, "example_rule")
register(_rule)
