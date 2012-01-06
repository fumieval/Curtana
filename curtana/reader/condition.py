import curtana.lib.parser_aliases as P

source_parser = \
    ((lambda x: lambda y: (y, x))
     ** (P.S('<a href="') >> "".join ** -P.D('"') << -P.NC(">") << P.AC
     * "".join ** -P.NC("<") << P.A)
     | P.A)

class Condition(object):
    def parse(self, data):
        pass
    def __invert__(self):
        return Not(self)
    def __or__(self, other):
        return Or(self, other)
    def __and__(self, other):
        return And(self, other)
    def __rshift__(self, other):
        return Item(other, self)

class Return(Condition):
    def __init__(self, value):
        self._v = value
    def check(self, data):
        return self._v

class Not(Condition):
    def __init__(self, condition):
        self._c = condition
    def check(self, data):
        return not self._c.check(data)

class Or(Condition):
    def __init__(self, left, right):
        self._left = left
        self._right = right
    def check(self, data):
        return self._left.check(data) or self._right.check(data)

class And(Condition):
    def __init__(self, left, right):
        self._left = left
        self._right = right
    def check(self, data):
        return self._left.check(data) and self._right.check(data)

class Sat(Condition):
    def __init__(self, predicate):
        self._p = predicate
    def check(self, data):
        return self._p(data)

class Item(Condition):
    def __init__(self, key, condition):
        self._k = key
        self._c = condition
    def check(self, data):
        return self._c(data[self._k])

class Eq(Condition):
    def __init__(self, value):
        self._v = value
    def check(self, data):
        return self._v == data

class Apply(Condition):
    def __init__(self, f, condition):
        self._f = f
        self._c = condition
    def check(self, data):
        return self._c(self._f(data))

def hasKey(*names):
    if len(names) == 0:
        return Return(True)
    else:
        return Sat(lambda data: names[0] in data) & hasKey(names[1:])

def include(word):
    return Sat(lambda data: word in data["text"])

def fromUser(screen_name):
    return Eq(screen_name) << "user" << "screen_name"

def fromUsers(screen_names):
    return Sat(lambda x: x in screen_names) << "user" << "screen_name"

def fromSource(name):
    return Sat(lambda data: name == source_parser(data["source"])[0])