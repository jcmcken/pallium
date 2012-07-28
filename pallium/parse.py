import xml.sax as sax
import re

class GangliaContentHandler(sax.ContentHandler):
    """
    Base Ganglia content handler. Does not do anything with the data, but it will
    execute logic to filter out data that doesn't match ``grid_expr``, 
    ``cluster_expr``, or ``host_expr``. 
    """
    def __init__(self, grid_expr=".*", cluster_expr=".*", host_expr=".*"):

        self.exprs = {
            'grid': re.compile(grid_expr),
            'cluster': re.compile(cluster_expr),
            'host': re.compile(host_expr),
        }

        self.current = {
            'grid': None, 'cluster': None, 'host': None 
        }

        self.skip = {}

        sax.ContentHandler.__init__(self)

    def _eval_re(self, type, text):
        pat = self.exprs.get(type, None)

        if pat is None:
            raise ValueError("Invalid regular expression type '%s" % type)

        return bool(pat.search(text))

    def _check_skip(self, type):
        skip = self.skip.get(type, None)
        current = self.current.get(type, None)

        if skip is None or current is None:
            ret = False
        else:
            ret = skip == current

        return ret

    def _set_skip(self, type, value):
        if not self._eval_re(type, value):
            self.skip[type] = value
            return True
        return False

    def _handle_grid(self, attrs):
        name = attrs['NAME']
        self.current['grid'] = name

        # if grid doesn't match regexp, set skip
        if self._set_skip('grid', name): return

        self.handle_grid(attrs)

    def handle_grid(self, attrs):
        pass

    def _handle_cluster(self, attrs):
        name = attrs['NAME']

        self.current['cluster'] = name

        # if cluster doesn't match regexp, set skip
        if self._set_skip('cluster', name): return

        # skip node if GRID set to skip
        if self._check_skip('grid'): return

        self.handle_cluster(attrs)

    def handle_cluster(self, attrs):
        pass

    def _handle_host(self, attrs):
        name = attrs['NAME']
        self.current['host'] = name

        # if host doesn't match regexp, set skip
        if self._set_skip('host', name): return

        # skip node if GRID or CLUSTER set to skip
        if self._check_skip('grid'): return 
        if self._check_skip('cluster'): return

        self.handle_host(attrs)

    def handle_host(self, attrs):
        pass

    def _handle_metric(self, attrs):
        name = attrs['NAME']

        # skip node if GRID, CLUSTER, or HOST set to skip
        if self._check_skip('grid'): return 
        if self._check_skip('cluster'): return
        if self._check_skip('host'): return

        self.handle_metric(attrs)

    def handle_metric(self, attrs):
        pass

    def _handle_grid_end(self):
        self.current['grid'] = None
        self.skip['grid'] = None
        self.handle_grid_end()

    def handle_grid_end(self):
        pass

    def _handle_cluster_end(self):
        self.current['cluster'] = None
        self.skip['cluster'] = None
        self.handle_cluster_end()

    def handle_cluster_end(self):
        pass

    def _handle_host_end(self):
        self.current['host'] = None
        self.skip['host'] = None
        self.handle_host_end()

    def handle_host_end(self):
        pass

    def _handle_metric_end(self):
        self.handle_metric_end()

    def handle_metric_end(self):
        pass

    def startElement(self, name, attrs):
        print self.current

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
    def __init__(self, **kwargs):
        self.data = {}
        GangliaContentHandler.__init__(self, **kwargs)
    
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
