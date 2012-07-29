import xml.sax as sax
import re
from pallium.ganglia import GangliaMetaDaemon
from pallium.condition import GangliaBooleanTree

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
        self.handle_grid_end()
        self.current['grid'] = None

    def handle_grid_end(self):
        pass

    def _handle_cluster_end(self):
        self.handle_cluster_end()
        self.current['cluster'] = None

    def handle_cluster_end(self):
        pass

    def _handle_host_end(self):
        self.handle_host_end()
        self.current['host'] = None

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
        # alert dict from ``pallium.alerts.load_alerts``
        self.alerts = alerts

        # each alert should keep track of what it's skipping here
        self.skip = {}

        # Keep track of metrics for the host currently being parsed.
        # Structure is of the form {"metric_name":"metric_val", ... }
        self.current_host_data = {}
 
        """
        Keep track of alert hits.

        Structure is of the form::

            {
              "alert_name1": [ "matching_host1", "matching_host2", ... ],
              "alert_name2": [ ... ],
              ...
            }

        """
        self.alert_results = {}

        GangliaContentHandler.__init__(self)
    
    def handle_grid(self, attrs):
        name = attrs['NAME']

        for alert_name, alert_data in self.alerts.iteritems():
            self.skip.setdefault(alert_name, {})
            if not bool(alert_data['filter']['grid'].search(name)):
                self.skip[alert_name].setdefault('grid', name)
    
    def handle_cluster(self, attrs):
        name = attrs['NAME']

        for alert_name, alert_data in self.alerts.iteritems():
            if not bool(alert_data['filter']['cluster'].search(name)):
                self.skip[alert_name].setdefault('cluster', name)
    
    def handle_host(self, attrs):
        name = attrs['NAME']

        for alert_name, alert_data in self.alerts.iteritems():
            if not bool(alert_data['filter']['host'].search(name)):
                self.skip[alert_name].setdefault('host', name)
    
    def handle_metric(self, attrs):
        name = attrs['NAME']
        val = attrs['VAL']
        
        # store the data for this metric
        self.current_host_data[name] = val

    def handle_host_end(self):
        tree = GangliaBooleanTree(self.current_host_data)

        for alert_name, alert_data in self.alerts.iteritems():

            # if alert is set to skip, don't evaluate it
            if self.skip[alert_name].get('grid') == self.current['grid'] or \
               self.skip[alert_name].get('cluster') == self.current['cluster'] or \
               self.skip[alert_name].get('host') == self.current['host']:
                continue

            # evaluate the alert rule against metrics from the host that was just parsed
            result = tree.walk(alert_data['rule'])

            # if ``result`` is ``True``, the alert has a hit
            if result is True:
                self.alert_results.setdefault(alert_name, [])
                self.alert_results[alert_name].append(self.current['host'])

        # reset current host data
        self.current_host_data = {}

