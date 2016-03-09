import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from cookiemonster.common.collections import UpdateCollection
from cookiemonster.common.models import Enrichment
from cookiemonster.common.sqlalchemy import SQLAlchemyDatabaseConnector
from cookiemonster.cookiejar import CookieJar
from cookiemonster.cookiejar.rate_limited_biscuit_tin import RateLimitedBiscuitTin
from cookiemonster.elmo import HTTP_API, APIDependency
from cookiemonster.logging.influxdb.logger import InfluxDBLogger
from cookiemonster.logging.influxdb.models import InfluxDBConnectionConfig
from cookiemonster.logging.logger import PythonLoggingLogger, Logger
from cookiemonster.notifications.notification_receiver import NotificationReceiverSource
from cookiemonster.processor._enrichment import EnrichmentLoaderSource
from cookiemonster.processor._rules import RuleSource
from cookiemonster.processor.basic_processing import BasicProcessorManager
from cookiemonster.processor.processing import ProcessorManager
from cookiemonster.retriever.log.sqlalchemy_mapper import SQLAlchemyRetrievalLogMapper
from cookiemonster.retriever.log.sqlalchemy_models import SQLAlchemyModel
from cookiemonster.retriever.manager import PeriodicRetrievalManager, RetrievalManager
from cookiemonster.retriever.source.irods.baton_mappers import BatonUpdateMapper
from sqlalchemy import create_engine

from hgicookiemonster.config import load_config

_MEASUREMENT_ENRICH_TIME = "enrich_time"


def run(config_location):
    # Load config
    config = load_config(config_location)

    # Setup measurement logging
    influxdb_config = InfluxDBConnectionConfig(config.influxdb.host, config.influxdb.port, config.influxdb.username,
                                               config.influxdb.password, config.influxdb.database)
    logger = InfluxDBLogger(influxdb_config)

    # Setup database for retrieval log
    engine = create_engine(config.retrieval.log_database)
    SQLAlchemyModel.metadata.create_all(bind=engine)

    # Setup data retrieval manager
    update_mapper = BatonUpdateMapper(config.baton.binaries_location, zone=config.baton.zone)
    database_connector = SQLAlchemyDatabaseConnector(config.retrieval.log_database)
    retrieval_log_mapper = SQLAlchemyRetrievalLogMapper(database_connector)
    retrieval_manager = PeriodicRetrievalManager(config.retrieval.period, update_mapper, retrieval_log_mapper, logger)

    # Setup enrichment manager
    enrichment_loader_source = EnrichmentLoaderSource(config.processing.enrichment_loaders_location)
    enrichment_loader_source.start()

    # Setup cookie jar
    cookie_jar = RateLimitedBiscuitTin(config.cookie_jar.max_requests_per_second, config.cookie_jar.url,
                                       config.cookie_jar.database)

    # Setup rules source
    rules_source = RuleSource(config.processing.rules_location)
    rules_source.start()

    # Setup notification receiver source
    notification_receivers_source = NotificationReceiverSource(config.processing.notification_receivers_location)
    notification_receivers_source.start()

    # Setup the data processor manager
    processor_manager = BasicProcessorManager(cookie_jar, rules_source, enrichment_loader_source,
                                              notification_receivers_source, config.processing.max_threads, logger)

    # Connect components to the cookie jar
    _connect_retrieval_manager_to_cookie_jar(retrieval_manager, cookie_jar, config.cookie_jar.max_requests_per_second,
                                             logger)
    _connect_processor_manager_to_cookie_jar(processor_manager, cookie_jar)

    # Setup the HTTP API
    api = HTTP_API()
    api.inject(APIDependency.CookieJar, cookie_jar)
    api.listen(config.api.port)

    # Start the retrieval manager
    retrieval_manager.start(config.retrieval.since)

    # Start processing of any unprocessed cookies
    processor_manager.process_any_cookies()


def _connect_processor_manager_to_cookie_jar(processor_manager: ProcessorManager, cookie_jar: CookieJar):
    """
    Connects the given processor manager to the given cookie jar.
    :param processor_manager: the processor manager
    :param cookie_jar: the cookie jar to connect to
    """
    # Connect the data processor manager to the cookie jar
    def prompt_processor_manager_to_process_cookie_updates(number_of_updates: int):
        logging.debug("Prompting process manager to process %d updated cookie(s)" % number_of_updates)
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
    def timed_enrichment(target: str, enrichment: Enrichment):
        logging.debug("Enriching \"%s\" with: %s" % (target, enrichment))
        started_at = time.monotonic()
        cookie_jar.enrich_cookie(target, enrichment)
        time_taken = time.monotonic() - started_at
        logger.record(_MEASUREMENT_ENRICH_TIME, time_taken)
        logging.info("Took %f seconds (wall time) to enrich cookie with path \"%s\"" % (time_taken, target))

    def put_updates_in_cookie_jar(update_collection: UpdateCollection):
        with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            for update in update_collection:
                enrichment = Enrichment("irods_update", datetime.now(), update.metadata)
                executor.submit(timed_enrichment, update.target, enrichment)

    retrieval_manager.add_listener(put_updates_in_cookie_jar)


if __name__ == "__main__":
    # Setup logging - rm do first thing due to issue discussed here:
    # https://stackoverflow.com/questions/1943747/python-logging-before-you-run-logging-basicconfig
    logging.basicConfig(format="%(asctime)s\t%(threadName)s\t%(message).500s", level=logging.DEBUG)
    # Stop requests library from logging lots of "Starting new HTTP connection (1): XX.XX.XX.XX"
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Eat cookies")
    parser.add_argument("configurationLocation", type=str, help="Location of the configuration file")
    args = parser.parse_args()

    # Go!
    run(args.configurationLocation)
