import pytest

from mvrex import process_mvrex_row


def _row(sample_values, validation_mode='ip_strict', regex=r'^[0-9A-Fa-f.:]+$'):
    return {
        'sample_values': sample_values,
        'validation_regex': regex,
        'validation_mode': validation_mode,
    }


def _process(row, field='sample_values'):
    argvals = {'field': field, 'showunmatched': 't', 'showcount': 't'}
    return process_mvrex_row(row, 'validation_regex', field, 'mvrex', argvals)


def test_mv_ipv6_mix():
    row = _row(['ff02::1', 'fe80::gabc', '10.0.0.5'])
    _process(row)
    assert row['mvrex_unmatched'] == ['fe80::gabc']
    assert row['mvrex_unmatched_count'] == 1


def test_empty_validation_mode_preserves_findall_semantics():
    row = {
        'sample_values': '12345',
        'validation_regex': r'^\d{1,5}$',
        'validation_mode': '',
    }
    _process(row)
    assert row['mvrex_matched_count'] == 1


def test_polymorphic_src_ipv6_and_hostname():
    row = _row(
        ['ff02::1', 'firewall01.corp.example', '10.0.0.1 junk'],
        validation_mode='ip_polymorphic',
        regex=r'^[\w\.:\-%]+$',
    )
    _process(row)
    assert 'ff02::1' in row['mvrex_matches']
    assert 'firewall01.corp.example' in row['mvrex_matches']
    assert row['mvrex_unmatched'] == ['10.0.0.1 junk']


def test_dvc_ae9():
    row = _row(
        ['10.1.1.1', 'router-core-01', '10.1.1.1 junk'],
        validation_mode='ip_polymorphic',
        regex=r'^[\w\.:\-%]+$',
    )
    _process(row)
    assert row['mvrex_unmatched'] == ['10.1.1.1 junk']


def test_strict_rejects_zone_suffix():
    row = _row(['fe80::1%eth0'])
    _process(row)
    assert row['mvrex_unmatched_count'] == 1


def test_scalar_full_string():
    row = _row('10.0.0.5')
    row['sample_values'] = '10.0.0.5'
    _process(row)
    assert row['mvrex_matched_count'] == 1
    row2 = _row('10.0.0.1 trailing-junk', validation_mode='ip_polymorphic', regex=r'^[\w\.:\-%]+$')
    row2['sample_values'] = '10.0.0.1 trailing-junk'
    _process(row2)
    assert row2['mvrex_unmatched_count'] == 1