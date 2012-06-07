from collections import deque

from curtana.lib.classes import *

def tail_recursion(f):
    def tail(f):
        a = f
        while callable(a):
            a = a()
        return a
    return lambda self, stream: tail(f(self, stream))

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
