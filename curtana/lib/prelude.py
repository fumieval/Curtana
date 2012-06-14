import functools
import itertools

map = itertools.imap
filter = itertools.ifilter

par = functools.partial

def fanout(f, g):
    def fanout_applicand(x):
        return f(x), g(x)
    return fanout_applicand

def compose(f, g):
    return lambda *args: f(g(*args))

def fix(f):
    return par(f, lambda *args: fix(f)(*args))

def flip(f):
    def flip_applicand(x):
        def flip_applicand_(y):
            return f(y, x)
        return flip_applicand_
    return flip_applicand

def star(f):
    def star_applicand(x):
        return f(*x)
    return star_applicand

def unstar(f):
    def unstar_applicand(*args):
        return f(args)
    return unstar_applicand

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
