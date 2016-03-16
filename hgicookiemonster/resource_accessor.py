from cookiemonster.common.resource_accessor import ResourceAccessor
from cookiemonster.cookiejar import CookieJar

from hgicookiemonster.config import CookieMonsterConfig


class HgiCookieMonsterResourceAccessor(ResourceAccessor):
    """
    Resource accessor for HGI Cookie Monster's rules, notification receivers and enrichment loaders.
    """
    def __init__(self, cookie_jar: CookieJar, config: CookieMonsterConfig):
        self.cookie_jar = cookie_jar
        self.config = config
