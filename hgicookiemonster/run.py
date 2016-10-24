import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Lock

from cookiemonster.common.collections import UpdateCollection
from cookiemonster.common.models import Enrichment
from cookiemonster.contrib.connection_pool import patch_http_connection_pool
from cookiemonster.cookiejar import CookieJar, RateLimitedBiscuitTin
from cookiemonster.cookiejar.biscuit_tin import add_couchdb_logging
from cookiemonster.cookiejar.logging_cookie_jar import add_cookie_jar_logging
from cookiemonster.elmo import HTTP_API, APIDependency
from cookiemonster.logging.influxdb.logger import InfluxDBLogger
from cookiemonster.logging.influxdb.models import InfluxDBConnectionConfig
from cookiemonster.logging.logger import PythonLoggingLogger, Logger
from cookiemonster.monitor.cookiejar_monitor import CookieJarMonitor
from cookiemonster.monitor.threads_monitor import ThreadsMonitor
from cookiemonster.processor._enrichment import EnrichmentLoaderSource
from cookiemonster.processor._rules import RuleSource
from cookiemonster.processor.basic_processing import BasicProcessorManager
from cookiemonster.processor.processing import ProcessorManager
from cookiemonster.retriever.manager import PeriodicRetrievalManager, RetrievalManager
from cookiemonster.retriever.source.irods.baton_mappers import BatonUpdateMapper

from hgicookiemonster.clients.message_queue import BasicMessageQueue
from hgicookiemonster.clients.slack import BasicSlackClient
from hgicookiemonster.clients.rule_log import RuleOutputWriter
from hgicookiemonster.config import load_config
from hgicookiemonster.context import HgiContext

MEASUREMENT_ENRICH_TIME = "enrich_time"
MEASUREMENT_STILL_TO_ENRICH = "still_to_enrich"
IRODS_UPDATE_ENRICHMENT = "irods_update"


def run(config_location):
    # Load config
    config = load_config(os.path.join(config_location, "setup.conf"))

    # Setup measurement logging
    logging_buffer_latency = timedelta(seconds=config.influxdb.buffer_latency)
    influxdb_config = InfluxDBConnectionConfig(config.influxdb.host, config.influxdb.port, config.influxdb.username,
                                               config.influxdb.password, config.influxdb.database)
    logger = InfluxDBLogger(influxdb_config, buffer_latency=logging_buffer_latency)

    # Set HTTP connection pool size (for CouchDB)
    # NOTE This is taken from an environment variable, as it's not
    # something that would probably need tweaking that much:
    pool_size = int(os.environ.get('COOKIEMONSTER_HTTP_POOL_SIZE', 16))
    patch_http_connection_pool(maxsize=pool_size)

    # Setup cookie jar
    cookie_jar = RateLimitedBiscuitTin(config.cookie_jar.max_requests_per_second, config.cookie_jar.url,
                                       config.cookie_jar.database,
                                       config.cookie_jar.buffer_capacity, config.cookie_jar.buffer_latency)
    add_cookie_jar_logging(cookie_jar, logger)
    add_couchdb_logging(cookie_jar, logger)

    # Setup data retrieval manager
    update_mapper = BatonUpdateMapper(config.baton.binaries_location, zone=config.baton.zone)
    retrieval_manager = PeriodicRetrievalManager(config.retrieval.period, update_mapper, logger)

    # # Setup basic Slack client
    # slack = BasicSlackClient(config.slack.token, config.slack.default_channel, config.slack.default_username)
    slack = None

    # Setup rule output log file writer
    rule_log_writer = RuleOutputWriter(config.output.log_file)

    # # Setup basic message queue (e.g. RabbitMQ) client
    # message_queue = BasicMessageQueue(config.message_queue.host, config.message_queue.port,
    #                                   config.message_queue.username, config.message_queue.password)
    message_queue = None

    # Define the context that rules and enrichment loaders has access to
    context = HgiContext(cookie_jar, config, rule_log_writer, slack, message_queue)

    # Setup rules source
    rules_source = RuleSource(config.processing.rules_location, context)
    rules_source.start()

    # Setup enrichment loader source
    enrichment_loader_source = EnrichmentLoaderSource(config.processing.enrichment_loaders_location, context)
    enrichment_loader_source.start()

    # Setup the data processor manager
    processor_manager = BasicProcessorManager(cookie_jar, rules_source, enrichment_loader_source,
                                              config.processing.max_threads, logger)

    # Connect components to the cookie jar
    _connect_retrieval_manager_to_cookie_jar(retrieval_manager, cookie_jar, config.cookie_jar.max_requests_per_second,
                                             logger)
    _connect_retrieval_manager_to_since_file(retrieval_manager, config_location)
    _connect_processor_manager_to_cookie_jar(processor_manager, cookie_jar)

    # Setup the HTTP API
    api = HTTP_API()
    api.inject(APIDependency.CookieJar, cookie_jar)
    api.inject(APIDependency.System, None)
    api.listen(config.api.port)

    # Start the retrieval manager from the last known successful
    # retrieval time (or invocation time, otherwise)
    try:
        with open(os.path.join(config_location, "since"), "r") as f:
            since_time = datetime.fromtimestamp(int(f.read()))
    except:
        since_time = datetime.now()

    retrieval_manager.start(since_time)

    # Start processing of any unprocessed cookies
    processor_manager.process_any_cookies()

    # Setup monitors
    ThreadsMonitor(logger, logging_buffer_latency).start()
    CookieJarMonitor(logger, logging_buffer_latency, cookie_jar).start()


def _connect_processor_manager_to_cookie_jar(processor_manager: ProcessorManager, cookie_jar: CookieJar):
    """
    Connects the given processor manager to the given cookie jar.
    :param processor_manager: the processor manager
    :param cookie_jar: the cookie jar to connect to
    """
    # Connect the data processor manager to the cookie jar
    def prompt_processor_manager_to_process_cookie_updates():
        logging.debug("Prompting process manager to process updated cookies")
        processor_manager.process_any_cookies()
    cookie_jar.add_listener(prompt_processor_manager_to_process_cookie_updates)


def _connect_retrieval_manager_to_cookie_jar(retrieval_manager: RetrievalManager, cookie_jar: CookieJar,
                                             number_of_threads: int=None, logger: Logger=PythonLoggingLogger()):
    """
    Connect the given retrieval manager to the given cookie jar.
    :param retrieval_manager: the retrieval manager
    :param cookie_jar: the cookie jar to connect to
    :param number_of_threads: the number of threads to use when putting cookies into the jar
    """
    still_to_enrich = 0
    still_to_enrich_lock = Lock()
    thread_pool = ThreadPoolExecutor(max_workers=number_of_threads)

    def timed_enrichment(target: str, enrichment: Enrichment):
        nonlocal still_to_enrich
        logging.debug("Enriching \"%s\" with: %s" % (target, enrichment))
        started_at = time.monotonic()

        try:
            # Let's leave this here, as it's very important that the
            # enrichment succeeds and we need to know about it in detail
            # if/when it doesn't!
            cookie_jar.enrich_cookie(target, enrichment)
        except:
            logging.exception("Enrichment of \"%s\" failed!!", target)
            raise

        time_taken = time.monotonic() - started_at
        logger.record(MEASUREMENT_ENRICH_TIME, time_taken)
        logging.info("Took %f seconds (wall time) to enrich cookie with path \"%s\"" % (time_taken, target))
        with still_to_enrich_lock:
            still_to_enrich -= 1
            logger.record(MEASUREMENT_STILL_TO_ENRICH, still_to_enrich)

    def put_updates_in_cookie_jar(update_collection: UpdateCollection):
        nonlocal still_to_enrich
        for update in update_collection:
            enrichment = Enrichment(IRODS_UPDATE_ENRICHMENT, update.timestamp, update.metadata)
            with still_to_enrich_lock:
                still_to_enrich += 1
                logger.record(MEASUREMENT_STILL_TO_ENRICH, still_to_enrich)
            thread_pool.submit(timed_enrichment, update.target, enrichment)

    retrieval_manager.add_listener(put_updates_in_cookie_jar)


def _connect_retrieval_manager_to_since_file(retrieval_manager: RetrievalManager,
                                             config_location: str):
    """
    Connect the given retrieval manager to the "since" file

    @param  retrieval_manager  The retrieval manager
    @param  config_location    Directory containing since file
    """
    since_file = os.path.join(config_location, "since")

    def update_since_file(update_collection: UpdateCollection):
        nonlocal since_file
        
        if update_collection:
            last_retrieval_time = update_collection.get_most_recent()[0].timestamp

            with open(since_file, "w") as f:
                f.write(str(int(last_retrieval_time.timestamp())))

    retrieval_manager.add_listener(update_since_file)


if __name__ == "__main__":
    # Setup logging - rm do first thing due to issue discussed here:
    # https://stackoverflow.com/questions/1943747/python-logging-before-you-run-logging-basicconfig
    logging.basicConfig(format="%(asctime)s\t%(threadName)s\t%(message).500s", level=logging.DEBUG)
    # Stop requests library from logging lots of "Starting new HTTP connection (1): XX.XX.XX.XX"
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Check ~/.cookie-monster exists and contains setup.conf
    configurationLocation = os.path.join(os.path.expanduser("~"), ".cookie-monster")
    if not os.path.isdir(configurationLocation):
        raise NotADirectoryError("{} does not exist or is not a directory".format(configurationLocation))
    if not os.path.exists(os.path.join(configurationLocation, "setup.conf")):
        raise FileNotFoundError("No setup.conf found in {}".format(configurationLocation))

    # Go!
    run(configurationLocation)
