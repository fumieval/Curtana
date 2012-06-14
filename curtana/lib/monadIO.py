"""
Monadic actions
"""
from curtana.lib.mixin import SingleMix, InfixMix
import functools

__all__ = ["IOZero", "IOException", "IOOne", "IO", "Return", "IOWrapper", "Satisfy", "IOFunction", "wrapIO", "funcIO", "joinIO"]

class IOZeroType:
    def __repr__(self):
        return "IOZero"
    def __nonzero__(self):
        return False

IOZero = IOZeroType()

class IOException(IOZeroType):
    def __init__(self, exception):
        self.exception = exception
    def raise_(self):
        raise self.exception

class IOOneType:
    def __repr__(self):
        return "IOOne"
    def __nonzero__(self):
        return True
    
IOOne = IOOneType()

class Ref(SingleMix("value")):
    pass

class IO:
    def __init__(self): pass
    def __and__(self, f):           return Bind(self, f)
    def __or__(self, other):        return Or(self, other)
    def __rshift__(self, other):    return DiscardL(self, other)
    def __lshift__(self, other):    return DiscardR(self, other)
    def __mul__(self, other):       return Apply(self, other)
    def __rpow__(self, f):          return Lift(f, self)
    def __rxor__(self, f):          return Lift(f, self)
    def do(self):
        raise NotImplementedError

class ReadRef(IO):
    def __init__(self, ref):
        self.ref = ref
    def do(self):
        return self.ref.value
    def __repr__(self):
        return "ReadRef({0})".format(self.ref)

class WriteRef(IO):
    def __init__(self, ref, value):
        self.ref = ref
        self.value = value
    def do(self):
        self.ref.value = self.value
        return IOOne
    def __repr__(self):
        return "WriteRef({0}, {1})".format(self.ref, self.value)

class ModifyRef(IO):
    def __init__(self, ref, f):
        self.ref = ref
        self.f = f   
    def do(self):
        self.ref.value = self.f(self.ref.value)
        return IOOne     
    def __repr__(self):
        return "ModifyRef({0}, {1})".format(self.ref, self.f)

class Return(IO, SingleMix()):
    __init__ = SingleMix().__init__
    def do(self):
        return self.x

class Bind(IO, InfixMix()):
    op = "&"
    __init__ = InfixMix().__init__
    def do(self):
        result = self.left.do()
        if isinstance(result, IOZeroType):
            return result
        return self.right(result).do()

class DiscardL(IO, InfixMix()):
    op = ">>"
    __init__ = InfixMix().__init__            
    def do(self):
        result = self.left.do()
        if isinstance(result, IOZeroType):
            return result
        return self.right.do()

class DiscardR(IO, InfixMix()):
    op = "<<"
    __init__ = InfixMix().__init__            
    def do(self):
        result = self.left.do()
        if isinstance(result, IOZeroType):
            return result
        self.right.do()
        return result

class Or(IO, InfixMix()):
    op = "|"
    __init__ = InfixMix().__init__
    def do(self):
        result = self.left.do()
        if isinstance(result, IOZeroType):
            return self.right.do()
        return result    

class Lift(IO, InfixMix()):
    op = "^"
    __init__ = InfixMix().__init__
    def do(self):
        result = self.right.do()
        if isinstance(result, IOZeroType):
            return result
        return self.left(result)

class Apply(IO, InfixMix()):
    op = "*"
    __init__ = InfixMix().__init__    
    def do(self):
        f = self.left.do()
        if isinstance(f, IOZeroType):
            return f
        x = self.right.do()
        if isinstance(x, IOZeroType):
            return x
        return f(x)

class Satisfy(IO, SingleMix("predicate")):
    __init__ = SingleMix("predicate").__init__
    def do(self):
        if self.predicate():
            return IOOne
        else:
            return IOZero

class IOFunction(IO, SingleMix()):
    __init__ = SingleMix().__init__
    def do(self):
        return self.x()

class IOWrapper(IO):
    def __init__(self, f, *args, **kwargs):
        self.f = functools.partial(f, *args, **kwargs)
    def do(self):
        try:
            return self.f()
        except IOError, e:
            return IOException(e)

class IOJoin(IO, SingleMix()):
    __init__ = SingleMix().__init__
    def do(self):
        return self.x().do()

def funcIO(f):
    def g(*args, **kwargs):
        return IOFunction(functools.partial(f, *args, **kwargs))
    return g

def wrapIO(f):
    def g(*args, **kwargs):
        return IOWrapper(f, *args, **kwargs)
    return g

def joinIO(f):
    def g(*args, **kwargs):
        return IOJoin(functools.partial(f, *args, **kwargs))
    return g

def sequence(xs):
    for x in xs:
        result = x.do()
        if isinstance(result, IOZero):
            break
        yield result
