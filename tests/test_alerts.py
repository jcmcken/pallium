
from pallium.alerts import DictAlert, DEFAULT_ALERT, InvalidAlert, \
                           DEFAULT_METALERT, DictMetalert
from pallium.config import load_json_config
from tests import ALERT_DIR
import os

ALERT_BLANK_RULE = {
  "name": "alert_blank_rule",
  "description": "An alert where everything is valid, except the rule is set"
                 "to []",
}

ALERT_GOOD_RULE = ALERT_BLANK_RULE.copy()
ALERT_GOOD_RULE["rule"] = [ "or", "blah==1", "bar==2" ]

METALERT_BLANK_RULE = {
  "name": "metalert_blank_rule",
  "description": "An alert where everything is valid, except the rule is set"
                 "to []",
}

METALERT_GOOD_RULE = METALERT_BLANK_RULE.copy()
METALERT_GOOD_RULE["rule"] = [ "or", "blah==1", "bar==2" ]

def test_fixture_alert_dir():
    print ALERT_DIR
    assert os.path.isdir(ALERT_DIR)

def test_default_alert_is_bad():
    try:
        DictAlert(DEFAULT_ALERT)
    except InvalidAlert, e:
        assert "key 'name' is not set" in e.args[0]
        return
    assert False

def test_blank_rule_alert():
    try:
        DictAlert(ALERT_BLANK_RULE)
    except InvalidAlert, e:
        assert "must be a boolean tree" in e.args[0]
        return
    assert False

def test_ok_rule():
    DictAlert(ALERT_GOOD_RULE)

def test_default_metalert_is_bad():
    try:
        DictMetalert(DEFAULT_METALERT)
    except InvalidAlert, e:
        assert "key 'name' is not set" in e.args[0]
        return
    assert False

def test_blank_rule_metalert():
    try:
        DictMetalert(METALERT_BLANK_RULE)
    except InvalidAlert, e:
        assert "must be a boolean tree" in e.args[0]
        return
    assert False

def test_meta_ok_rule():
    DictMetalert(METALERT_GOOD_RULE)
