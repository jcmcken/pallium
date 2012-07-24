__version__ = '0.0.1'
__author__ = 'Jon McKenzie'

import socket
import xml.sax as sax
import re

DEFAULT_GMETAD_PORT = 8651

def _generate_raw_data(host='localhost', port=DEFAULT_GMETAD_PORT):
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

COMPARATORS = [ '==', '>=', '<=', '<', '>' ]
OPERATORS = [ "or", "and" ]

_OP_LIST = "|".join(["(%s)"] * len(COMPARATORS))
STR_RE_OPERATOR = "(" + _OP_LIST % tuple(COMPARATORS) + ")"
STR_RE_VAL = "[\w\.]+"
STR_RE_KEY = "\w+"
STR_RE_EXPRESSION = "^" + STR_RE_KEY + STR_RE_OPERATOR + STR_RE_VAL + "$"

RE_EXPRESSION = re.compile(STR_RE_EXPRESSION)

def is_boolean_tree(data):
    return isinstance(data, list) and data[0] in OPERATORS and \
           len(data) >= 2

def is_valid_metric(expr):
    return bool(RE_EXPRESSION.search(expr))

def apply_operator(op, data):
    if op == 'or':
        reducer = lambda x,y: x or y
    elif op == 'and':
        reducer = lambda x,y: x and y
    else:
        raise # invalid operator
    return reduce(reducer, data)

def evaluate(expr):
    import random
    return random.choice([True, False])

def walk(tree, evaluator=lambda x: evaluate):
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

