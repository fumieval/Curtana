"""
Bases performing construction and representation
"""
from curtana.lib.prelude import Once

class VoidMix(object):
    def __repr__(self): return self.__class__.__name__ + "()"
    
@Once
def SingleMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "{0}({!r})".format(self.__class__.__name__, self.__dict__[param])
    return type("SingleMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@Once
def UnaryMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%s%r" % (self.__class__.op, self.__dict__[param])
    return type("UnaryMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@Once
def PropertyMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%r.%s" % (self.__dict__[param], self.__class__.attr)
    return type("PropertyMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

@Once
def InfixMix(left="left", right="right"):
    def __init__(self, x, y):
        self.__dict__[left] = x
        self.__dict__[right] = y
    def __repr__(self):
        return "(%r %s %r)" % (self.__dict__[left], self.__class__.op, self.__dict__[right])
    return type("InfixMix({!r}, {!r})".format(left, right), (object,), {"__init__": __init__, "__repr__": __repr__})
