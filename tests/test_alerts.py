
from pallium.alerts import (
    DictAlert, DEFAULT_ALERT, InvalidAlert, DEFAULT_METALERT, DictMetalert, 
    load_alerts, JsonAlert
)
from pallium.config import load_json_config
from tests import ALERT_DIR
import os

ALERT_BLANK_RULE = {
  "name": "alert_blank_rule",
  "description": "An alert where everything is valid, except the rule is set"
                 "to []",
}

ALERT_GOOD_RULE = ALERT_BLANK_RULE.copy()
ALERT_RULE = [ "or", "blah==1", "bar==2" ]
ALERT_GOOD_RULE["rule"] = ALERT_RULE

ALERT_BAD_NAME = ALERT_GOOD_RULE.copy()
ALERT_BAD_NAME['name'] = 'Something invalid'

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

def test_invalid_alert_name():
    try:
        DictAlert(ALERT_BAD_NAME)
    except ValueError, e:
        assert 'invalid alert name' in e.args[0]
        return
    assert False

def test_alert_load():
    alerts = load_alerts(ALERT_DIR, alert_cls=JsonAlert)
    assert isinstance(alerts, dict)
    assert bool(alerts) is True

