import json
from pathlib import Path

import pytest

from mvrex import process_mvrex_row

FIXTURES = Path(__file__).parent / 'fixtures'


def _run_samples(field_cfg, expect_pass):
    row = {
        'sample_values': field_cfg['samples'],
        'validation_regex': field_cfg['validation_regex'],
        'validation_mode': field_cfg['validation_mode'],
    }
    argvals = {'field': 'sample_values', 'showunmatched': 't', 'showcount': 't'}
    process_mvrex_row(row, 'validation_regex', 'sample_values', 'mvrex', argvals)
    unmatched = row.get('mvrex_unmatched', [])
    if not isinstance(unmatched, list):
        unmatched = [unmatched] if unmatched else []
    for value in expect_pass:
        assert value not in unmatched, f'{value} should pass on {field_cfg["field"]}'
    for value in field_cfg['samples']:
        if value not in expect_pass:
            assert value in unmatched, f'{value} should fail on {field_cfg["field"]}'


def test_ipv6_network_traffic_fixture():
    data = json.loads((FIXTURES / 'ipv6_network_traffic_samples.json').read_text())
    expectations = {
        'src_ip': {
            'pass': ['fe80::7a45:58ff:fe84:37cb', 'FE80::7A45:58FF:FE84:37CB'],
        },
        'dest_ip': {
            'pass': ['ff02::1', 'ff02::fb'],
        },
        'src': {
            'pass': ['ff02::1', 'fe80::7a45:58ff:fe84:37cb', 'fe80::1%eth0', 'firewall01.corp.example', '10.0.0.5'],
        },
        'dest': {
            'pass': ['ff02::1'],
        },
    }
    for field_cfg in data:
        _run_samples(field_cfg, expectations[field_cfg['field']]['pass'])


def test_ipv4_regression_baseline():
    data = json.loads((FIXTURES / 'ipv4_regression_baseline.json').read_text())
    for field_cfg in data['fields']:
        row = {
            'sample_values': field_cfg['samples'],
            'validation_regex': field_cfg['validation_regex'],
            'validation_mode': field_cfg['validation_mode'],
        }
        argvals = {'field': 'sample_values', 'showunmatched': 't', 'showcount': 't'}
        process_mvrex_row(row, 'validation_regex', 'sample_values', 'mvrex', argvals)
        assert row['mvrex_unmatched_count'] <= field_cfg['max_unmatched_count']