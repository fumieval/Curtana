"""
Parsing expression grammar (?) library
"""

__all__ = ["ParserError", "Parser", "Strict", "Return", "Any", "Failure", "Delay", "ApplyN",
           "Null", "Sat", "Char", "NotChar", "AnyChar",
           "String", "Until", "Delimit", "Find", "Regex"]

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

class ParserError(Exception):
    pass

class StringI(object):
    def __init__(self, string, start=0):
        self.string = string
        self.end = len(string)
        self.start = start
        self.index = start
        
    def next(self):
        if self.eos:
            raise StopIteration
        else:
            c = self.string[self.index]
            self.index += 1
            return c
            raise StopIteration
    def __repr__(self):
        return "StringI(%r)" % self.remaining
    def reset(self):
        self.index = self.start
    @property
    def tee(self):
        return StringI(self.string, self.index)
    @property
    def used(self):
        return self.string[:self.index]
    @property
    def remaining(self):
        return self.string[self.index:]
    @property
    def peek(self):
        return self.string[self.index]
    @property
    def eos(self):
        return self.index == self.end

class Parser(object):
    """Parser base.
    type: Parser NoneType
    """
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
    def __mod__(self, n):           return Repeat(self, n)
    def __rpow__(self, f):          return Lift(f, self)
    def __rxor__(self, f):          return Lift(f, self)
    def __add__(self, f):           return Concat(self, f)
    
    @property
    def opt(self):                  return Optional(self)
    
    def __call__(self, string):
        result = self.parse(StringI(string))
        return result and result[0]
    def parse_string(self, string):
        result = self.parse(StringI(string))
        return result and (result[0], result[1].remaining)
    def parse(self, string):
        return None, string

class Strict(Parser, SingleMix):
    """
    Raises a exception iff the parser failed.
    type: Parser -> Parser
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        s, t = string.used, string.remaining
        result = self._x.parse(string)
        if result:
            return result
        else:
            raise ParserError("Parse error on '%s' : expecting %r after '%s'" % (t, self._x, s))

class Return(Parser, SingleMix):
    """Always returns specified value.
    type: a -> Parser a
    """
    __init__ = SingleMix.__init__
    def parse(self, string): return self._x, string

class Any(Parser, VoidMix):
    """Always succeed and consume all of the input.
    type: Parser string
    """
    def parse(self, string):
        return string.remaining, StringI("")

class Failure(Parser, VoidMix):
    """Always fail.
    type: Parser a
    """
    def parse(self, string): return None

class Delay(Parser, SingleMix):
    """It uses the return value of the function.
    This is useful when you want to define a recursive parser.
    type: (() -> Parser a) -> Parser a
    """
    __init__ = SingleMix.__init__
    def parse(self, string): return self._x().parse(string)

class And(Parser, SingleMix):
    """
    Succeeds if the parser succeeded. But it doesn't consume string.
    type: Parser a -> Parser NoneType
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        return self._x.parse(string.tee) and (None, string)
    def __repr__(self, string):
        return "abs(%r)" % self._x

class Not(Parser, UnaryMix):
    """
    Succeeds if the parser failed. But it doesn't consume string.
    type: Parser a -> Parser NoneType
    """
    op = "~"
    __init__ = UnaryMix.__init__
    def parse(self, string):
        return not self._x.parse(string.tee) and (None, string) or None

class Optional(Parser, PropertyMix):
    """
    Returns the parser's result. but if the parser failed, it returns None.
    type: Parser a -> Parser (Either a NoneType)
    """
    attr = "opt"
    __init__ = PropertyMix.__init__
    def parse(self, string):
        result = self._x.parse(string)
        return result or (None, string)

class Or(Parser, InfixMix):
    """
    Returns a result of the first parser if the first parser succeed
    otherwise it returns a result of the second parser.
    type: (Parser a, Parser b) -> Parser (Either a b)
    """
    op = "|"
    __init__ = InfixMix.__init__
    def parse(self, string):
        return self._left.parse(string.tee) or self._right.parse(string)

class Bind(Parser, InfixMix):
    """
    Compose the parser and the function that takes a result of the parser and returns a parser.
    It's equivalent to Haskell's monad binding (>>=).
    type: (Parser a, a -> Parser b) -> Parser b
    """
    op = "&"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result = self._left.parse(string)
        return result and self._right(result[0]).parse(result[1])

class DiscardL(Parser, InfixMix):
    """Composite of two parsers, discarding the result of the first parser.
    type: (Parser a, Parser b) -> Parser b
    """
    op = ">>"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result0 = self._left.parse(string)
        return result0 and self._right.parse(result0[1])

class DiscardR(Parser, InfixMix):
    """Composite of two parsers, discarding the result of the second parser.
    type: (Parser a, Parser b) -> Parser a
    """
    op = "<<"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0], result1[1])
                
class Lift(Parser, InfixMix):
    """Lifting of the function to a parser.
    type: (a -> b, Parser a) -> Parser b
    """
    op = "^"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result = self._right.parse(string)
        return result and (self._left(result[0]), result[1])

class Apply(Parser, InfixMix):
    """Applying the parser to the parser.
    type: (Parser (a -> b), Parser a) -> Parser b
    """
    op = "*"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0](result1[0]), result1[1])

class ApplyN(Parser):
    """
    Apply a function to specified parsers' result.
    type: ((a, b, c, ...) -> z, Parser a, Parser b, Parser c,...) -> Parser z
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
    """Matches empty string.
    type: Parser string
    """
    def parse(self, string):
        if string.eos:
            return ("", string)

class Sat(Parser, SingleMix):
    """Matches a character satisfying the predicate.
    type: (char -> bool) -> Parser char
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        try:
            char = next(string)
        except StopIteration:
            return None
        return self._x(char) and (char, string) or None

class Char(Sat, SingleMix_):
    """Matches specified character.
    type: char -> Parser char
    """
    def __init__(self, char):
        Sat.__init__(self, lambda x: x == char)
        SingleMix_.__init__(self, char)
    __repr__ = SingleMix_.__repr__

class NotChar(Sat, SingleMix_):
    """Matches a character expecting specified character.
    type: char -> Parser char
    """
    def __init__(self, char):
        Sat.__init__(self, lambda x: x != char)
        SingleMix_.__init__(self, char)
    __repr__ = SingleMix_.__repr__

class AnyChar(Sat, VoidMix):
    """Matches any character.
    type: Parser char
    """
    def __init__(self): Sat.__init__(self, lambda x: True)
    __repr__ = VoidMix.__repr__

class String(Parser, SingleMix):
    """Matches specified string.
    type: string -> Parser string
    """
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

class Until(Parser, SingleMix):
    """Delimits by the parser.
    type: parser -> Parser string
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        s = ""
        while True:
            r = self._x.parse(string.tee)
            if r:
                return s, string
            try:
                s += next(string)
            except StopIteration:
                break
        return s, string

class Delimit(Parser, SingleMix):
    """Delimits by the parser.
    type: parser -> Parser string
    """
    __init__ = SingleMix.__init__
    def parse(self, string):
        s = ""
        while True:
            r = self._x.parse(string.tee)
            if r:
                return s, r[1]
            try:
                s += next(string)
            except StopIteration:
                break
        return s, string

class Find(Parser, SingleMix):
    __init__ = SingleMix.__init__
    def parse(self, string):
        while True:
            r = self._x.parse(string.tee)
            if r:
                return r
            try:
                next(string)
            except StopIteration:
                break

class Concat(Parser, InfixMix):
    op = "+"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result0 = self._left.parse(string)
        if result0:
            result1 = self._right.parse(result0[1])
            return result1 and (result0[0] + result1[0], result1[1])

class Many(Parser, UnaryMix):
    """Applies the parser repeatedly and returns a list of results.
    type: Parser a -> Parser [a]
    """
    op = "-"
    __init__ = UnaryMix.__init__
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
    """Applies the parser repeatedly at least once.
    type: Parser a -> Parser [a]
    """
    op = "+"
    __init__ = UnaryMix.__init__
    def parse(self, string):
        result = self._x.parse(string)
        if result:
            xs, t = Many(self._x).parse(result[1])
            return [result[0]] + xs, t

class Regex(Parser, SingleMix):
    def __init__(self, x):
        import re
        SingleMix.__init__(self, x)
        self.re = re.compile(x)
    def parse(self, string):
        result = self.re.search(string.remaining)
        return result and (result.group(), string.remaining[result.end():])
        
class Repeat(Parser, InfixMix):
    op = "%"
    __init__ = InfixMix.__init__
    def parse(self, string):
        result = []
        s = string
        for _ in xrange(self._right):
            r = self._left.parse(s)
            if r:
                result.append(r[0])
                s = r[1]
            else:
                return None
        return result, string
