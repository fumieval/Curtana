class NTuple(tuple):
    def __call__(self, x):
        return NTuple(self + (x,))

emptyTuple = NTuple()
 
