
def ixmap(f, dicts):
    return ((f(key), value) for key, value in dicts.iteritems())