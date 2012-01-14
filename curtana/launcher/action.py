
class Action():
    def __init__(self, f):
        self.f = f
    def __call__(self):
        return Action(self.f)
    def do(self):
        return self.f()
    def __and__(self, k):
        return Bind(self, k)
    
    def __rshift__(self, k):
        return self & (lambda _: k)

class Bind(Action):
    def __init__(self, x, k):
        self.x = x
        self.k = k
    def do(self):
        return self.k(self.x.do()).do()
    def __repr__(self):
        return "(%r & %r)" % (self.x, self.k)

class Return(Action):

    def __init__(self, x):
        self.x = x
        Action.__init__(self, lambda: x)
    def __repr__(self):
        return "Return(%r)" % self.x