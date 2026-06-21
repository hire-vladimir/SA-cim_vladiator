import csv
import re
from pathlib import Path


def _read_lookup_rows():
    path = Path(__file__).resolve().parent.parent / 'lookups' / 'cim_validator_field_regex.csv'
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def test_lookup_csv_has_three_columns_only():
    rows = _read_lookup_rows()
    assert rows
    assert set(rows[0].keys()) == {'datamodel', 'field', 'validation_regex'}


def test_ip_lookup_rows_have_ipv6_capable_regex():
    rows = _read_lookup_rows()
    by_key = {(r['datamodel'], r['field']): r for r in rows}
    assert by_key[('*', '*_ip')]['validation_regex'] == r'^[0-9A-Fa-f.:]+$'
    assert by_key[('*', 'src')]['validation_regex'] == r'^[\w\.:\-%]+$'
    assert by_key[('*', 'dest')]['validation_regex'] == r'^[\w\.:\-%]+$'
    assert by_key[('*', 'dvc')]['validation_regex'] == r'^[\w\.:\-%]+$'
    assert by_key[('UBA_Asset_Data', 'ip')]['validation_regex'] == r'^[0-9A-Fa-f.:]+$'


def test_parse_ip_validation_macro_exists():
    path = Path(__file__).resolve().parent.parent / 'default' / 'macros.conf'
    text = path.read_text(encoding='utf-8')
    assert '[cim_vladiator_parse_ip_validation]' in text
    block = re.search(
        r'\[cim_vladiator_parse_ip_validation\](.*?)(?:\n\[|\Z)',
        text,
        re.DOTALL,
    )
    assert block is not None
    assert 'definition = true' in block.group(1)
