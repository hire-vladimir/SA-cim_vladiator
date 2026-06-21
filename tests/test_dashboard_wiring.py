from pathlib import Path


def test_dashboard_uses_parse_ip_validation_macro():
    path = Path(__file__).resolve().parent.parent / 'default' / 'data' / 'ui' / 'views' / 'cim_validator.xml'
    text = path.read_text(encoding='utf-8')
    assert 'parseip=`cim_vladiator_parse_ip_validation`' in text


def test_dashboard_does_not_reference_validation_mode():
    path = Path(__file__).resolve().parent.parent / 'default' / 'data' / 'ui' / 'views' / 'cim_validator.xml'
    text = path.read_text(encoding='utf-8')
    assert 'validation_mode' not in text