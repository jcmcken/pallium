DICT1 = {
  "key1": {
    "key2": "",
    "key3": "key4",
  },
  "key5": "key6"
}

DICT2 = {
  "key1": {
    "key2": "key7",
    "key3": "key8",
  },
  "key5": False
}


from pallium.util import _recursive_update, SuperDict

def test_recursive_update():
    d = DICT1.copy()
    u = DICT2.copy()
    n = _recursive_update(d, u)

    assert n == DICT2

def test_super_dict():
    d = SuperDict(DICT1)
    u = DICT2.copy()

    d.recursive_update(u)

    assert dict(d) == DICT2
