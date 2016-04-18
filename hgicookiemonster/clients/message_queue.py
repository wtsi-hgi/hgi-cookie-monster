from pika import PlainCredentials, ConnectionParameters, BlockingConnection


class BasicMessageQueue:
    """
    Basic message queue client (e.g. for use with RabbitMQ).
    """
    def __init__(self, username: str, password: str, host: str, port: int):
        """
        Constructor.
        :param username: username for message broker
        :param password: username for message broker
        :param host: location of message broker
        :param port: port message broker runs on
        """
        credentials = PlainCredentials(username, password)
        self._connection_parameters = ConnectionParameters(host, port, credentials=credentials)

    def post(self, message: str, queue_name: str):
        """
        Posts the given message to a queue with the given name via the message broker's default exchange.
        :param message: the message to post
        :param queue_name: the name of the queue to post to
        """
        connection = BlockingConnection(self._connection_parameters)
        try:
            channel = connection.channel()
            channel.basic_publish(exchange="", routing_key=queue_name, body=message)
        finally:
            connection.close()
