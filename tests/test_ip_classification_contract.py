import csv
from pathlib import Path

import pytest

from cim_vladiator_common import IP_CLASSIFICATION_CONTRACT, derive_validation_mode

LOOKUP_PATH = Path(__file__).resolve().parent.parent / 'lookups' / 'cim_validator_field_regex.csv'


def _load_lookup_rows():
    with LOOKUP_PATH.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def test_contract_csv_ip_rows_present_with_expected_regex_families():
    rows = _load_lookup_rows()
    by_key = {(r['datamodel'], r['field']): r['validation_regex'] for r in rows}
    families = IP_CLASSIFICATION_CONTRACT['regex_families']
    for key, family in IP_CLASSIFICATION_CONTRACT['csv_ip_rows'].items():
        assert key in by_key, f'missing CSV row {key}'
        assert by_key[key] == families[family]


def test_lookup_csv_has_no_validation_mode_column():
    rows = _load_lookup_rows()
    assert rows
    assert 'validation_mode' not in rows[0].keys()


@pytest.mark.parametrize(
    'field,datamodel,expected',
    [
        ('endpoint_ip', 'Network_Traffic', 'ip_strict'),
        ('src_translated_ip', 'Network_Traffic', 'ip_strict'),
        ('ip', 'Network_Traffic', ''),
        ('ip', 'UBA_Asset_Data', 'ip_strict'),
        ('src', 'Network_Traffic', 'ip_polymorphic'),
        ('dest', 'Network_Traffic', 'ip_polymorphic'),
        ('dvc', 'Network_Traffic', 'ip_polymorphic'),
    ],
)
def test_derive_validation_mode_matches_contract(field, datamodel, expected):
    assert derive_validation_mode(field, datamodel, True) == expected