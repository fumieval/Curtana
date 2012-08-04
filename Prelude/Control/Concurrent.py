
class Branch:
    """
    Flexible stream forker.
    """
    def __init__(self, stream):
        self.queues = []
        self.stream = iter(stream)
    def next(self):
        data = next(self.stream)
        for queue in self.queues:
            queue.append(data)
        return data
    
class Leaf:
    def __init__(self, branch):
        self.branch = branch
        self.queue = deque()
        self.branch.queues.append(self.queue)
    def __iter__(self):
        while True:
            if len(self.queue) == 0:
                self.branch.next()
            yield self.queue.popleft()
 
