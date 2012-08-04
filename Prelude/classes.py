
class Functor:
    def fmap(self, f):
        raise NotImplementedError
    def __rxor__(self, f):
        return self.fmap(f)
    def __rpow__(self, f):
        return self.fmap(f)

class Applicative(Functor):
    @staticmethod
    def pure(x):
        raise NotImplementedError
    def ap(self, a):
        raise NotImplementedError
    def __mul__(self, other):
        return self.ap(other)

class Alternative(Applicative):
    @staticmethod
    def empty():
        raise NotImplementedError
    def alt(self, a):
        raise NotImplementedError
    def opt(self):
        return self | Alternative.pure(None)
    def __or__(self, other):
        return self.alt(other)
    def some(self):
        return (lambda x, xs: [x] + xs) ** self * self.many()
    def many(self):
        return self.some() | Alternative.pure([])

class Monad:
    def bind(self, k):
        raise NotImplementedError
    def __and__(self, k):
        return self.bind(k)
    def __rshift__(self, other):
        return self.bind(lambda _: other)
