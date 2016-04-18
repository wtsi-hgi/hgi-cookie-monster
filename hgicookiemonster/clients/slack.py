from slackclient import SlackClient

_SLACK_CLIENT_POST_MESSAGE = "chat.postMessage"


class BasicSlackClient:
    """
    Basic slack client.git
    """
    def __init__(self, token: str, default_channel: str, default_username: str):
        """
        Constructor.
        :param token: authentication tocken from BasicSlackClient
        """
        self._default_channel = default_channel
        self._default_username = default_username
        self._slack_client = SlackClient(token)

    def post(self, message: str, channel: str=None, username: str=None):
        """
        Post the given message to the given channel as the given username.
        :param message: the message to post
        :param channel: the channel to post to
        :param username: the username to post as
        """
        if channel is None:
            channel = self._default_channel
        if username is None:
            username = self._default_username

        self._slack_client.api_call(_SLACK_CLIENT_POST_MESSAGE, channel=channel, text=message, username=username)
