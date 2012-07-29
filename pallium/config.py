
try:
    import json
except ImportError:
    import simplejson as json

import re
from copy import deepcopy

_STR_RE_VALID_TAG = "^[A-Za-z0-9_\-]+$"
_RE_VALID_TAG = re.compile(_STR_RE_VALID_TAG)

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

def valid_tag(tag):
    return bool(_RE_VALID_TAG.search(tag))
