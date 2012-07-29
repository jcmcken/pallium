import re

# For alert condition expressions
COMPARATORS = [ '==', '>=', '<=', '<', '>' ]

# Regexs for validating a metric expression
_OP_LIST = "|".join(["(%s)"] * len(COMPARATORS))
_STR_RE_OPERATOR = "(" + _OP_LIST % tuple(COMPARATORS) + ")"
_STR_RE_VAL = "[\w\.]+"
_STR_RE_KEY = "\w+"
_STR_RE_EXPRESSION = "^" + _STR_RE_KEY + _STR_RE_OPERATOR + _STR_RE_VAL + "$"
_RE_EXPRESSION = re.compile(_STR_RE_EXPRESSION)

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

    @classmethod
    def is_boolean_tree(cls, tree):
        """
        Decide if ``tree`` (a list) is a valid boolean expression tree. These checks
        simply validate the general structure of ``tree``.
        """
        return len(tree) >= 2 and isinstance(tree, list) and \
               tree[0] in cls.OPERATORS

    @classmethod
    def is_valid_node(cls, node):
        raise NotImplementedError

class GangliaBooleanTree(BooleanTree):
    def evaluate_node(self, node):
        import random
        return random.choice([True, False])

    @classmethod
    def is_valid_node(cls, node):
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

