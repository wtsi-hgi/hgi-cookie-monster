from datetime import datetime
from configparser import ConfigParser

CONFIG_RETRIEVAL = "retrieval"
CONFIG_RETRIEVAL_LOG_DATABASE = "log"
CONFIG_RETRIEVAL_PERIOD = "period"
CONFIG_RETRIEVAL_SINCE = "since"

CONFIG_COOKIEJAR = "cookiejar"
CONFIG_COOKIEJAR_URL = "url"
CONFIG_COOKIEJAR_DATABASE = "database"
CONFIG_COOKIEJAR_MAX_REQUESTS_PER_SECOND = "max_requests_per_second"

CONFIG_PROCESSING = "processing"
CONFIG_PROCESSING_PROCESSORS = "processors"
CONFIG_PROCESSING_RULES = "rules"
CONFIG_PROCESSING_NOTIFICATION_RECEIVERS = "notification_receivers"
CONFIG_PROCESSING_ENRICHMENT_LOADERS = "enrichment_loaders"

CONFIG_API = "api"
CONFIG_API_PORT = "port"

CONFIG_BATON = "baton"
CONFIG_BATON_BINARIES_LOCATION = "bin"
CONFIG_BATON_IRODS_ZONE = "zone"


class CookieMonsterConfig:
    """
    Configuration for Cookie Monster.
    """
    class RetrievalConfig:
        def __init__(self):
            self.log_database = None    # type: str
            self.period = None  # type: float
            self.since = None   # type: datetime

    class CookieJarConfig:
        def __init__(self):
            self.url = None    # type: str
            self.database = None    # type: str
            self.max_requests_per_second = None     # type: int

    class ProcessingConfig:
        def __init__(self):
            self.number_of_processors = None   # type: int
            self.rules_location = None   # type: str
            self.enrichment_loaders_location = None   # type: str
            self.notification_receivers_location = None   # type: str

    class BatonConfig:
        def __init__(self):
            self.binaries_location = None   # type: str
            self.zone = None    # type: str

    class ApiConfig:
        def __init__(self):
            self.port = None    # type: int

    def __init__(self):
        self.retrieval = CookieMonsterConfig.RetrievalConfig()
        self.cookie_jar = CookieMonsterConfig.CookieJarConfig()
        self.processing = CookieMonsterConfig.ProcessingConfig()
        self.baton = CookieMonsterConfig.BatonConfig()
        self.api = CookieMonsterConfig.ApiConfig()


def load_config(location: str) -> CookieMonsterConfig:
    """
    Loads Cookie Monster configuration from the settings file at the given location.
    :param location: the location of the settings file
    :return: the configuration
    """
    config_parser = ConfigParser()
    config_parser.read(location)

    config = CookieMonsterConfig()

    config.retrieval.log_database = config_parser[CONFIG_RETRIEVAL].get(CONFIG_RETRIEVAL_LOG_DATABASE)
    config.retrieval.period = config_parser[CONFIG_RETRIEVAL].getfloat(CONFIG_RETRIEVAL_PERIOD)
    config.retrieval.since = datetime.fromtimestamp(config_parser[CONFIG_RETRIEVAL].getint(CONFIG_RETRIEVAL_SINCE))

    config.processing.number_of_processors = config_parser[CONFIG_PROCESSING].getint(CONFIG_PROCESSING_PROCESSORS)

    config.processing.rules_location = config_parser[CONFIG_PROCESSING].get(CONFIG_PROCESSING_RULES)
    config.processing.enrichment_loaders_location = config_parser[CONFIG_PROCESSING].get(
        CONFIG_PROCESSING_ENRICHMENT_LOADERS)
    config.processing.notification_receivers_location = config_parser[CONFIG_PROCESSING].get(
        CONFIG_PROCESSING_NOTIFICATION_RECEIVERS)

    config.cookie_jar.url = config_parser[CONFIG_COOKIEJAR].get(CONFIG_COOKIEJAR_URL)
    config.cookie_jar.database = config_parser[CONFIG_COOKIEJAR].get(CONFIG_COOKIEJAR_DATABASE)
    config.cookie_jar.max_requests_per_second = config_parser[CONFIG_COOKIEJAR].get(
        CONFIG_COOKIEJAR_MAX_REQUESTS_PER_SECOND)

    config.baton.binaries_location = config_parser[CONFIG_BATON].get(CONFIG_BATON_BINARIES_LOCATION)
    config.baton.zone = config_parser[CONFIG_BATON].get(CONFIG_BATON_IRODS_ZONE)

    config.api.port = config_parser[CONFIG_API].getint(CONFIG_API_PORT)

    return config
