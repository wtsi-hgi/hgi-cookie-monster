import logging
from datetime import datetime
from os.path import dirname, join
from os.path import realpath
from threading import Thread
from configparser import ConfigParser

from cookiemonster.common.collections import UpdateCollection
from cookiemonster.common.models import Enrichment
from cookiemonster.common.sqlalchemy import SQLAlchemyDatabaseConnector
from cookiemonster.cookiejar import BiscuitTin
from cookiemonster.elmo import HTTP_API, APIDependency
from cookiemonster.notifications.notification_receiver import NotificationReceiverSource
from cookiemonster.processor._enrichment import EnrichmentLoaderSource
from cookiemonster.processor._rules import RuleSource
from cookiemonster.processor.basic_processing import BasicProcessorManager
from cookiemonster.retriever.log.sqlalchemy_mapper import SQLAlchemyRetrievalLogMapper
from cookiemonster.retriever.log.sqlalchemy_models import SQLAlchemyModel
from cookiemonster.retriever.manager import PeriodicRetrievalManager
from cookiemonster.retriever.source.irods.baton_mapper import BatonUpdateMapper
from sqlalchemy import create_engine

from hgicookiemonster.config import CONFIG_RETRIEVAL, CONFIG_RETRIEVAL_SINCE, CONFIG_RETRIEVAL_LOG_DATABASE, \
    CONFIG_PROCESSING, CONFIG_PROCESSING_PROCESSORS, CONFIG_COOKIEJAR, CONFIG_COOKIEJAR_HOST, CONFIG_COOKIEJAR_PORT, \
    CONFIG_COOKIEJAR_DATABASE, CONFIG_PROCESSING_RULES, CONFIG_PROCESSING_ENRICHMENT_LOADERS, \
    CONFIG_PROCESSING_NOTIFICATION_RECEIVERS, CONFIG_BATON, CONFIG_BATON_BINARIES_LOCATION, CONFIG_BATON_ZONE, \
    CONFIG_API, CONFIG_API_PORT
from hgicookiemonster.config import CONFIG_RETRIEVAL_PERIOD

_PROJECT_ROOT = join(dirname(realpath(__file__)))


def get_config(location: str) -> ConfigParser:
    config = ConfigParser()
    config.read(location)

    # os.path.isabs(my_path)
    # config.
    return config

def main():
    config = get_config("%s/../setup.conf" % _PROJECT_ROOT)

    retrieval_log_database_location = config[CONFIG_RETRIEVAL].get(CONFIG_RETRIEVAL_LOG_DATABASE)
    retrieval_period = config[CONFIG_RETRIEVAL].getfloat(CONFIG_RETRIEVAL_PERIOD)
    updates_since = config[CONFIG_RETRIEVAL].getint(CONFIG_RETRIEVAL_SINCE)

    number_of_processors = config[CONFIG_PROCESSING].getint(CONFIG_PROCESSING_PROCESSORS)

    cookiejar_database_host = config[CONFIG_COOKIEJAR].getint(CONFIG_COOKIEJAR_HOST)
    cookiejar_database_port = config[CONFIG_COOKIEJAR].getint(CONFIG_COOKIEJAR_PORT)
    cookiejar_database_name = config[CONFIG_COOKIEJAR].getint(CONFIG_COOKIEJAR_DATABASE)

    rules_directory = config[CONFIG_PROCESSING].getint(CONFIG_PROCESSING_RULES)
    enrichment_loaders_directory = config[CONFIG_PROCESSING].getint(CONFIG_PROCESSING_ENRICHMENT_LOADERS)
    notification_receivers_directory = config[CONFIG_PROCESSING].getint(CONFIG_PROCESSING_NOTIFICATION_RECEIVERS)

    baton_install_directory = config[CONFIG_BATON].getint(CONFIG_BATON_BINARIES_LOCATION)
    baton_zone =  config[CONFIG_BATON].getint(CONFIG_BATON_ZONE)

    http_api_port = config[CONFIG_API].getint(CONFIG_API_PORT)

    # Setup database for retrieval log
    engine = create_engine(retrieval_log_database_location)
    SQLAlchemyModel.metadata.create_all(bind=engine)

    # Setup data retrieval manager
    update_mapper = BatonUpdateMapper(baton_install_directory, baton_zone)
    database_connector = SQLAlchemyDatabaseConnector(retrieval_log_database_location)
    retrieval_log_mapper = SQLAlchemyRetrievalLogMapper(database_connector)
    retrieval_manager = PeriodicRetrievalManager(retrieval_period, update_mapper, retrieval_log_mapper)

    # Setup enrichment manager
    enrichment_loader_source = EnrichmentLoaderSource(enrichment_loaders_directory)
    enrichment_loader_source.start()

    # Setup cookie jar

    cookie_jar = BiscuitTin("%s:%s" % (cookiejar_database_host, cookiejar_database_port), cookiejar_database_name)

    # Setup rules source
    rules_source = RuleSource(rules_directory)
    rules_source.start()

    # Setup notification receiver source
    notification_receivers_source = NotificationReceiverSource(notification_receivers_directory)
    notification_receivers_source.start()

    # Setup the data processor manager
    processor_manager = BasicProcessorManager(
        number_of_processors, cookie_jar, rules_source, enrichment_loader_source, notification_receivers_source)

    # Connect the cookie jar to the retrieval manager
    def put_update_in_cookie_jar(update_collection: UpdateCollection):
        for update in update_collection:
            enrichment = Enrichment("irods_update", datetime.now(), update.metadata)
            logging.debug("Enriching \"%s\" with: %s" % (update.target, enrichment))
            Thread(target=cookie_jar.enrich_cookie, args=(update.target, enrichment)).start()
    retrieval_manager.add_listener(put_update_in_cookie_jar)

    # Connect the data processor manager to the cookie jar
    def prompt_processor_manager_to_process_cookie_updates(number_of_updates: int):
        logging.debug("Prompting process manager to process %d updated cookie(s)" % number_of_updates)
        processor_manager.process_any_cookies()
    cookie_jar.add_listener(prompt_processor_manager_to_process_cookie_updates)

    # Setup the HTTP API
    api = HTTP_API()
    api.inject(APIDependency.CookieJar, cookie_jar)
    api.listen(http_api_port)

    # Start the retrieval manager
    retrieval_manager.start(updates_since)


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s:%(message)s")
    logging.root.setLevel("DEBUG")
    main()
