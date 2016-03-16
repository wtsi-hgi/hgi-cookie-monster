from cookiemonster import Cookie, Notification, Rule, RuleAction
from hgicommon.data_source import register
from hgicommon.mixable import Priority

from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor

INTERESTING_COOKIE = "interesting"


def _matches(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> bool:
    return "interesting" in cookie.identifier


def _generate_action(cookie: Cookie, resource_accessor: HgiCookieMonsterResourceAccessor) -> RuleAction:
    return RuleAction([Notification(INTERESTING_COOKIE, data=cookie.identifier)], False)


_rule = Rule(_matches, _generate_action, Priority.MAX_PRIORITY)
register(_rule)