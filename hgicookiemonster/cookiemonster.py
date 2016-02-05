import logging
from datetime import datetime
from os.path import dirname, join
from os.path import realpath
from threading import Thread

from cookiemonster.common.collections import UpdateCollection
from cookiemonster.common.enums import EnrichmentSource
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

_PROJECT_ROOT = join(dirname(realpath(__file__)))


def main():
    retrieval_log_database_location = "sqlite:///%s/retrieval-log.sqlite" % _PROJECT_ROOT
    retrieval_period = 30.0
    updates_since = datetime.fromtimestamp(0)

    number_of_processors = 5

    manager_db_host = "http://192.168.0.11:5984"
    manager_db_name = "cookiemonster"

    rules_directory = "%s/rules" % _PROJECT_ROOT
    enrichment_loaders_directory = "%s/enrichment_loaders" % _PROJECT_ROOT
    notification_receivers_directory = "%s/notification_receivers" % _PROJECT_ROOT

    baton_install_directory = "/usr/local/bin"

    http_api_port = 5000

    # Setup database for retrieval log
    engine = create_engine(retrieval_log_database_location)
    SQLAlchemyModel.metadata.create_all(bind=engine)

    # Setup data retrieval manager
    update_mapper = BatonUpdateMapper(baton_install_directory, "iplant")
    database_connector = SQLAlchemyDatabaseConnector(retrieval_log_database_location)
    retrieval_log_mapper = SQLAlchemyRetrievalLogMapper(database_connector)
    retrieval_manager = PeriodicRetrievalManager(retrieval_period, update_mapper, retrieval_log_mapper)

    # Setup enrichment manager
    enrichment_loader_source = EnrichmentLoaderSource(enrichment_loaders_directory)
    enrichment_loader_source.start()

    # Setup cookie jar
    cookie_jar = BiscuitTin(manager_db_host, manager_db_name)

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
            enrichment = Enrichment(EnrichmentSource.IRODS_UPDATE, datetime.now(), update.metadata)
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
