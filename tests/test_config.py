
from pallium.config import valid_tag

GOOD_TAG = "this_is_good"
BAD_TAG = "$this is bad"

def test_valid_tag():
    assert valid_tag(GOOD_TAG) is True
    assert valid_tag(BAD_TAG) is False
