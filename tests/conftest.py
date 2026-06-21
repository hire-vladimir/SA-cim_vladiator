import sys
from pathlib import Path
from types import ModuleType

BIN_DIR = Path(__file__).resolve().parent.parent / 'bin'
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

if 'splunk' not in sys.modules:
    splunk = ModuleType('splunk')
    intersplunk = ModuleType('splunk.Intersplunk')
    intersplunk.readResults = lambda *args, **kwargs: []
    intersplunk.getKeywordsAndOptions = lambda: ([], {})
    intersplunk.outputResults = lambda results: None
    intersplunk.generateErrorResults = lambda e: None
    splunk.Intersplunk = intersplunk
    sys.modules['splunk'] = splunk
    sys.modules['splunk.Intersplunk'] = intersplunk
