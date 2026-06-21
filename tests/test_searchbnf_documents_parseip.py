from pathlib import Path


def test_searchbnf_documents_parseip_option():
    path = Path(__file__).resolve().parent.parent / 'default' / 'searchbnf.conf'
    text = path.read_text(encoding='utf-8')
    assert 'parseip=<bool>' in text
    assert 'cim_vladiator_parse_ip_validation' in text
