from pallium.parse import (
    LoadingGangliaContentHandler, parse_feed, file_feeder
)
from tests import XML_DIR
import os

GMETAD_DATA = os.path.join(XML_DIR, 'gmeta_20000_lines.xml')

def test_integration_loading_parser():
    handler = LoadingGangliaContentHandler()
    feeder = lambda x: file_feeder(x, GMETAD_DATA)
    parser = parse_feed(handler, feeder)
    
    data = handler.data

    assert isinstance(data, dict)
    assert bool(data)
    assert data.get('unspecified')
    assert data['unspecified'].get('Test Cluster')
    assert data['unspecified']['Test Cluster'].get('192.168.1.105')


