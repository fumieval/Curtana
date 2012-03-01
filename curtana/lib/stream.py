from collections import deque

Empty = type("EmptyType", (), {"__repr__": lambda self: "Empty"})()
EOF = type("EOFType", (), {"__repr__": lambda self: "EOF"})()

from curtana.lib.classes import *

def tail_recursion(f):
    def tail(f):
        a = f
        while callable(a):
            a = a()
        return a
    return lambda self, stream: tail(f(self, stream))

class Iteratee(Applicative, Monad):
    @staticmethod
    def pure(x):
        return Done(x, Empty)
    def enum(self, stream):
        raise NotImplementedError
    def run(self):
        raise NotImplementedError
    
class Cont(Iteratee):
    def __init__(self, k):
        self.k = k
    
    def enum_(self, stream):
        def _():
            try:
                return self.k(next(stream)).enum_(stream)
            except StopIteration:
                return self
        return _
    
    enum = tail_recursion(enum_)
    
    def run(self):
        result = self.k(EOF)
        if isinstance(result, Done):
            return result.run()
    def bind(self, f):
        return Cont(lambda s: self.k(s) & f)
    def bind0(self, s):
        return self.k(s)
    def fmap(self, f):
        return Cont(lambda x: self.k(x).fmap(f))
    def ap(self, it):
        return Cont(lambda x: self.k(x).ap(it))
    def __repr__(self):
        return "Cont({0})".format(self.k)
    
class Done(Iteratee):
    def __init__(self, result, stream):
        self.result = result
        self.stream = stream
    def enum_(self, stream):
        return lambda: self
    enum = tail_recursion(enum_)
    def run(self):
        return self.result
    def bind(self, f):
        return f(self.result).bind0(self.stream)
    def bind0(self, stream):
        return Done(self.result, stream)
    def fmap(self, f):
        return Done(f(self.result), self.stream)
    def ap(self, it):
        return it.fmap(self.result)
    def __repr__(self):
        return "Done({0}, {1})".format(self.result, self.stream)

def head_step(e):
    if e == EOF:
        return Done(None, EOF)
    elif e == Empty:
        return Cont(head_step)
    else:
        return Done(e, Empty)

head = Cont(head_step)

def peek_step(e):
    if e == EOF:
        return Done(None, EOF)
    elif e == Empty:
        return Cont(peek_step)
    else:
        return Done(e, e)

peek = Cont(peek_step)

def drop_step(n):
    def it(e):
        if e == EOF:
            return Done(None, EOF)
        elif e == Empty:
            return Cont(drop_step)
        else:
            return drop(n - 1)
    return it

def drop(n):
    if n == 0:
        return Done(None, Empty)
    else:
        return Cont(drop_step(n))

def filterI(pred):
    def it(i):
        if isinstance(i, Done):
            return Iteratee.pure(i)
        else:
            def step(e):
                if e == EOF:
                    return Done(i.k(EOF), EOF)
                elif pred(e):
                    return filterI(pred)(i.k(e))
            return Cont(step)
    return it

def mapI(f):
    def it(i):
        if isinstance(i, Done):
            return Iteratee.pure(i)
        else:
            def step(e):
                if e == EOF:
                    return Done(i.k(EOF), EOF)
                elif e == Empty:
                    return Cont(step)
                else:
                    return mapI(f)(f(e))
    return it

def iterate(function):
    while True:
        yield function()

class splitBy():
    def __init__(self, predicate, iterable):
        self.predicate = predicate
        self.iterable = iter(iterable)
        self.cont = True
    """split iterables by a element which satisfies the predicate."""
    def __iters(self):
        for i in self.iterable:
            if self.predicate(i):
                return
            yield i
        self.cont = False
    def __iter__(self):
        while self.cont:
            yield self.__iters()

class Branch:
    def __init__(self, stream):
        self.queues = []
        self.stream = iter(stream)
    def next(self):
        data = next(self.stream)
        for queue in self.queues:
            queue.append(data)
        return data
    
class Leaf:
    def __init__(self, stream):
        self.queue = deque()
        self.stream.queues.append(self.queue)
    def __iter__(self):
        while True:
            if len(self.queue) == 0:
                self.stream.next()
            yield self.queue.popleft()

def bufferBy(predicate, iterable):
    """divide iterables to the longest list that satisfies the predicate."""
    buf = []
    for el in iterable:
        buf.append(el)
        if not predicate(buf):
            v = buf.pop()
            yield buf
            buf = [v]
    yield buf
