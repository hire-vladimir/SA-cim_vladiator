import csv
from pathlib import Path


def test_ip_lookup_rows_have_validation_mode():
    path = Path(__file__).resolve().parent.parent / 'lookups' / 'cim_validator_field_regex.csv'
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    by_key = {(r['datamodel'], r['field']): r for r in rows}
    assert by_key[('*', '*_ip')]['validation_mode'] == 'ip_strict'
    assert by_key[('*', 'src')]['validation_mode'] == 'ip_polymorphic'
    assert by_key[('UBA_Asset_Data', 'ip')]['validation_mode'] == 'ip_strict'
    assert by_key[('*', 'severity')]['validation_mode'] == ''