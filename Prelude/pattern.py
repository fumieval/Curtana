from Prelude import map, zip, concat, dropwhile, curry, cons
from Prelude.Data.Tuple import emptyTuple
from Prelude.ParserCombinators import *
from Prelude.ParserCombinators.String import *
from Prelude.ParserCombinators import Python as Py

def construct(pattern):
    patterns = (curry(cons) ** Pattern.parse * -(Char(" ") >> -Pattern.parse))(pattern)
    def run(args):
        results = list(pat.match(x) for pat, x in zip(patterns, args))
        if all(x is not None for x in results):
            return dict(concat(results))
    return run

def build(*definitions):
    definitions_ = [(construct(pat), f) for pat, f in definitions]
    def run(*args):
        for pat, f in definitions_:
            matches = pat(args)
            if matches is not None:
                return f(**matches)
        raise ValueError("No matches")
    return run

class Pattern:
    parse = Delay(lambda: Cons.parse | Var.parse | Atomic.parse | List.parse | Py.parens(Pattern.parse) | Tuple.parse)
    parse_noncons = Delay(lambda: Var.parse | Atomic.parse | List.parse | Py.parens(Pattern.parse) | Tuple.parse)
    def match(self, value):
        raise NotImplementedError

class Var(Single("name")):
    parse = Delay(lambda: Var ** Py.identifier)
    def match(self, value):
        return [(self.name, value)] * (self.name != "_")

class Atomic(Single("value")):
    parse = Delay(lambda: Atomic ** Py.literal)
    def match(self, value):
        if self.value == value:
            return []

class List(Single("items")):
    parse = Delay(lambda: List ** Py.brackets(Py.expression_list(Pattern.parse)))
    def match(self, value):
        if len(self.items) == len(self.items):
            results = list(pat.match(x) for pat, x in zip(self.items, value))
            if all(results):
                return list(concat(results))
    
class Tuple(Single("items")):
    parse = Delay(lambda: Tuple ** Py.parens(Py.expression_list(Pattern.parse)))
    def match(self, value):
        if len(self.items) == len(self.items):
            results = list(pat.match(x) for pat, x in zip(self.items, value))
            if all(x is not None for x in results):
                return list(concat(results))

class Cons(Multi("x", "xs")):
    parse = Delay(lambda: curry(Cons) ** Pattern.parse_noncons * (Char(":") >> Pattern.parse))
    def match(self, value):
        if len(value) > 0:
            y = self.x.match(value[0])
            if y:
                ys = self.xs.match(value[1:])
                return ys and y + ys
