from collections import deque

def iterate(function):
    while True:
        yield function()

def splitBy(predicate, stream):
    def iters(eos):
        for i in stream:
            if predicate(i):
                break
            yield i
        eos[0] = True
    eos = [False]
    while not eos[0]:
        yield iters(eos)
            
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

def bufferBy(predicate, stream):
    """
    split stream 
    """
    buf = []
    for el in stream:
        buf.append(el)
        if not predicate(buf):
            v = buf.pop()
            yield buf
            buf = [v]
    yield buf