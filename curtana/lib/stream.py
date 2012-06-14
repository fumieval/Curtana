import itertools
from collections import deque
from curtana.lib.mixin import SingleMix, InfixMix
from curtana.lib.classes import *

class Processor:
    def __rshift__(self, other):
        return ProcessorComposite(self, other)

class ProcessorComposite(Processor, InfixMix("left", "right")):
    op = ">>"
    __init__ = InfixMix.__init__
    def __call__(self, stream):
        return self.right(self.left(stream))

class Map(Processor, SingleMix("function")):
    __init__ = SingleMix.__init__
    def __call__(self, stream):
        return itertools.imap(self.function, stream)

class Filter(Processor, SingleMix("predicate")):
    __init__ = SingleMix.__init__
    def __call__(self, stream):
        return itertools.ifilter(self.predicate, stream)

class SplitBy(Processor, SingleMix("predicate")):
    """split iterables by a element which satisfies the predicate."""
    def __init__(self, predicate):
        SingleMix.__init__(self, predicate)
        self.cont = True
    def __iters(self, iterable):
        for i in iterable:
            if self.predicate(i):
                return
            yield i
        self.cont = False
    def __call__(self, stream):
        while self.cont:
            yield self.__iters(stream)

class BufferBy(Processor, SingleMix("predicate")):
    """divide iterables to the longest list that satisfies the predicate."""
    __init__ = SingleMix.__init__
    def __call__(self, stream):
        buf = []
        for el in stream:
            buf.append(el)
            if not self.predicate(buf):
                v = buf.pop()
                yield buf
                buf = [v]
        yield buf

def iterate(function):
    while True:
        yield function()

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
