
"""
Functions and classes for processing streams.
"""

import itertools
import operator
from collections import deque

from Prelude.mixin import Single
from Prelude.classes import *

__all__ = ["map", "filter", "zip", "take", "drop", "takewhile", "dropwhile", "concat", "count", "iterate",
            "splitBy", "bufferBy", "nubBy"]

map = itertools.imap
filter = itertools.ifilter
zip = itertools.izip
def take(n, seq): return itertools.islice(seq, 0, n)
def drop(n, seq): return itertools.islice(seq, n, None)
takewhile = itertools.takewhile
dropwhile = itertools.dropwhile
concat = itertools.chain.from_iterable
count = itertools.count

def iterate(function):
    """call the function repeatedly and yields the results."""
    while True:
        yield function()

class splitBy(Single("predicate")):
    """split iterables by a element which satisfies the predicate."""
    def __init__(self, predicate):
        SingleMix("predicate").__init__(self, predicate)
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

def bufferBy(predicate, stream):
    """divide iterables to the longest list that satisfies the predicate."""
    buf = []
    for el in stream:
        buf.append(el)
        if not self.predicate(buf):
            v = buf.pop()
            yield buf
            buf = [v]
        yield buf

def nubBy(stream, equivalence=operator.eq):
    xs = []
    for i in stream:
        for j in xs:
            if equivalence(i, j):
                break
        else:
            yield i
            xs.append(i)
 
