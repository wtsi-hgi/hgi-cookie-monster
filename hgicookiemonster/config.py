from datetime import datetime
from configparser import ConfigParser

CONFIG_RETRIEVAL = "retrieval"
CONFIG_RETRIEVAL_PERIOD = "period"
CONFIG_RETRIEVAL_SINCE = "since"

CONFIG_COOKIEJAR = "cookiejar"
CONFIG_COOKIEJAR_URL = "url"
CONFIG_COOKIEJAR_DATABASE = "database"
CONFIG_COOKIEJAR_MAX_REQUESTS_PER_SECOND = "max_requests_per_second"

CONFIG_PROCESSING = "processing"
CONFIG_PROCESSING_MAX_THREADS = "max_threads"
CONFIG_PROCESSING_RULES = "rules"
CONFIG_PROCESSING_ENRICHMENT_LOADERS = "enrichment_loaders"

CONFIG_BATON = "baton"
CONFIG_BATON_BINARIES_LOCATION = "bin"
CONFIG_BATON_IRODS_ZONE = "zone"

CONFIG_API = "api"
CONFIG_API_PORT = "port"

CONFIG_INFLUXDB = "influxdb"
CONFIG_INFLUXDB_HOST = "host"
CONFIG_INFLUXDB_PORT = "port"
CONFIG_INFLUXDB_USERNAME = "username"
CONFIG_INFLUXDB_PASSWORD = "password"
CONFIG_INFLUXDB_DATABASE = "database"
CONFIG_INFLUXDB_BUFFER_LATENCY = "buffer_latency"

CONFIG_SLACK = "slack"
CONFIG_SLACK_TOKEN = "token"
CONFIG_SLACK_DEFAULT_CHANNEL = "default_channel"
CONFIG_SLACK_DEFAULT_USERNAME = "default_username"

CONFIG_MESSAGE_QUEUE = "message_queue"
CONFIG_MESSAGE_QUEUE_HOST = "host"
CONFIG_MESSAGE_QUEUE_PORT = "port"
CONFIG_MESSAGE_QUEUE_USERNAME = "username"
CONFIG_MESSAGE_QUEUE_PASSWORD = "password"


class CookieMonsterConfig:
    """
    Configuration for Cookie Monster.
    """
    class RetrievalConfig:
        def __init__(self):
            self.period = None  # type: float
            self.since = None   # type: datetime

    class CookieJarConfig:
        def __init__(self):
            self.url = None    # type: str
            self.database = None    # type: str
            self.max_requests_per_second = None     # type: int

    class ProcessingConfig:
        def __init__(self):
            self.max_threads = None   # type: int
            self.rules_location = None   # type: str
            self.enrichment_loaders_location = None   # type: str

    class BatonConfig:
        def __init__(self):
            self.binaries_location = None   # type: str
            self.zone = None    # type: str

    class ApiConfig:
        def __init__(self):
            self.port = None    # type: int

    class InfluxDBConfig:
        def __init__(self):
            self.host = None    # type: str
            self.port = None    # type: int
            self.username = None    # type: str
            self.password = None    # type: str
            self.database = None    # type: str
            self.buffer_latency = None  # type: int

    class SlackConfig:
        def __init__(self):
            self.token = None   # type: str
            self.default_channel = None     # type: str
            self.default_username = None     # type: str

    class MessageQueueConfig:
        def __init__(self):
            self.host = None  # type: str
            self.port = None  # type: int
            self.username = None  # type: str
            self.password = None  # type: str
            self.database = None  # type: str

    def __init__(self):
        self.retrieval = CookieMonsterConfig.RetrievalConfig()
        self.cookie_jar = CookieMonsterConfig.CookieJarConfig()
        self.processing = CookieMonsterConfig.ProcessingConfig()
        self.baton = CookieMonsterConfig.BatonConfig()
        self.api = CookieMonsterConfig.ApiConfig()
        self.influxdb = CookieMonsterConfig.InfluxDBConfig()
        self.slack = CookieMonsterConfig.SlackConfig()
        self.message_queue = CookieMonsterConfig.MessageQueueConfig()


def load_config(location: str) -> CookieMonsterConfig:
    """
    Loads Cookie Monster configuration from the settings file at the given location.
    :param location: the location of the settings file
    :return: the configuration
    """
    config_parser = ConfigParser()
    config_parser.read(location)

    config = CookieMonsterConfig()

    config.retrieval.period = config_parser[CONFIG_RETRIEVAL].getfloat(CONFIG_RETRIEVAL_PERIOD)
    config.retrieval.since = datetime.fromtimestamp(config_parser[CONFIG_RETRIEVAL].getint(CONFIG_RETRIEVAL_SINCE))

    config.processing.max_threads = config_parser[CONFIG_PROCESSING].getint(
        CONFIG_PROCESSING_MAX_THREADS)

    config.processing.rules_location = config_parser[CONFIG_PROCESSING].get(CONFIG_PROCESSING_RULES)
    config.processing.enrichment_loaders_location = config_parser[CONFIG_PROCESSING].get(
        CONFIG_PROCESSING_ENRICHMENT_LOADERS)

    config.cookie_jar.url = config_parser[CONFIG_COOKIEJAR].get(CONFIG_COOKIEJAR_URL)
    config.cookie_jar.database = config_parser[CONFIG_COOKIEJAR].get(CONFIG_COOKIEJAR_DATABASE)
    config.cookie_jar.max_requests_per_second = config_parser[CONFIG_COOKIEJAR].getint(
        CONFIG_COOKIEJAR_MAX_REQUESTS_PER_SECOND)

    config.baton.binaries_location = config_parser[CONFIG_BATON].get(CONFIG_BATON_BINARIES_LOCATION)
    config.baton.zone = config_parser[CONFIG_BATON].get(CONFIG_BATON_IRODS_ZONE)

    config.api.port = config_parser[CONFIG_API].getint(CONFIG_API_PORT)

    config.influxdb.host = config_parser[CONFIG_INFLUXDB].get(CONFIG_INFLUXDB_HOST)
    config.influxdb.port = config_parser[CONFIG_INFLUXDB].get(CONFIG_INFLUXDB_PORT)
    config.influxdb.username = config_parser[CONFIG_INFLUXDB].get(CONFIG_INFLUXDB_USERNAME)
    config.influxdb.password = config_parser[CONFIG_INFLUXDB].get(CONFIG_INFLUXDB_PASSWORD)
    config.influxdb.database = config_parser[CONFIG_INFLUXDB].get(CONFIG_INFLUXDB_DATABASE)
    config.influxdb.buffer_latency = config_parser[CONFIG_INFLUXDB].getint(CONFIG_INFLUXDB_BUFFER_LATENCY)

    config.slack.token = config_parser[CONFIG_SLACK].get(CONFIG_SLACK_TOKEN)
    config.slack.default_channel = config_parser[CONFIG_SLACK].get(CONFIG_SLACK_DEFAULT_CHANNEL)
    config.slack.default_username = config_parser[CONFIG_SLACK].get(CONFIG_SLACK_DEFAULT_USERNAME)

    config.message_queue.host = config_parser[CONFIG_MESSAGE_QUEUE].get(CONFIG_MESSAGE_QUEUE_HOST)
    config.message_queue.port = config_parser[CONFIG_MESSAGE_QUEUE].get(CONFIG_MESSAGE_QUEUE_PORT)
    config.message_queue.username = config_parser[CONFIG_MESSAGE_QUEUE].get(CONFIG_MESSAGE_QUEUE_USERNAME)
    config.message_queue.password = config_parser[CONFIG_MESSAGE_QUEUE].get(CONFIG_MESSAGE_QUEUE_PASSWORD)

    return config
