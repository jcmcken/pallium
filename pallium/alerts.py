
import re
from pallium.condition import GangliaBooleanTree
from pallium.config import load_json_config, _STR_RE_VALID_TAG, valid_tag
from pallium.util import SuperDict, files_from_dir

DEFAULT_ALERT = {
  "name": None,
  "description": None,
  "options": {
    "threshold": 1,
    "priority": "low",
    "grouped": False
  },
  "filter": {
    "grid": ".*",
    "cluster": ".*",
    "host": ".*",
  },
  "rule": [],
}

DEFAULT_METALERT = {
  "name": None,
  "description": None,
  "options": {
    "threshold": 1,
    "priority": "low",
  },
  "rule": [],
}

class InvalidAlert(AttributeError): pass

class BaseAlert(SuperDict):
    required_settings = []
    default = {}

    def __init__(self, data):
        SuperDict.__init__(self, self.default)

        self._load_config(data)

    def _load_config(self, data):
        data = self.load_config(data)
        self.recursive_update(data)
        self._validate_alert()
        self._convert_data()

    def _validate_alert(self):
        for key in self.required_settings:
            if not self.get(key, None):
                raise InvalidAlert("key '%s' is not set in alert '%s'" % \
                    (key, self))
        name = self.get('name')

        # must have a valid tag name
        if not valid_tag(name):
            raise ValueError("invalid alert name '%s', must match regex '%s'" % \
                (name, _STR_RE_VALID_TAG))
        self._validate_rule(self['rule'])

    def _validate_rule(self, rule):
        if not GangliaBooleanTree.is_boolean_tree(rule):
            raise InvalidAlert(
                "the alert rule in '%s' must be a boolean tree" % self
            )
       
    def _convert_data(self):
        pass

    def load_config(self, data):
        raise NotImplementedError

class Alert(BaseAlert):
    required_settings = [ "name", "description" ]
    default = DEFAULT_ALERT
       
    def _convert_data(self):
        for key in [ "grid", "cluster", "host" ]:
            self["filter"][key] = re.compile(self["filter"][key])

    def load_config(self, data):
        raise NotImplementedError

class AlertJsonLoader(object):
    def load_config(self, data):
        return load_json_config(data)

class AlertDictLoader(object):
    def load_config(self, data):
        if not isinstance(data, dict):
            raise InvalidAlert("invalid data type for alert '%s'" % data)
        return data

class JsonAlert(AlertJsonLoader, Alert): pass
class DictAlert(AlertDictLoader, Alert): pass

class Metalert(BaseAlert):
    required_settings = [ "name", "description" ]
    default = DEFAULT_METALERT

class JsonMetalert(AlertJsonLoader, Metalert): pass
class DictMetalert(AlertDictLoader, Metalert): pass

def load_alerts(directory, alert_cls):
    files = files_from_dir(directory)
    store = {}
    for file in files:
        alert = dict(alert_cls(file))
        name = alert['name']
        if name in store:
            raise Exception # duplicate alert name
        store[name] = alert
        del store[name]['name'] 

    return store
        

