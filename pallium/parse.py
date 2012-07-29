import xml.sax as sax
import re
from pallium.ganglia import GangliaMetaDaemon

def gmetad_feeder(parser):
    gmetad = GangliaMetaDaemon()
    
    for chunk in gmetad.query():
        parser.feed(chunk)

def file_feeder(parser, filename):
    for line in open(filename):
        parser.feed(line)

def parse_feed(handler, feeder):
    parser = sax.make_parser()
    parser.setContentHandler(handler)
    feeder(parser)
    return parser

class GangliaContentHandler(sax.ContentHandler):
    """
    Base Ganglia content handler. Does not do anything with the data, but it will
    execute logic to filter out data that doesn't match ``grid_expr``, 
    ``cluster_expr``, or ``host_expr``. 
    """
    def __init__(self):

        self.current = {
            'grid': None, 'cluster': None, 'host': None 
        }

        sax.ContentHandler.__init__(self)

    def _handle_grid(self, attrs):
        name = attrs['NAME']
        self.current['grid'] = name

        self.handle_grid(attrs)

    def handle_grid(self, attrs):
        pass

    def _handle_cluster(self, attrs):
        name = attrs['NAME']

        self.current['cluster'] = name

        self.handle_cluster(attrs)

    def handle_cluster(self, attrs):
        pass

    def _handle_host(self, attrs):
        name = attrs['NAME']
        self.current['host'] = name

        self.handle_host(attrs)

    def handle_host(self, attrs):
        pass

    def _handle_metric(self, attrs):
        self.handle_metric(attrs)

    def handle_metric(self, attrs):
        pass

    def _handle_grid_end(self):
        self.current['grid'] = None
        self.handle_grid_end()

    def handle_grid_end(self):
        pass

    def _handle_cluster_end(self):
        self.current['cluster'] = None
        self.handle_cluster_end()

    def handle_cluster_end(self):
        pass

    def _handle_host_end(self):
        self.current['host'] = None
        self.handle_host_end()

    def handle_host_end(self):
        pass

    def _handle_metric_end(self):
        self.handle_metric_end()

    def handle_metric_end(self):
        pass

    def startElement(self, name, attrs):
        if name == "GRID":
            self._handle_grid(attrs)
        elif name == "CLUSTER":
            self._handle_cluster(attrs)
        elif name == "HOST":
            self._handle_host(attrs)
        elif name == "METRIC":
            self._handle_metric(attrs)
        else: return # ignore everything else

    def endElement(self, name):
        
        if name == "GRID":
            self._handle_grid_end()
        elif name == "CLUSTER":
            self._handle_cluster_end()
        elif name == "HOST":
            self._handle_host_end()
        elif name == "METRIC":
            self._handle_metric_end()

        else: return # ignore everything else

class LoadingGangliaContentHandler(GangliaContentHandler):
    """
    A Ganglia content handler that simply loads the Gmetad data structure into
    a dictionary.

    Without specifying grid/cluster/host filter regexps, the whole structure 
    will be loaded into ``data``.

    Structure is of the form::

        {"grid_name": 
          "cluster_name": {
            "host_name": {
              "metric_name_1": { "value": "...", "units": "...", "type": "..." },
              "metric_name_2": { "value": "...", "units": "...", "type": "..." },
              ...
            }
          }
        }
    """
    def __init__(self):
        self.data = {}
        GangliaContentHandler.__init__(self)
    
    def handle_grid(self, attrs):
        self.data.setdefault(attrs['NAME'], {})
    
    def handle_cluster(self, attrs):
        self.data[self.current['grid']].setdefault(attrs['NAME'], {})
    
    def handle_host(self, attrs):
        self.data[self.current['grid']][self.current['cluster']].setdefault(attrs['NAME'], {})
    
    def handle_metric(self, attrs):

        metric_data = { 
            'value': attrs['VAL'], 
            'units': attrs['UNITS'], 
            'type': attrs['TYPE']
        } 

        self.data[self.current['grid']][self.current['cluster']]\
                 [self.current['host']][attrs['NAME']] = metric_data

class AlertingGangliaContentHandler(GangliaContentHandler):
    def __init__(self, alerts):
        self.alerts = alerts
        self.data = {}
        GangliaContentHandler.__init__(self)
    
    def handle_grid(self, attrs):
        pass
    
    def handle_cluster(self, attrs):
        pass
    
    def handle_host(self, attrs):
        pass
    
    def handle_metric(self, attrs):
        pass
