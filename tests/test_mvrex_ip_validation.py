import pytest

from mvrex import process_mvrex_row


def _row(sample_values, field='src_ip', datamodel='Network_Traffic', regex=r'^[0-9A-Fa-f.:]+$'):
    return {
        'field': field,
        'datamodel': datamodel,
        'sample_values': sample_values,
        'validation_regex': regex,
    }


def _process(row, field='sample_values', parseip='t'):
    argvals = {'field': field, 'showunmatched': 't', 'showcount': 't', 'parseip': parseip}
    return process_mvrex_row(row, 'validation_regex', field, 'mvrex', argvals)


def test_mv_ipv6_mix():
    row = _row(['ff02::1', 'fe80::gabc', '10.0.0.5'])
    _process(row)
    assert row['mvrex_unmatched'] == ['fe80::gabc']
    assert row['mvrex_unmatched_count'] == 1


def test_non_ip_field_preserves_findall_semantics():
    row = {
        'field': 'severity',
        'datamodel': 'Network_Traffic',
        'sample_values': '12345',
        'validation_regex': r'^\d{1,5}$',
    }
    _process(row)
    assert row['mvrex_matched_count'] == 1


def test_parseip_disabled_skips_stage2_on_ip_field():
    row = _row(['fe80::gabc', 'ff02::1'])
    _process(row, parseip='f')
    assert row['mvrex_unmatched'] == ['fe80::gabc']
    assert 'ff02::1' in row['mvrex_matches']


def test_polymorphic_src_ipv6_and_hostname():
    row = _row(
        ['ff02::1', 'firewall01.corp.example', '10.0.0.1 junk'],
        field='src',
        regex=r'^[\w\.:\-%]+$',
    )
    _process(row)
    assert 'ff02::1' in row['mvrex_matches']
    assert 'firewall01.corp.example' in row['mvrex_matches']
    assert row['mvrex_unmatched'] == ['10.0.0.1 junk']


def test_dvc_ae9():
    row = _row(
        ['10.1.1.1', 'router-core-01', '10.1.1.1 junk'],
        field='dvc',
        regex=r'^[\w\.:\-%]+$',
    )
    _process(row)
    assert row['mvrex_unmatched'] == ['10.1.1.1 junk']


def test_strict_rejects_zone_suffix():
    row = _row(['fe80::1%eth0'])
    _process(row)
    assert row['mvrex_unmatched_count'] == 1


def test_none_and_string_values_normalized_once():
    """None and non-string samples share one normalization path for stage-1 and stage-2."""
    row = _row([None, '10.0.0.5'])
    _process(row)
    assert row['mvrex_matches'] == ['10.0.0.5']
    assert row['mvrex_unmatched'] == [None]


def test_scalar_full_string():
    row = _row('10.0.0.5')
    row['sample_values'] = '10.0.0.5'
    _process(row)
    assert row['mvrex_matched_count'] == 1
    row2 = _row('10.0.0.1 trailing-junk', field='dest', regex=r'^[\w\.:\-%]+$')
    row2['sample_values'] = '10.0.0.1 trailing-junk'
    _process(row2)
    assert row2['mvrex_unmatched_count'] == 1