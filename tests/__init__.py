import os

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TEST_ROOT, 'fixtures')
ALERT_DIR = os.path.join(FIXTURES_DIR, 'alerts')
FAKE_ALERTS_DIR = os.path.join(ALERT_DIR, 'fake')
REAL_ALERTS_DIR = os.path.join(ALERT_DIR, 'real')
XML_DIR = os.path.join(FIXTURES_DIR, 'xml')
