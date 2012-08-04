from Prelude.mixin import *
from Prelude.classes import *

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

class Parser(object, Alternative, Monad):
    """Parser base.
    type: Parser NoneType
    """
    def fmap(self, f):      return Lift(f, self)
    @staticmethod
    def pure(x):            return Return(x)
    @staticmethod
    def empty():            return Failure()
    def ap(self, other):    return Apply(self, other)
    def alt(self, other):   return Or(self, other)
    def bind(self, f):      return Bind(self, f)
    
    def __rshift__(self, other):    return DiscardL(self, other)
    def __lshift__(self, other):    return DiscardR(self, other)

    def __abs__(self):              return And(self)
    def __invert__(self):           return Not(self)
    
    def __neg__(self):              return Many(self)
    def __pos__(self):              return Some(self)
    def __mod__(self, n):           return Repeat(self, n)
    def __add__(self, f):           return Concat(self, f)
    def __call__(self, stream):
        raise NotImplementedError
    def parse(self, stream):
        return NotImplementedError
    def __call__(self, stream):
        result = self.parse(StringI(stream))
        return result and result[0]
    def parse_stream(self, stream):
        result = self.parse(StringI(stream))
        return result and (result[0], result[1].remaining)
        
class Strict(Parser, Single()):
    """
    Raises a exception iff the parser failed.
    type: Parser -> Parser
    """
    def parse(self, stream):
        s, t = stream.used, stream.remaining
        result = self.x.parse(stream)
        if result:
            return result
        else:
            raise ParserError("Parse error on '%s' : expecting %r after '%s'" % (t, self.x, s))

class Return(Parser, Single()):
    """Always returns specified value.
    type: a -> Parser a
    """
    def parse(self, stream): return self.x, stream

class Any(Parser, Void):
    """Always succeed and consume all of the input.
    type: Parser stream
    """
    def parse(self, stream):
        return stream.remaining, StringI("")

class Failure(Parser, Void):
    """Always fail.
    type: Parser a
    """
    def parse(self, stream): return None

class Delay(Parser, Single()):
    """It uses the return value of the function.
    This is useful when you want to define a recursive parser.
    type: (() -> Parser a) -> Parser a
    """
    def parse(self, stream): return self.x().parse(stream)

class And(Parser, Single()):
    """
    Succeeds if the parser succeeded. But it doesn't consume stream.
    type: Parser a -> Parser NoneType
    """
    def parse(self, stream):
        return self.x.parse(stream.tee) and (None, stream)
    def __repr__(self, stream):
        return "abs(%r)" % self.x

class Not(Parser, Unary()):
    """
    Succeeds if the parser failed. But it doesn't consume stream.
    type: Parser a -> Parser NoneType
    """
    op = "~"
    def parse(self, stream):
        return not self.x.parse(stream.tee) and (None, stream) or None

class Or(Parser, Infix()):
    """
    Returns a result of the first parser if the first parser succeed
    otherwise it returns a result of the second parser.
    type: (Parser a, Parser b) -> Parser (Either a b)
    """
    op = "|"
    def parse(self, stream):
        return self.left.parse(stream.tee) or self.right.parse(stream)

class Bind(Parser, Infix()):
    """
    Compose the parser and the function that takes a result of the parser and returns a parser.
    It's equivalent to Haskell's monad binding (>>=).
    type: (Parser a, a -> Parser b) -> Parser b
    """
    op = "&"
    def parse(self, stream):
        result = self.left.parse(stream)
        return result and self.right(result[0]).parse(result[1])

class DiscardL(Parser, Infix()):
    """Composite of two parsers, discarding the result of the first parser.
    type: (Parser a, Parser b) -> Parser b
    """
    op = ">>"
    def parse(self, stream):
        result0 = self.left.parse(stream)
        return result0 and self.right.parse(result0[1])

class DiscardR(Parser, Infix()):
    """Composite of two parsers, discarding the result of the second parser.
    type: (Parser a, Parser b) -> Parser a
    """
    op = "<<"
    def parse(self, stream):
        result0 = self.left.parse(stream)
        if result0:
            result1 = self.right.parse(result0[1])
            return result1 and (result0[0], result1[1])
                
class Lift(Parser, Infix()):
    """Lifting of the function to a parser.
    type: (a -> b, Parser a) -> Parser b
    """
    op = "^"
    def parse(self, stream):
        result = self.right.parse(stream)
        return result and (self.left(result[0]), result[1])

class Apply(Parser, Infix()):
    """Applying the parser to the parser.
    type: (Parser (a -> b), Parser a) -> Parser b
    """
    op = "*"
    def parse(self, stream):
        result0 = self.left.parse(stream)
        if result0:
            result1 = self.right.parse(result0[1])
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
    
    def parse(self, stream):
        t = stream
        args = []
        for p in self._ps:
            result = p.parse(t)
            if result:
                args.append(result[0])
                t = result[1]
            else:
                return None
        return self._f(*args), t
 
class Many(Parser, Unary()):
    """Applies the parser repeatedly and returns a list of results.
    type: Parser a -> Parser [a]
    """
    op = "-"
    def parse(self, stream):
        results = []
        t = stream
        while True:
            result = self.x.parse(t.tee)
            if not result:
                return results, t
            results.append(result[0])
            t = result[1]

class Some(Parser, Unary()):
    """Applies the parser repeatedly at least once.
    type: Parser a -> Parser [a]
    """
    op = "+"
    def parse(self, stream):
        result = self.x.parse(stream)
        if result:
            xs, t = Many(self.x).parse(result[1])
            return [result[0]] + xs, t

class Repeat(Parser, Infix()):
    op = "%"
    def parse(self, stream):
        result = []
        s = stream
        for _ in xrange(self.right):
            r = self.left.parse(s)
            if r:
                result.append(r[0])
                s = r[1]
            else:
                return None
        return result, stream

class Concat(Parser, Infix()):
    op = "+"
    def parse(self, string):
        result0 = self.left.parse(string)
        if result0:
            result1 = self.right.parse(result0[1])
            return result1 and (result0[0] + result1[0], result1[1])