from cookiemonster import Notification, NotificationReceiver
from hgicommon.data_source import register

from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor
from hgicookiemonster.rules.example_rule import INTERESTING_COOKIE


def _retrieve(notification: Notification, resource_accessor: HgiCookieMonsterResourceAccessor):
    if notification.about == INTERESTING_COOKIE:
        resource_accessor.slack.post_message("This looks interesting: %s" % notification.data)


_notification_receiver = NotificationReceiver(_retrieve)
register(_notification_receiver)
