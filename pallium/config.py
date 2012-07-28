
try:
    import json
except ImportError:
    import simplejson as json

from copy import deepcopy

DEFAULT_CONFIG_FILE = "/etc/pallium/config.json"

DEFAULT_CONFIG = {
  "alerts_dir": "/etc/pallium/alerts"
}

def load_pallium_config(filename):
    config = load_json_config(filename)
    default = deepcopy(DEFAULT_CONFIG)
    default.update(config)
    return default

def load_json_config(filename):
    return json.load(open(filename))

