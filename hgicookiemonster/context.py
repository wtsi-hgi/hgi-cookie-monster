from cookiemonster.common.resource_accessor import ResourceAccessor
from cookiemonster.cookiejar import CookieJar

from hgicookiemonster.clients.message_queue import BasicMessageQueue
from hgicookiemonster.clients.slack import BasicSlackClient
from hgicookiemonster.config import CookieMonsterConfig


class HgiContext(ResourceAccessor):
    """
    Context for HGI Cookie Monster's rules, notification receivers and enrichment loaders.
    """
    def __init__(self, cookie_jar: CookieJar, config: CookieMonsterConfig, slack: BasicSlackClient,
                 message_queue: BasicMessageQueue):
        self.cookie_jar = cookie_jar
        self.config = config
        self.slack = slack
        self.message_queue = message_queue
