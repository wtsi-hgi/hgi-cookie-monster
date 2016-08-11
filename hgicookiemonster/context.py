from cookiemonster.common.context import Context
from cookiemonster.cookiejar import CookieJar

from hgicookiemonster.clients.message_queue import BasicMessageQueue
from hgicookiemonster.clients.slack import BasicSlackClient
from hgicookiemonster.clients.rule_log import RuleOutputWriter
from hgicookiemonster.config import CookieMonsterConfig


class HgiContext(Context):
    """
    Context for HGI Cookie Monster's rules, notification receivers and enrichment loaders.
    """
    def __init__(self, cookie_jar: CookieJar, config: CookieMonsterConfig,
                 rule_log_writer: RuleOutputWriter, slack: BasicSlackClient,
                 message_queue: BasicMessageQueue):
        self.cookie_jar = cookie_jar
        self.config = config
        self.rule_writer = rule_log_writer
        self.slack = slack
        self.message_queue = message_queue
