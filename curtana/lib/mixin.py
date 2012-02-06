class VoidMix(object):
    def __repr__(self): return self.__class__.__name__ + "()"

class SingleMix(object):
    def __init__(self, x): self._x = x
    def __repr__(self): return "%s(%r)" % (self.__class__.__name__, self._x)

class SingleMix_(object):
    def __init__(self, y): self._y = y
    def __repr__(self): return "%s(%r)" % (self.__class__.__name__, self._y)

class UnaryMix(object):
    def __init__(self, x): self._x = x
    def __repr__(self): return "%s%r" % (self.__class__.op, self._x)

class PropertyMix(object):
    def __init__(self, x): self._x = x
    def __repr__(self): return "%r.%s" % (self._x, self.__class__.attr)

class InfixMix(object):
    def __init__(self, left, right):
        self._left = left
        self._right = right
    def __repr__(self):
        return "(%r %s %r)" % (self._left, self.__class__.op, self._right)
