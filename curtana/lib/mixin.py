"""
Bases performing construction and representation
"""
class VoidMix(object):
    def __repr__(self): return self.__class__.__name__ + "()"

def SingleMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.__dict__[param])
    return type("SingleMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

def UnaryMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%s%r" % (self.__class__.op, self.__dict__[param])
    return type("UnaryMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

def PropertyMix(param="x"):
    def __init__(self, x):
        self.__dict__[param] = x
    def __repr__(self):
        return "%r.%s" % (self.__dict__[param], self.__class__.attr)
    return type("PropertyMix({!r})".format(param), (object,), {"__init__": __init__, "__repr__": __repr__})

def InfixMix(left="left", right="right"):
    def __init__(self, left, right):
        self.__dict__[left] = left
        self.__dict__[right] = right
    def __repr__(self):
        return "(%r %s %r)" % (self.__dict__[left], self.__class__.op, self.__dict__[right])
    return type("InfixMix({!r}, {!r})".format(left, right), (object,), {"__init__": __init__, "__repr__": __repr__})
