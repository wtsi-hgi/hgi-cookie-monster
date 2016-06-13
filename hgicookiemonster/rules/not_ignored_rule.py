import json
import os
from collections import UserDict
from os.path import dirname, normpath, realpath, join
from typing import Dict, List, Any, Iterable
from urllib.parse import quote
from urllib.request import urlopen, Request

from cookiemonster.common.helpers import EnrichmentJSONDecoder
from cookiemonster.common.models import Cookie, Enrichment
from cookiemonster.processor.json_convert import RuleApplicationLogJSONDecoder
from cookiemonster.processor.models import Rule
from cookiemonster.processor.models import RuleApplicationLog
from cookiemonster.processor.processing import RULE_APPLICATION
from hgicommon.data_source import register
from hgicommon.mixable import Priority
from hgicookiemonster.context import HgiContext

NOT_IGNORED_RULE_ID = "not_ignored"
NOT_IGNORED_RULE_PRIORITY = Priority.MIN_PRIORITY

NOT_IGNORED_LIST_LOCATION = normpath(join(dirname(realpath(__file__)), "not_ignored.txt"))

_RULE_APPLICATION_LOG_JSON_DECODER = RuleApplicationLogJSONDecoder()


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    """Matches if this rule has not been matched before."""
    rule_application_enrichments = [enrichment for enrichment in cookie.enrichments if enrichment.source == RULE_APPLICATION]
    for enrichment in rule_application_enrichments:
        rule_application_log = _RULE_APPLICATION_LOG_JSON_DECODER.decode_parsed(enrichment.metadata)    # type: RuleApplicationLog
        if rule_application_log.rule_id == NOT_IGNORED_RULE_ID:
            # Limit to reporting once per identifier
            return False
    return True


def _action(cookie: Cookie, context: HgiContext) -> bool:
    """Write timestamp and identifier to tab separated file."""
    with open(NOT_IGNORED_LIST_LOCATION, "a") as file:
        file.write("%s%s" % (cookie.identifier, os.linesep))
    return False


class CookieLoadingDict(UserDict):
    """
    Dictionary where keys should be identifiers to cookies that are accessible via the Cookie Monster API. Values are
    loaded from the API on-the-fly and cached.
    """
    _ENRICHMENT_JSON_DECODER = EnrichmentJSONDecoder()

    def __init__(self, api_location: str, identifiers: Iterable[str]):
        super().__init__({(identifier, None) for identifier in identifiers})
        self.api_location = api_location

    def __getitem__(self, key: Any) -> Cookie:
        if self.data[key] is None:
            self[key] = self._load_cookie(key)
        return self.data[key]

    def _load_cookie(self, identifier: str) -> Cookie:
        """
        Loads a cookie with the given identifier.
        :param identifier: the identifier of the cookie to load
        :return: the loaded cookie
        """
        # FIXME: There should be a `CookieJar` to do all this (see issue:
        # https://github.com/wtsi-hgi/cookie-monster/issues/44)
        url = "%s?identifier=%s" % (self.api_location, quote(identifier))
        request = Request(url, None, {"Accept": "application/json"})
        cookie_as_json = json.loads(urlopen(request).read().decode("utf-8"))
        # FIXME: There should be a `CookieJSONDecoder`
        cookie = Cookie(identifier)
        for enrichment in CookieLoadingDict._ENRICHMENT_JSON_DECODER.decode_parsed(cookie_as_json["enrichments"]):
            assert isinstance(enrichment, Enrichment)
            cookie.enrich(enrichment)
        return cookie


def read_not_ignored(cookie_monster_api_location: str, not_ignored_list_location: str=NOT_IGNORED_LIST_LOCATION) \
        -> Dict[str, Cookie]:
    """
    Gets not ignored cookies in a dict where the keys are the identifiers of the ignored cookies and the values are the
    cookies themselves (loaded on-the-fly).
    :param cookie_monster_api_location: the location of the Cookie Monster API
    :param not_ignored_list_location: the location of the not ignored list to read
    :return: not ignored cookies
    """
    identifiers = []    # type: List[str]
    with open(not_ignored_list_location, "r") as file:
        for line in file:
            identifiers.append(line)
    return CookieLoadingDict(cookie_monster_api_location, identifiers)


_rule = Rule(_matches, _action, NOT_IGNORED_RULE_ID, NOT_IGNORED_RULE_PRIORITY)
register(_rule)
