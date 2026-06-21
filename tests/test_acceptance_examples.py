import json
from pathlib import Path

from mvrex import process_mvrex_row

FIXTURES = Path(__file__).parent / 'fixtures'


def _run_samples(field_cfg, expect_pass, parseip='t'):
    row = {
        'field': field_cfg['field'],
        'datamodel': field_cfg['datamodel'],
        'sample_values': field_cfg['samples'],
        'validation_regex': field_cfg['validation_regex'],
    }
    argvals = {'field': 'sample_values', 'showunmatched': 't', 'showcount': 't', 'parseip': parseip}
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
            'pass': [
                'fe80::7a45:58ff:fe84:37cb',
                'FE80::7A45:58FF:FE84:37CB',
                'ff02::1',
            ],
        },
        'dest_ip': {
            'pass': ['ff02::1', 'fe80::7a45:58ff:fe84:37cb', 'ff02::fb'],
        },
        'src': {
            'pass': [
                'ff02::1',
                'fe80::7a45:58ff:fe84:37cb',
                'fe80::1%eth0',
                'firewall01.corp.example',
                '10.0.0.5',
            ],
        },
        'dest': {
            'pass': ['ff02::1', 'fe80::7a45:58ff:fe84:37cb'],
        },
        'ip': {
            'pass': ['2001:db8::1'],
        },
        'dvc': {
            'pass': ['10.1.1.1', 'router-core-01'],
        },
    }
    for field_cfg in data:
        _run_samples(field_cfg, expectations[field_cfg['field']]['pass'])


def test_macro_off_ipv6_still_passes_stage1():
    """Valid IPv6 literals pass regex stage when parseip is disabled (no stage-2)."""
    data = json.loads((FIXTURES / 'ipv6_network_traffic_samples.json').read_text())
    by_field = {cfg['field']: cfg for cfg in data}
    ipv6_literals = ['ff02::1', 'fe80::7a45:58ff:fe84:37cb']
    for field in ('src_ip', 'dest_ip', 'src', 'dest'):
        cfg = by_field[field]
        focused = {**cfg, 'samples': ipv6_literals}
        _run_samples(focused, ipv6_literals, parseip='f')


def test_macro_off_weaker_junk_rejection():
    """Macro-off uses findall-only semantics; partial IPs matching regex may pass."""
    partial_ip_cfg = {
        'field': 'dest_ip',
        'datamodel': 'Network_Traffic',
        'validation_regex': r'^[0-9A-Fa-f.:]+$',
        'samples': ['192.168.1'],
    }
    _run_samples(partial_ip_cfg, ['192.168.1'], parseip='f')
    _run_samples(partial_ip_cfg, [], parseip='t')


def test_ipv4_regression_baseline():
    data = json.loads((FIXTURES / 'ipv4_regression_baseline.json').read_text())
    for field_cfg in data['fields']:
        row = {
            'field': field_cfg['field'],
            'datamodel': field_cfg['datamodel'],
            'sample_values': field_cfg['samples'],
            'validation_regex': field_cfg['validation_regex'],
        }
        argvals = {'field': 'sample_values', 'showunmatched': 't', 'showcount': 't', 'parseip': 't'}
        process_mvrex_row(row, 'validation_regex', 'sample_values', 'mvrex', argvals)
        assert row['mvrex_unmatched_count'] <= field_cfg['max_unmatched_count']
