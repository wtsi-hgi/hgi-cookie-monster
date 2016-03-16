from cookiemonster import Cookie, Notification, Rule, RuleAction
from cookiemonster.common.resource_accessor import ResourceAccessor
from hgicommon.mixable import Priority
from hgicommon.data_source import register

INTERESTING_COOKIE = "interesting"


def _matches(cookie: Cookie, resource_accessor: ResourceAccessor) -> bool:
    return "interesting" in cookie.identifier


def _generate_action(cookie: Cookie, resource_accessor: ResourceAccessor) -> RuleAction:
    return RuleAction([Notification(INTERESTING_COOKIE, data=cookie.identifier)], False)


_rule = Rule(_matches, _generate_action, Priority.MAX_PRIORITY)
register(_rule)