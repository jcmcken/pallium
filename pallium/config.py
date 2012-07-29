
try:
    import json
except ImportError:
    import simplejson as json

import re
import socket
from copy import deepcopy

_STR_RE_VALID_TAG = "[A-Za-z0-9_\-]+"
_STR_RE_VALID_TAG_COMPLETE = "^%s$" % _STR_RE_VALID_TAG
_RE_VALID_TAG = re.compile(_STR_RE_VALID_TAG_COMPLETE)

DEFAULT_CONFIG_FILE = "/etc/pallium/config.json"

DEFAULT_CONFIG = {
  # gmetad server hostname or IP
  "server": "localhost",

  # gmetad request port (prints entire metric tree)
  "request_port": 8651,

  # gmetad interactive port
  "interactive_port": 8652,

  # directory where alerts are stored
  "alerts_dir": "/etc/pallium/alerts",
  
  # directory where metalerts are stored
  "metalerts_dir": "/etc/pallium/metalerts",

  # who to send alert emails to
  "email_to": [],

  # who to send alert emails as
  "email_from": "pallium@%s" % socket.getfqdn(),

  # number of seconds between gmetad queries -- should not be set too low,
  # especially for large grids
  "check_every": 30,
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
