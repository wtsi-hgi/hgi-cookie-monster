from slackclient import SlackClient

_SLACK_CLIENT_POST_MESSAGE = "chat.postMessage"


class Slack:
    """
    TODO
    """
    def __init__(self, token: str, default_channel: str, default_username: str):
        """
        Constructor.
        :param token: authentication tocken from Slack
        """
        self._default_channel = default_channel
        self._default_username = default_username
        self._slack_client = SlackClient(token)

    def post_message(self, message: str, channel: str=None, username: str=None):
        """
        TODO
        :param channel:
        :param username:
        """
        if channel is None:
            channel = self._default_channel
        if username is None:
            username = self._default_username

        self._slack_client.api_call(_SLACK_CLIENT_POST_MESSAGE, channel=channel, text=message, username=username)


Slack("xoxp-2344385931-10295687988-26253588880-bd5719aad3", "test", "Cookie Monster").post_message("test")