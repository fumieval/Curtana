import functools
import itertools

map = itertools.imap
filter = itertools.ifilter

par = functools.partial

def fanout(f, g):
    return lambda x: (f(x), g(x))

def compose(f, g):
    return lambda *args: f(g(args))

def fix(f):
    return par(f, lambda *args: fix(f)(*args))

def flip(f):
    return lambda x: lambda y: f(y, x)

def star(f):
    return lambda x: f(*x)
    
class Memoize:
    """
    Example usage:
    >>> @Memoize
    ... def fib(n):
    ...     if n <= 1:
    ...         return n
    ...     else:
    ...         return fib(n - 1) + fib(n - 2)
    >>> fib(300)
    222232244629420445529739893461909967206666939096499764990979600L
    """
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        if args in self.memo:
            return self.memo[args]
        else:
            result = self.f(*args)
            self.memo[args] = result
            return result
