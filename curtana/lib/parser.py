"""
Parsing expression grammar library
"""
from collections import defaultdict

class VoidMix(object):
    def __repr__(self): return self.__class__.__name__ + "()"

class SingleMix(object):
    def __init__(self, x): self._x = x
    def __repr__(self): return "%s(%r)" % (self.__class__.__name__, self._x)

class SingleMix_(object):
    def __init__(self, y): self._y = y
    def __repr__(self): return "%s(%r)" % (self.__class__.__name__, self._y)

class UnaryMix():
    def __init__(self, x): self._x = x
    def __repr__(self): return "%s%r" % (self.__class__.op, self._x)

class InfixMix():
    def __init__(self, left, right):
        self._left = left
        self._right = right
    def __repr__(self):
        return "(%r %s %r)" % (self._left, self.__class__.op, self._right)

class StringI():
    def __init__(self, string, start=0):
        self.string = string
        self.end = len(string)
        self.index = start
        
    def next(self):
        if self.index < self.end:
            c = self.string[self.index]
            self.index += 1
            return c
        else:
            raise StopIteration
    def __repr__(self):
        return "StringI(%r)" % self.remaining
    @property
    def tee(self):
        return StringI(self.string, self.index)
    @property
    def remaining(self):
        return self.string[self.index:]

class Parser(object):
    """Parser base."""
    def __init__(self): pass
    def __and__(self, f):           return Bind(self, f)
    def __div__(self, other):       return Or(self, other)
    def __or__(self, other):        return Or(self, other)
    def __rshift__(self, other):    return DiscardL(self, other)
    def __lshift__(self, other):    return DiscardR(self, other)
    def __mul__(self, other):       return Apply(self, other)
    def __abs__(self):              return And(self)
    def __invert__(self):           return Not(self)
    def __neg__(self):              return Many(self)
    def __pos__(self):              return Many1(self)
    def __rpow__(self, f):          return Lift(f, self)
    def __rxor__(self, f):          return Lift(f, self)
    def __call__(self, string):
        return self.parse(StringI(string))
    def parse(self, string):
        raise NotImplementedError

class Return(Parser, SingleMix):
    """Always returns specified value."""
    __init__ = SingleMix.__init__
    def parse(self, string): return self._x, string

class Any(Parser, VoidMix):
    """Always succeed and consume all of the input."""
    def parse(self, string):
        return string.remaining, iter("")

class Failure(Parser, VoidMix):
    """Always fail."""
    def parse(self, string): return None

class Delay(Parser, SingleMix):
    """It uses the return value of the function.
    This is useful when you want to define a recursive parser."""
    __init__ = SingleMix.__init__
    def parse(self, string): return self._x().parse(string)

class And(Parser, SingleMix):
    """
    Succeeds if the parser succeeded. But it doesn't consume string.
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        return self._x.parse(string.tee) and (None, string)
    def __repr__(self):
        return "abs(%r)" % self._x

class Not(Parser, UnaryMix):
    """
    Succeeds if the parser failed. But it doesn't consume string.
    """
    op = "~"
    __init__ = UnaryMix.__init__
    __repr__ = UnaryMix.__repr__
    def parse(self, string):
        return not self._x.parse(string.tee) and (None, string) or None

class Or(Parser, InfixMix):
    """
    Returns a result of the first parser if the first parser succeed
    otherwise it returns a result of the second parser.
    """
    op = "|"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        return self._left.parse(string.tee) or self._right.parse(string)

class Bind(Parser, InfixMix):
    """
    Compose the parser and the function that takes a result of the parser and returns a parser.
    It's equivalent to Haskell's monad binding (>>=).
    """
    op = "&"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        result = self._left.parse(string)
        return result and self._right(result[0]).parse(result[1])

class DiscardL(Parser, InfixMix):
    """Composite of two parsers, discarding the result of the first parser."""
    op = ">>"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        result0 = self._left.parse(string)
        return result0 and self._right.parse(result0[1])

class DiscardR(Parser, InfixMix):
    """Composite of two parsers, discarding the result of the second parser."""
    op = "<<"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0], result1[1])
                
class Lift(Parser, InfixMix):
    """Lifting of the function to a parser."""
    op = "^"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        result = self._right.parse(string)
        return result and (self._left(result[0]), result[1])

class Apply(Parser, InfixMix):
    """Applying the parser to the parser."""
    op = "*"
    __init__ = InfixMix.__init__
    __repr__ = InfixMix.__repr__
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0](result1[0]), result1[1])

class ApplyN(Parser):
    """
    Apply a function to specified parsers' result.
    """
    def __init__(self, f, *parsers):
        self._f = f
        self._ps = parsers
        
    def __repr__(self):
        return "ApplyN(%r, " + ", ".join(map(repr, self._ps)) + ")"
    
    def parse(self, string):
        t = string
        args = []
        for p in self._ps:
            result = p.parse(t)
            if result:
                args.append(result[0])
                t = result[1]
            else:
                return None
        return self._f(*args), t

class Null(Parser, VoidMix):
    """Matches empty string."""
    def parse(self, string):
        try:
            next(string)
        except StopIteration:
            return ("", string)
        return None

class Sat(Parser, SingleMix):
    """Matches a character satisfying the predicate."""
    __init__ = SingleMix.__init__
    def parse(self, string):
        try:
            char = next(string)
        except StopIteration:
            return None
        return self._x(char) and (char, string) or None

class Char(Sat, SingleMix_):
    """Matches specified character."""
    def __init__(self, char):
        Sat.__init__(self, lambda x: x == char)
        SingleMix_.__init__(self, char)
    __repr__ = SingleMix_.__repr__

class NotChar(Sat, SingleMix_):
    """Matches a character expecting specified character."""
    def __init__(self, char):
        Sat.__init__(self, lambda x: x != char)
        SingleMix_.__init__(self, char)
    __repr__ = SingleMix_.__repr__

class AnyChar(Sat, VoidMix):
    """Matches any character."""
    def __init__(self): Sat.__init__(self, lambda x: True)
    __repr__ = VoidMix.__repr__

class String(Parser, SingleMix):
    """Matches specified string."""
    __init__ = SingleMix.__init__
    def parse(self, string):
        s = ""
        for char in self._x:
            try:
                c = next(string)
            except StopIteration:
                return None
            if char != c:
                return None
            s += c
        return s, string

class Many(Parser, UnaryMix):
    """Applies the parser repeatedly and returns a list of results."""
    op = "-"
    __init__ = UnaryMix.__init__
    __repr__ = UnaryMix.__repr__
    def parse(self, string):
        results = []
        t = string
        while True:
            result = self._x.parse(t.tee)
            if not result:
                return results, t
            results.append(result[0])
            t = result[1]

class Many1(Parser, UnaryMix):
    """Applies the parser repeatedly at least once."""
    op = "+"
    __init__ = UnaryMix.__init__
    __repr__ = UnaryMix.__repr__
    def parse(self, string):
        result = self._x.parse(string)
        if result:
            xs, t = Many(self._x).parse(result[1])
            return [result[0]] + xs, t

class TupleA(tuple):
    def __call__(self, x):
        return TupleA(self + (x,))

class StringA():
    def __init__(self, string=""):
        self.string = string
    def __call__(self, other):
        return StringA(self.string + other)
    def __radd__(self, other):
        if isinstance(other, StringA):
            return other.string + self.string
        else:
            return other + self.string
    def __hash__(self):
        return hash(self.string)
    def __cmp__(self, other):
        if isinstance(other, StringA):
            return self.x.__cmp__(other.string)
        else:
            return self.x.__cmp__(other)
    def __len__(self):
        return len(self.string)
    def __str__(self):
        return str(self.string)
    def __unicode__(self):
        return unicode(self.string)
    def __repr__(self):
        return repr(self.string)

join = "".join

spaces = -Sat(lambda x: x.isspace())
digit = Sat(lambda x: x.isdigit())
alpha = Sat(lambda x: x.isalpha())
alnum = Sat(lambda x: x.isalnum())

nat = int ** join ** +digit