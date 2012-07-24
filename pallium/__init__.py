__version__ = '0.0.1'
__author__ = 'Jon McKenzie'

import socket
import xml.sax as sax
import re

# Gmetad settings
DEFAULT_GMETAD_PORT = 8651

# For alert condition expressions
COMPARATORS = [ '==', '>=', '<=', '<', '>' ]
OPERATORS = [ "or", "and" ]

# Regexs for validating a metric expression
_OP_LIST = "|".join(["(%s)"] * len(COMPARATORS))
STR_RE_OPERATOR = "(" + _OP_LIST % tuple(COMPARATORS) + ")"
STR_RE_VAL = "[\w\.]+"
STR_RE_KEY = "\w+"
STR_RE_EXPRESSION = "^" + STR_RE_KEY + STR_RE_OPERATOR + STR_RE_VAL + "$"
RE_EXPRESSION = re.compile(STR_RE_EXPRESSION)

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

def is_boolean_tree(data):
    """
    Decide if ``data`` (a list) is a valid boolean expression tree. These checks
    simply validate the general structure of ``data``.
    """
    return isinstance(data, list) and data[0] in OPERATORS and \
           len(data) >= 2

def is_valid_metric(expr):
    """
    Validate that ``expr`` is a valid metric expression.

    Metric expressions are of the form::

        <metric_name><comparator><value>

    ...where:
    
    * ``<metric_name>`` is a metric as reported by Ganglia.
     
    * ``<comparator>`` is one of ``<``, ``>``, ``<=``, ``>=``, ``==`` or 
      ``!=``,

    * ``<value>`` is integer-like, float-like, or resembles a simple string.
    """
    return bool(RE_EXPRESSION.search(expr))

def apply_operator(op, data):
    """
    Apply either an ``and`` operation or an ``or`` operation to the list of 
    booleans in ``data``.
    """
    if op == 'or':
        reducer = lambda x,y: x or y
    elif op == 'and':
        reducer = lambda x,y: x and y
    else:
        raise # invalid operator
    return reduce(reducer, data)

def evaluate(expr):
    """
    Evaluate the metric expression ``expr`` to either ``True`` or ``False``
    """
    import random
    return random.choice([True, False])

def walk(tree, evaluator=lambda x: evaluate):
    """
    Walk the boolean tree ``tree`` and evaluate each sub-tree and each metric
    expression, returning a single boolean result.

    Trees are simply lists in a "Polish notation"-type format. This means that
    the operator comes first in the list and all operands follow.

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
    if not is_boolean_tree(tree):
        raise Exception# invalid tree

    op, operands = tree[0], tree[1:]
    stack = []

    for operand in operands:
        if is_boolean_tree(operand):
            result = walk(operand)
        elif is_valid_metric(operand):
            result = evaluate(operand)
        else:
            raise Exception# not a metric expr or a boolean tree
        stack.append(result)
    final_result = apply_operator(op, stack)
    return final_result

class GangliaContentHandler(sax.ContentHandler):
    def __init__(self):
        sax.ContentHandler.__init__(self)
        self.tree = {}
        self.tree['ganglia'] = {}

        self.current_grid = None
        self.current_cluster = None

    def startDocument(self):
        print 'started xml parsing'

    def startElement(self, name, attrs):
        print

if __name__ == '__main__':
    parser = sax.make_parser()
    parser.setContentHandler(GangliaContentHandler())
    
    for chunk in _generate_raw_data():
        parser.feed(chunk)

