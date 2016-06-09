from copy import deepcopy
from datetime import datetime

from baton.json import DataObjectJSONEncoder
from baton.collections import IrodsMetadata, DataObjectReplicaCollection
from baton.models import DataObject, DataObjectReplica
from cookiemonster.common.models import Enrichment
from cookiemonster.retriever.source.irods.json_convert import DataObjectModificationJSONEncoder
from cookiemonster.retriever.source.irods.models import DataObjectModification
from hgicommon.collections import Metadata
from hgicookiemonster.run import IRODS_UPDATE_ENRICHMENT
from hgicookiemonster.shared.constants.irods import IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE

UNINTERESTING_DATA_OBJECT_MODIFICATION_AS_METADATA = Metadata(
    DataObjectModificationJSONEncoder().default(DataObjectModification(IrodsMetadata({"other": {"value"}})))
)
UNINTERESTING_DATA_OBJECT_AS_METADATA = Metadata(
    DataObjectJSONEncoder().default(DataObject("/path", metadata=IrodsMetadata({"other": {"value"}})))
)
CREATION_DATA_OBJECT_MODIFICATION_AS_METADATA = Metadata(
    DataObjectModificationJSONEncoder().default(
        DataObjectModification(
            modified_replicas=DataObjectReplicaCollection({
                DataObjectReplica(IRODS_FIRST_REPLICA_TO_BE_CREATED_VALUE, "some_checksum")
            })
        )
    )
)


def create_creation_enrichment(timestamp: datetime) -> Enrichment:
    """
    Creates an enrichment indicating the creation of a data object in iRODS at the given timestamp.
    :param timestamp: timestamp of the creation
    :return: the created enrichment
    """
    return Enrichment(IRODS_UPDATE_ENRICHMENT, timestamp, deepcopy(CREATION_DATA_OBJECT_MODIFICATION_AS_METADATA))
