import pytest

from cim_vladiator_common import validate_strict_ip, validate_polymorphic_ip, derive_validation_mode


@pytest.mark.parametrize(
    'value',
    [
        'fe80::7a45:58ff:fe84:37cb',
        'FE80::7A45:58FF:FE84:37CB',
        'ff02::1',
        'ff02::fb',
        '2001:db8::1',
        '10.0.0.5',
        '192.168.0.1',
        '::1',
        '0.0.0.0',
    ],
)
def test_strict_ip_accepts_valid_literals(value):
    assert validate_strict_ip(value) is True


@pytest.mark.parametrize(
    'value',
    [
        'fe80::1%eth0',
        'server01.corp.example',
        '192.168.1',
        'fe80::gabc',
        '256.1.1.1',
        '10.0.0.1 trailing-junk',
        ' 10.0.0.1',
        '10.0.0.1 ',
    ],
)
def test_strict_ip_rejects_invalid_values(value):
    assert validate_strict_ip(value) is False


def test_polymorphic_accepts_hostname_and_ipv4():
    assert validate_polymorphic_ip('firewall01.corp.example') is True
    assert validate_polymorphic_ip('10.0.0.5') is True
    assert validate_polymorphic_ip('router-core-01') is True


def test_polymorphic_accepts_ipv6_and_zone_suffix():
    assert validate_polymorphic_ip('ff02::1') is True
    assert validate_polymorphic_ip('fe80::7a45:58ff:fe84:37cb') is True
    assert validate_polymorphic_ip('fe80::1%eth0') is True


@pytest.mark.parametrize(
    'value',
    [
        '10.0.0.1 trailing-junk',
        '10.1.1.1 junk',
        '192.168.1',
    ],
)
def test_polymorphic_rejects_junk_and_partial_ip(value):
    assert validate_polymorphic_ip(value) is False


@pytest.mark.parametrize(
    'value',
    [
        'router-v2.5.1',
    ],
)
def test_polymorphic_rejects_dotted_hostname_ip_shape_misclassification(value):
    """Dotted hostnames match has_ip_shape heuristic and fail IP parse (accepted limitation)."""
    assert validate_polymorphic_ip(value) is False


def test_polymorphic_dvc_cases():
    assert validate_polymorphic_ip('10.1.1.1') is True
    assert validate_polymorphic_ip('router-core-01') is True
    assert validate_polymorphic_ip('10.1.1.1 junk') is False


@pytest.mark.parametrize(
    'field,datamodel,enabled,expected',
    [
        ('src_ip', 'Network_Traffic', True, 'ip_strict'),
        ('dest_ip', 'Network_Traffic', True, 'ip_strict'),
        ('src', 'Network_Traffic', True, 'ip_polymorphic'),
        ('dest', 'Network_Traffic', True, 'ip_polymorphic'),
        ('dvc', 'Network_Traffic', True, 'ip_polymorphic'),
        ('ip', 'UBA_Asset_Data', True, 'ip_strict'),
        ('src_ip', 'Network_Traffic', False, ''),
        ('severity', 'Network_Traffic', True, ''),
        ('ip', 'Network_Traffic', True, ''),
    ],
)
def test_derive_validation_mode(field, datamodel, enabled, expected):
    assert derive_validation_mode(field, datamodel, enabled) == expected
