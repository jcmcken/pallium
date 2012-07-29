
from pallium.condition import _RE_EXPRESSION, parse_metric_expr

GOOD_METRIC = "foo==bar"

INCOMPLETE_METRIC = 'foo=='
INCOHERENT_METRIC = 'lskfjlsdkj$JKL$j'
INVALID_COMPARATOR = 'foo<=>bar'

def test_metric_expr():
    match = _RE_EXPRESSION.match(GOOD_METRIC)
    assert match.group('metric') == 'foo'
    assert match.group('comparator') == '=='
    assert match.group('expected') == 'bar'

def test_invalid_metric_expr():
    assert parse_metric_expr(INCOMPLETE_METRIC) == (None, None, None)
    assert parse_metric_expr(INCOHERENT_METRIC) == (None, None, None)
    assert parse_metric_expr(INVALID_COMPARATOR) == (None, None, None)
