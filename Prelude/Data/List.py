undefined = type("UndefinedType", (), {"__repr__": lambda self: "undefined"})
def uncons(iterable):
    def it():
        it_ = iter(iterable)
        yield None
        head_ = next(it_)
        yield lambda: head_
        yield it_
    head = []
    tail = []
    i = it()
    def get_head(head):
        if not head:
            next(i)
            head = [next(i)]
        return head[0]
    def get_tail(head, tail):
        get_head(head)
        if not tail:
            tail = [next(i)]
        return tail[0]
    
    return (lambda: get_head(head)), (lambda: get_tail(head, tail))

class Cons:
    def __init__(self, head, tail):
        self.__head = head
        self.tail = tail
        self.active = False
        self.value = None
    
    @property
    def head(self):
        if self.active:
            return self.value
        else:
            self.value = self.__head()
            return self.value

    @staticmethod
    def from_iterable(iterable):
        car, cdr = uncons(iterable)
        return Cons(car, lambda: Cons.from_iterable(cdr()))