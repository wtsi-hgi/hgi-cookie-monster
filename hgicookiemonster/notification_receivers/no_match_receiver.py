from cookiemonster import Notification, NotificationReceiver
from cookiemonster.processor.processing import ABOUT_NO_RULES_MATCH
from hgicommon.data_source import register

from hgicookiemonster.resource_accessor import HgiCookieMonsterResourceAccessor


def _retrieve(notification: Notification, resource_accessor: HgiCookieMonsterResourceAccessor):
    if notification.about == ABOUT_NO_RULES_MATCH:
        print("No rules matched for: %s" % notification.data)


_notification_receiver = NotificationReceiver(_retrieve)
register(_notification_receiver)
