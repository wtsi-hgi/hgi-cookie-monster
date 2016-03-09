from cookiemonster import Cookie, Notification, Rule, RuleAction
from hgicommon.mixable import Priority
from hgicommon.data_source import register


def _matches(cookie: Cookie) -> bool:
    return "study_of_interest" in cookie.identifier


def _generate_action(cookie: Cookie) -> RuleAction:
    return RuleAction([Notification("everyone", data=cookie.identifier, sender="this_rule")], True)


_rule = Rule(_matches, _generate_action, Priority.MAX_PRIORITY)
register(_rule)