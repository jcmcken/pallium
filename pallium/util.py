import os

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

def files_from_dir(directory):
    files = []
    for filename in os.listdir(directory):
        fullname = os.path.join(os.path.abspath(directory), filename)
        # resolve links
        if os.path.islink(fullname):
            fullname = os.readlink(fullname)
        # skip non-files
        if not os.path.isfile(fullname):
            continue

        files.append(fullname)
    return files
