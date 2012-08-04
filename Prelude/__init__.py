from Prelude.Data.Iterables import *
from Prelude.classes import *

__all__ = [
    "map", "filter", "zip", "take", "drop", "takewhile", "dropwhile", "concat", "count",
    "ident", "const", "par", "flip", "fanout", "compose", "flip", "star", "unstar", "fix"
    "Functor", "Applicative", "Monad"
    ]

def static(f):
    return f()

# miscellaneous
def cons(x, xs):
    return [x] + xs