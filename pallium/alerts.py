
import re
from pallium.condition import GangliaBooleanTree
from pallium.config import load_json_config

DEFAULT_ALERT = {
  "grid": ".*",
  "cluster": ".*",
  "host": ".*",
}

class InvalidAlert(AttributeError): pass

class Alert(dict):
    def __init__(self, filename):
        self.filename = filename

        data = self._load_config(self.filename)
        self._validate_alert(data)
        data = self._convert_data(data)

        dict.__init__(self, data)
        
    def _validate_alert(self, data):
        for key in [ "name", "description", "grid", "cluster", "host", "rule" ]:
            if not data.get(key, None):
                raise InvalidAlert("key '%s' is not set in alert '%s'" % \
                    (key, self.filename))
        self._validate_rule(data['rule'])

    def _validate_rule(self, rule):
        if not GangliaBooleanTree.is_boolean_tree(rule):
            raise InvalidAlert(
                "the alert rule in '%s' must be a boolean tree" % self.filename
            )
       
    def _convert_data(self, data):
        for key in [ "grid", "cluster", "host" ]:
            data[key] = re.compile(data[key])
        return data

    def _load_config(self, filename):
        raise NotImplementedError

class JsonAlert(Alert):
    def _load_config(self, filename):
        return load_json_config(filename)

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
