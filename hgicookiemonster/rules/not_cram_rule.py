import re

from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext

NOT_CRAM_RULE_ID = "not_cram"
NOT_CRAM_RULE_PRIORITY = Priority.MAX_PRIORITY

_CRAM_EXTENSION_PATTERN = re.compile(".*\.cram$", re.IGNORECASE)


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    """Matches cookies related to files without .cram extensions."""
    return not re.match(_CRAM_EXTENSION_PATTERN, cookie.identifier)


def _action(cookie: Cookie, context: HgiContext) -> bool:
    """Stop further processing."""
    return True


_rule = Rule(_matches, _action, NOT_CRAM_RULE_ID, NOT_CRAM_RULE_PRIORITY)
register(_rule)
