
import re
from pallium.condition import GangliaBooleanTree
from pallium.config import load_json_config
from pallium.util import SuperDict

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

class Alert(SuperDict):
    REQUIRED_SETTINGS = [ "name", "description" ]

    def __init__(self, data):
        SuperDict.__init__(self, DEFAULT_ALERT)

        self._load_config(data)

    def _load_config(self, data):
        data = self.load_config(data)
        self._validate_alert(data)
        data = self._convert_data(data)

        self.recursive_update(data)

    def _validate_alert(self, data):
        for key in self.REQUIRED_SETTINGS:
            if not data.get(key, None):
                raise InvalidAlert("key '%s' is not set in alert '%s'" % \
                    (key, self.data))
        self._validate_rule(data['rule'])

    def _validate_rule(self, rule):
        if not GangliaBooleanTree.is_boolean_tree(rule):
            raise InvalidAlert(
                "the alert rule in '%s' must be a boolean tree" % self.data
            )
       
    def _convert_data(self, data):
        for key in [ "grid", "cluster", "host" ]:
            data[key] = re.compile(data[key])
        return data

    def load_config(self, data):
        raise NotImplementedError

class JsonAlert(Alert):
    def load_config(self, data):
        return load_json_config(data)

class DictAlert(Alert):
    def load_config(self, data):
        return data

def load_alerts(directory, alert_cls=JsonAlert):
    alerts = []
    for filename in os.listdir(directory):
        fullname = os.path.join(os.path.abspath(directory), filename)
        # resolve links
        if os.path.islink(fullname):
            fullname = os.readlink(fullname)
        # skip non-files
        if not os.path.isfile(fullname):
            continue

        alert = alert_cls(fullname)
        alerts.append(alert)
    return alerts
