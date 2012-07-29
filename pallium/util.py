def _recursive_update(d, u):
    """
    Yanked from ``http://stackoverflow.com/questions/3232943/``

    Recursively update dictionary ``d`` with ``u``
    """
    for k, v in u.iteritems():
        if isinstance(v, dict):
            r = _recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

class SuperDict(dict):
    def recursive_update(self, updated):
        self = SuperDict(_recursive_update(self, updated))
