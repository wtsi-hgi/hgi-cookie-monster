from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext



def _matches(cookie: Cookie, context: HgiContext) -> bool:
    """TODO"""
    return cookie.identifier.startswith("/seq/illumina/library_merge")


def _action(cookie: Cookie, context: HgiContext) -> bool:
    """TODO"""

    return False


_rule = Rule(_matches, _action, "not_cram", priority=0)
register(_rule)
