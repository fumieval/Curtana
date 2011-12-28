import itertools
import operator
import re

def infixMix(op):
    def _init(self, left, right):
        self._left = left
        self._right = right
    def _repr(self):
        return "(%r %s %r)" % (self._left, op, self._right)
    return type("InfixMix", (), {"__init__": _init, "__repr__": _repr})

class VoidMix():
    def __repr__(self):
        return self.__class__.__name__ + "()"

class SingleMix():
    def __init__(self, x):
        self._x = x
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._x)

class Parser():
    """Parser base."""
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
    
    def parse(self, string):
        raise NotImplementedError

    __call__ = parse

class Return(Parser, SingleMix):
    """Always returns specified value."""
    def parse(self, string): return self._x, string

class Any(Parser, VoidMix):
    """Always succeed and consume all of the input."""
    def parse(self, string): return string, ""

class Failure(Parser, VoidMix):
    """Always fail."""
    def parse(self, string): return None

class Delay(Parser, SingleMix):
    """It uses the return value of the function.
    This is useful when you want to define a recursive parser."""
    def parse(self, string): return self._x().parse(string)

class And(Parser, SingleMix):
    """
    Succeeds if a parser succeeded. But it doesn't consume string.
    """
    def parse(self, string):
        return self._x.parse(string) and (None, string)

class Not(Parser, SingleMix):
    """
    Succeeds if a parser failed. But it doesn't consume string.
    """
    def parse(self, string):
        return not self._x.parse(string) and (None, string) or None

class Or(Parser, infixMix("|")):
    """
    Returns a result of the first parser if the first parser succeed
    otherwise it returns a result of the second parser.
    """
    def parse(self, string):
        return self._left.parse(string) or self._right.parse(string)

class Bind(Parser, infixMix("&")):
    """
    Compose a parser and a function that takes a result of the parser and returns a parser.
    It's equivalent to Haskell's monad binding (>>=).
    """
    def parse(self, string):
        result = self._left.parse(string)
        return result and self._right(result[0]).parse(result[1])

class DiscardL(Parser, infixMix(">>")):
    """Composite of two parsers, discarding the result of the first parser."""
    def parse(self, string):
        result0 = self._left.parse(string)
        return result0 and self._right.parse(result0[1])

class DiscardR(Parser, infixMix("<<")):
    """Composite of two parsers, discarding the result of the second parser."""  
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0], result1[1])
                
class Lift(Parser, infixMix("^")):
    """Lifting of the function to a parser."""
    def parse(self, string):
        result = self._right.parse(string)
        return result and (self._left(result[0]), result[1])

class Apply(Parser, infixMix("*")):
    """Applying the parser to the parser."""
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
        return "ApplyN(%r, " + ", ".join(self._ps) + ")"
    
    def parse(self, string):
        t = string
        args = []
        for p in self._ps:
            result = p.parse(t)
            if result:
                args.append(result[1])
                t = result[1]
            else:
                return None
        return self._f(*args)

class Null(Parser, VoidMix):
    """Matches empty string."""
    def parse(self, string): return string == "" and (string, "")

class Sat(Parser, SingleMix):
    """Matches a character satisfying the predicate."""
    def parse(self, string):
        if string:
            return self._x(string[0]) and (string[0], string[1:]) or None

class Char(Sat, SingleMix):
    """Matches specified character."""
    def __init__(self, char):
        Sat.__init__(self, lambda x: x == char)
        SingleMix.__init__(self, char)

class NotChar(Sat, SingleMix):
    """Matches a character expecting specified character."""
    def __init__(self, char):
        Sat.__init__(self, lambda x: x != char)
        SingleMix.__init__(self, char)

class AnyChar(Char, VoidMix):
    """Matches any character."""
    def __init__(self): Sat.__init__(self, lambda x: True)

class String(Parser, SingleMix):
    """Matches specified string."""
    def parse(self, string):
        return len(string) < len(self._x) and \
            all(itertools.imap(operator.eq, self._x, string)) and \
            self._string, string[len(self._x):] or None

class Many(Parser, SingleMix):
    """Applies a parser repeatedly and returns a list of results."""  
    def parse(self, string):
        results = []
        t = string
        while t:
            result = self._x.parse(t)
            if not result:
                break
            results.append(result[0])
            t = result[1]
        return results, t

class Many1(Many, SingleMix):
    """Applies a parser repeatedly at least once."""
    def parse(self, string):
        result = self._x.parse(string)
        if result:
            xs, t = Many.parse(self, result[1])
            return [result[0]] + xs, t

class Delimited(Parser, SingleMix):
    """Aplits input by first occurring of specified string."""
    def parse(self, string):
        i = string.find(self._x)
        return string[:i], string[i + len(self._x):]

class Regex(Parser, SingleMix):
    """Matches specified regex pattern."""
    def __init__(self, pattern):
        self.re = re.compile(pattern)
        SingleMix.__init__(self, pattern)
    def parse(self, string):
        m = self.re.match(string)
        return m and string[m.end():]

class TupleA(tuple):
    def __call__(self, x):
        return TupleA(self + (x,))

class StringA():
    def __init__(self, x=""):
        self.x = x
    def __call__(self, other):
        return StringA(self.x + other)
    def __repr__(self):
        return repr(self.x)

join = "".join

spaces = -Sat(lambda x: x.isspace())
digit = Sat(lambda x: x.isdigit())
alpha = Sat(lambda x: x.isalpha())
alnum = Sat(lambda x: x.isalnum())

nat = int ** join ** +digit