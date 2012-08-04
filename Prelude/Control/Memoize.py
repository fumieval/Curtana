
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
    
    def __call__(self, *args, **kwargs):
        if args in self.memo:
            return self.memo[args]
        else:
            result = self.f(*args, **kwargs)
            self.memo[args] = result
            return result
    
    def force(self, *args, **kwargs):
        result = self.f(*args, **kwargs)
        self.memo[args] = result
        return result
    
    def clear(self):
        self.memo = {}
 
 
