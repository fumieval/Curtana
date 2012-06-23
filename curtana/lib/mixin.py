"""
Bases performing construction and representation
"""
from curtana.lib.prelude import once
import itertools as I

@once
def MultiMix(*params):
    """Example usage:
    >>> class Hoge(M.MultiMix('x', 'y', 'z')):
    ...    def sum(self):
    ...        return self.x + self.y + self.z
    ...    def product(self):
    ...        return self.x * self.y * self.z
    >>> hoge = Hoge(1, 2, 4)
    >>> hoge
    Hoge(1, 2, 4)
    >>> hoge.sum()
    7
    >>> hoge.product()
    8
    """
    def __init__(self, *args, **kwargs):
        arg = iter(args)
        for name in params:
            try:
                value = next(arg)
            except StopIteration:
                value = kwargs[name]
            self.__dict__[name] = value
        
    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(I.imap(repr, I.imap(self.__dict__.__getitem__, params))) + ")"
    return type("MultiMix({!r})".format(params), (object,), {"__init__": __init__, "__repr__": __repr__})

class VoidMix(object):
    def __repr__(self): return self.__class__.__name__ + "()"

@once
def SingleMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "{0}({!r})".format(self.__class__.__name__, self.__dict__[param])
    return type("SingleMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@once
def UnaryMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%s%r" % (self.__class__.op, self.__dict__[param])
    return type("UnaryMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@once
def PropertyMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%r.%s" % (self.__dict__[param], self.__class__.attr)
    return type("PropertyMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@once
def InfixMix(left="left", right="right"):
    def __init__(self, x, y):
        self.__dict__[left] = x
        self.__dict__[right] = y
    def __repr__(self):
        return "(%r %s %r)" % (self.__dict__[left], self.__class__.op, self.__dict__[right])
    return type("InfixMix({!r}, {!r})".format(left, right), (object,), {"__init__": __init__, "__repr__": __repr__})
