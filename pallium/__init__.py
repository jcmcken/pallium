__version__ = '0.0.1'
__author__ = 'Jon McKenzie'

import socket
import xml.sax as sax
import re
import optparse
from pprint import pprint

# Gmetad settings
DEFAULT_GMETAD_PORT = 8651

# For alert condition expressions
COMPARATORS = [ '==', '>=', '<=', '<', '>' ]

# Regexs for validating a metric expression
_OP_LIST = "|".join(["(%s)"] * len(COMPARATORS))
_STR_RE_OPERATOR = "(" + _OP_LIST % tuple(COMPARATORS) + ")"
_STR_RE_VAL = "[\w\.]+"
_STR_RE_KEY = "\w+"
_STR_RE_EXPRESSION = "^" + _STR_RE_KEY + _STR_RE_OPERATOR + _STR_RE_VAL + "$"
_RE_EXPRESSION = re.compile(_STR_RE_EXPRESSION)

def _generate_raw_data(host='localhost', port=DEFAULT_GMETAD_PORT):
    """
    Connect to ``(host, port)`` and stream any data. Break if received data is ever
    empty (signalling EOF).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    recv = "dummy data"
    while recv:
        recv = s.recv(512)
        if recv:
            yield recv

    # tear down the socket
    s.shutdown(socket.SHUT_RDWR)
    s.close()

class BooleanTree(object):

    # operator implementations
    OPERATORS = {
      "or": lambda x,y: x or y,
      "and": lambda x,y: x and y
    }

    def walk(self, tree):
        """
        Walk the boolean tree ``tree`` and evaluate each sub-tree and each metric
        expression, returning a single boolean result.
    
        Trees are simply lists in a "Polish notation"-type format. This means that
        the operator comes first in the list and all operands follow.
    
        Valid operators are ``or`` and ``and``.
    
        For example, a simple tree looks like this::
    
            [ "or", "some_expr1==2.0", "some_expr2==test" ]
    
        This expression translates to "``some_expr1 == 2.0`` or ``some_expr2 == test``".
    
        Trees may be nested arbitrarily. For example::
    
            [ "and",
                [ "or", 
                    [ "some_expr1==2.0", "some_expr2==test" ]
                ],
                "some_expr3!=2241.3"
            ]
    
        This tree would first evaluate the tree given in the previous example. Next, it would evaluate
        whether ``some_expr3 != 2241.3``. Finally, it would take these two results and check if they
        are both true.
    
        """
        if not self.is_boolean_tree(tree):
            raise Exception# invalid tree
    
        op, operands = tree[0], tree[1:]
        stack = []
    
        for operand in operands:
            if self.is_boolean_tree(operand):
                result = self.walk(operand)
            elif is_valid_node(operand):
                result = self.evaluate_node(operand)
            else:
                raise Exception# not a metric expr or a boolean tree
            stack.append(result)
        final_result = self.apply_operator(op, stack)
        return final_result

    def apply_operator(self, operator, items):
        """
        Apply either an ``and`` operation or an ``or`` operation to the list of 
        booleans in ``items``.
        """
        op_func = self.OPERATORS.get(op, None)

        if op_func is None:
            raise Exception #invalid op

        return reduce(op_func, items)

    def evaluate_node(self, node):
        raise NotImplementedError

    def is_boolean_tree(self, tree):
        """
        Decide if ``tree`` (a list) is a valid boolean expression tree. These checks
        simply validate the general structure of ``tree``.
        """
        return isinstance(tree, list) and tree[0] in self.OPERATORS and \
               len(tree) >= 2

    def is_valid_node(self, node):
        raise NotImplementedError

class GangliaBooleanTree(BooleanTree):
    def evaluate_node(self, node):
        import random
        return random.choice([True, False])

    def is_valid_node(self, node):
        """
        Validate that ``node`` is a valid metric expression.
    
        Metric expressions are of the form::
    
            <metric_name><comparator><value>
    
        ...where:
        
        * ``<metric_name>`` is a metric as reported by Ganglia.
         
        * ``<comparator>`` is one of ``<``, ``>``, ``<=``, ``>=``, ``==`` or 
          ``!=``,
    
        * ``<value>`` is integer-like, float-like, or resembles a simple string.
        """
        return bool(_RE_EXPRESSION.search(node))

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

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('-G', '--grid-regexp')
    cli.add_option('-C', '--cluster-regexp')
    cli.add_option('-H', '--host-regexp')
    return cli

if __name__ == '__main__':
    cli = create_cli()
    opts, args = cli.parse_args()

    datastore = {}

    kwargs = {}
    if opts.grid_regexp:
        kwargs['grid_expr'] = opts.grid_regexp
    if opts.cluster_regexp:
        kwargs['cluster_expr'] = opts.cluster_regexp
    if opts.host_regexp:
        kwargs['host_expr'] = opts.host_regexp

    parser = sax.make_parser()
    handler = GangliaContentHandler(datastore, **kwargs)
    parser.setContentHandler(handler)
    
    for chunk in _generate_raw_data():
        parser.feed(chunk)

    pprint(datastore)

    

