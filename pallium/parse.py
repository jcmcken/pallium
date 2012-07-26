import xml.sax as sax
import re

class GangliaContentHandler(sax.ContentHandler):
    def __init__(self, datastore, grid_expr=".*", cluster_expr=".*", host_expr=".*"):

        self.exprs = {
            'grid': re.compile(grid_expr),
            'cluster': re.compile(cluster_expr),
            'host': re.compile(host_expr),
        }

        self.current = {
            'grid': None, 'cluster': None, 'host': None 
        }

        self.skip = {}

        self.data = datastore

        sax.ContentHandler.__init__(self)

    def _eval_re(self, type, text):
        pat = self.exprs.get(type, None)

        if pat is None:
            raise ValueError("Invalid regular expression type '%s" % type)

        return bool(pat.search(text))

    def startDocument(self):
        print 'started xml parsing'

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

        self.data.setdefault(name, {})

    def _handle_cluster(self, attrs):
        name = attrs['NAME']

        self.current['cluster'] = name

        # if cluster doesn't match regexp, set skip
        if self._set_skip('cluster', name): return

        # skip node if GRID set to skip
        if self._check_skip('grid'): return

        self.data[self.current['grid']].setdefault(name, {})

    def _handle_host(self, attrs):
        name = attrs['NAME']
        self.current['host'] = name

        # if host doesn't match regexp, set skip
        if self._set_skip('host', name): return

        # skip node if GRID or CLUSTER set to skip
        if self._check_skip('grid'): return 
        if self._check_skip('cluster'): return
        
        self.data[self.current['grid']][self.current['cluster']].setdefault(name, {})

    def _handle_metric(self, attrs):
        name = attrs['NAME']

        # skip node if GRID, CLUSTER, or HOST set to skip
        if self._check_skip('grid'): return 
        if self._check_skip('cluster'): return
        if self._check_skip('host'): return

        metric_data = { 
            'name': attrs['VAL'], 
            'units': attrs['UNITS'], 
            'type': attrs['TYPE']
        } 

        self.data[self.current['grid']][self.current['cluster']]\
                 [self.current['host']][name] = metric_data

    def _handle_grid_end(self):
        self.current['grid'] = None
        self.skip['grid'] = None

    def _handle_cluster_end(self):
        self.current['cluster'] = None
        self.skip['cluster'] = None

    def _handle_host_end(self):
        self.current['host'] = None
        self.skip['host'] = None

    def _handle_metric_end(self):
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
