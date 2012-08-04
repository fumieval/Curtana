import functools

ident = lambda x: x
const = lambda x: lambda y: x
par = functools.partial

def fanout(f, g):
    """fanout(f, g)(x) = (f(x), g(x))"""
    def fanout_applicand(x): return f(x), g(x)
    return fanout_applicand

def compose(f, g):
    """compose(f, g)(x) = f(g(x))"""
    def compose_applicand(*args): return f(g(*args))
    return compose_applicand

def flip(f):
    """flip(f)(x)(y) = f(y, x)"""
    def flip_applicand(x):
        def flip_applicand_(y): return f(y, x)
        return flip_applicand_
    return flip_applicand 

def star(f):
    """star(f)((x, y)) = f(x, y)"""
    def star_applicand(x): return f(*x)
    return star_applicand

def unstar(f):
    """unstar(f)(x, y) = f((x, y))"""
    def unstar_applicand(*args): return f(args)
    return unstar_applicand

def curry(f):
    """curry(f)(x)(y) = f(x, y)"""
    return lambda x: lambda y: f(x, y)

def uncurry(f):
    """curry(f)(x, y) = f(x)(y)"""
    def uncurry_applicand(*args):
        g = f
        for arg in args:
            g = f(arg)
        return g

def fix(f):
    """fix(f) = par(f, fix(f))"""
    return par(f, lambda *args: fix(f)(*args))
 
