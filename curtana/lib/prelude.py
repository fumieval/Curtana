"""
Curtana Standard Prelude
"""
import functools
import itertools

map = itertools.imap
filter = itertools.ifilter

par = functools.partial

def fanout(f, g):
    """fanout(f, g)(x) = (f(x), g(x))"""
    def fanout_applicand(x):
        return f(x), g(x)
    return fanout_applicand

def compose(f, g):
    """compose(f, g)(x) = f(g(x))"""
    def compose_applicand(*args):
        return f(g(*args))
    return compose_applicand

def fix(f):
    """fix(f) = par(f, fix(f))"""
    return par(f, lambda *args: fix(f)(*args))

def flip(f):
    """flip(f)(x)(y) = f(y, x)"""
    def flip_applicand(x):
        def flip_applicand_(y):
            return f(y, x)
        return flip_applicand_
    return flip_applicand

def star(f):
    """star(f)((x, y)) = f(x, y)"""
    def star_applicand(x):
        return f(*x)
    return star_applicand

def unstar(f):
    """unstar(f)(x, y) = f((x, y))"""
    def unstar_applicand(*args):
        return f(args)
    return unstar_applicand

class once:
    """
    Example usage:
    >>> @once
    ... def fib(n):
    ...     if n <= 1:
    ...         return n
    ...     else:
    ...         return fib(n - 1) + fib(n - 2)
    >>> fib(100)
    354224848179261915075L
    """
    def __init__(self, f):
        self.f = f
        self.memo = {}
    
    @property
    def __doc__(self):
        return self.f.__doc__
    
    def __call__(self, *args):
        if args in self.memo:
            return self.memo[args]
        else:
            result = self.f(*args)
            self.memo[args] = result
            return result
    
    def force(self, *args):
        result = self.f(*args)
        self.memo[args] = result
        return result
    
    def clear(self):
        self.memo = {}

if __name__ == "__main__":
    import doctest
    doctest.testmod()