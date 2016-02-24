import argparse
import logging
from datetime import datetime
from threading import Thread

from cookiemonster.common.collections import UpdateCollection
from cookiemonster.common.models import Enrichment
from cookiemonster.common.sqlalchemy import SQLAlchemyDatabaseConnector
from cookiemonster.cookiejar import BiscuitTin, CookieJar
from cookiemonster.elmo import HTTP_API, APIDependency
from cookiemonster.notifications.notification_receiver import NotificationReceiverSource
from cookiemonster.processor._enrichment import EnrichmentLoaderSource
from cookiemonster.processor._rules import RuleSource
from cookiemonster.processor.basic_processing import BasicProcessorManager
from cookiemonster.processor.processing import ProcessorManager
from cookiemonster.retriever.log.sqlalchemy_mapper import SQLAlchemyRetrievalLogMapper
from cookiemonster.retriever.log.sqlalchemy_models import SQLAlchemyModel
from cookiemonster.retriever.manager import PeriodicRetrievalManager, RetrievalManager
from cookiemonster.retriever.source.irods.baton_mapper import BatonUpdateMapper
from sqlalchemy import create_engine

from hgicookiemonster.config import load_config


def run(config_location):
    # Load config
    config = load_config(config_location)

    # Setup database for retrieval log
    engine = create_engine(config.retrieval.log_database)
    SQLAlchemyModel.metadata.create_all(bind=engine)

    # Setup data retrieval manager
    update_mapper = BatonUpdateMapper(config.baton.binaries_location)
    database_connector = SQLAlchemyDatabaseConnector(config.retrieval.log_database)
    retrieval_log_mapper = SQLAlchemyRetrievalLogMapper(database_connector)
    retrieval_manager = PeriodicRetrievalManager(config.retrieval.period, update_mapper, retrieval_log_mapper)

    # Setup enrichment manager
    enrichment_loader_source = EnrichmentLoaderSource(config.processing.enrichment_loaders_location)
    enrichment_loader_source.start()

    # Setup cookie jar
    cookie_jar = BiscuitTin(config.cookie_jar.url, config.cookie_jar.database)

    # Setup rules source
    rules_source = RuleSource(config.processing.rules_location)
    rules_source.start()

    # Setup notification receiver source
    notification_receivers_source = NotificationReceiverSource(config.processing.notification_receivers_location)
    notification_receivers_source.start()

    # Setup the data processor manager
    processor_manager = BasicProcessorManager(config.processing.number_of_processors, cookie_jar, rules_source,
                                              enrichment_loader_source, notification_receivers_source)

    # Connect components tot he cookie jar
    _connect_retrieval_manager_to_cookie_jar(retrieval_manager, cookie_jar)
    _connect_processor_manager_to_cookie_jar(processor_manager, cookie_jar)

    # Setup the HTTP API
    api = HTTP_API()
    api.inject(APIDependency.CookieJar, cookie_jar)
    api.listen(config.api.port)

    # Setup logging
    logging.basicConfig(format="%(threadName)s:%(message)s")
    logging.root.setLevel("DEBUG")

    # Start the retrieval manager
    retrieval_manager.start(config.retrieval.since)


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


def _connect_retrieval_manager_to_cookie_jar(retrieval_manager: RetrievalManager, cookie_jar: CookieJar):
    """
    Connect the given retrieval manager to the given cookie jar.
    :param retrieval_manager: the retrieval manager
    :param cookie_jar: the cookie jar to connect to
    """
    def put_updates_in_cookie_jar(update_collection: UpdateCollection):
        for update in update_collection:
            enrichment = Enrichment("irods_update", datetime.now(), update.metadata)
            logging.debug("Enriching \"%s\" with: %s" % (update.target, enrichment))
            Thread(target=cookie_jar.enrich_cookie, args=(update.target, enrichment)).start()
    retrieval_manager.add_listener(put_updates_in_cookie_jar)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eat cookies")
    parser.add_argument("configurationLocation", type=str, help="Location of the configuration file")
    args = parser.parse_args()
    run(args.configurationLocation)
