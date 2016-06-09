import re
from os.path import normpath, dirname, join, realpath

from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules.not_cram_rule import NOT_CRAM_RULE_PRIORITY
from hgicookiemonster.shared.common import was_creation_observed, extract_latest_metadata_key_value_known_in_irods
from hgicookiemonster.shared.constants.irods import IRODS_MANUAL_QC_KEY

CREATION_OBSERVED_BUT_NO_HUMAN_REFERENCE_RULE_ID = "creation_observed_but_no_human_reference"
CREATION_OBSERVED_BUT_NO_HUMAN_REFERENCE_RULE_PRIORITY = NOT_CRAM_RULE_PRIORITY + 1

_CORRECT_MANUAL_QC_VALUE = 1
_KNOWN_UNINTERESTING_REFERENCES_PATH = normpath(join(dirname(realpath(__file__)), "resources/non-human-species.txt"))
_REFERENCE_EXTRACTION_PATTERN = re.compile(".*/references/(.*?)/.*", re.IGNORECASE)


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    """
    Matches if the creation of the data object in iRODS has been observed but the reference has been set to one that we
    are not interested in.
    """
    if not was_creation_observed(cookie.enrichments):
        return False

    reference = extract_latest_metadata_key_value_known_in_irods(cookie.enrichments, IRODS_MANUAL_QC_KEY)
    if reference is None:
        # No update to reference yet
        return False
    if len(reference) != 1:
        # Multiple values for reference is unexpected
        return False

    reference_species_groups = re.match(_REFERENCE_EXTRACTION_PATTERN, reference[0])
    if reference_species_groups is None:
        # Reference is in unexpected format
        return False
    reference_species = reference_species_groups.group(0)

    # Read uninteresting references from file every time to (easily) support live updates to this list
    with open(_KNOWN_UNINTERESTING_REFERENCES_PATH) as file:
        uninteresting_references = file.read().splitlines()

    return reference_species in uninteresting_references


def _action(cookie: Cookie, context: HgiContext) -> bool:
    """Stop further processing."""
    return True


_rule = Rule(_matches, _action, CREATION_OBSERVED_BUT_NO_HUMAN_REFERENCE_RULE_ID,
             CREATION_OBSERVED_BUT_NO_HUMAN_REFERENCE_RULE_PRIORITY)
register(_rule)
