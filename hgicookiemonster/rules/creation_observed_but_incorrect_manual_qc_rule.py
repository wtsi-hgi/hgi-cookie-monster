from cookiemonster.common.models import Cookie
from cookiemonster.processor.models import Rule
from hgicommon.data_source import register
from hgicookiemonster.context import HgiContext
from hgicookiemonster.rules.not_cram_rule import NOT_CRAM_RULE_PRIORITY
from hgicookiemonster.shared.common import was_creation_observed, extract_latest_metadata_key_value_known_in_irods

CREATION_OBSERVED_BUT_INCORRECT_MANUAL_QC = "creation_observed_but_incorrect_manual_qc"
CREATION_OBSERVED_BUT_INCORRECT_MANUAL_QC_RULE_PRIORITY = NOT_CRAM_RULE_PRIORITY + 1

_INCORRECT_MANUAL_QC_VALUE = 1
_IRODS_MANUAL_QC_KEY = "manual_qc"


def _matches(cookie: Cookie, context: HgiContext) -> bool:
    """Matches if the creation has been observed but there manual QC has not been set to 1."""
    if not was_creation_observed(cookie.enrichments):
        return False

    manual_qc = extract_latest_metadata_key_value_known_in_irods(cookie.enrichments, _IRODS_MANUAL_QC_KEY)
    if manual_qc is None:
        # No update to manual QC yet
        return False
    if len(manual_qc) != 1:
        # Multiple values for manual QC is unexpected
        return False
    return _INCORRECT_MANUAL_QC_VALUE in manual_qc


def _action(cookie: Cookie, context: HgiContext) -> bool:
    """Stop further processing."""
    return True


_rule = Rule(_matches, _action, CREATION_OBSERVED_BUT_INCORRECT_MANUAL_QC,
             CREATION_OBSERVED_BUT_INCORRECT_MANUAL_QC_RULE_PRIORITY)
register(_rule)
