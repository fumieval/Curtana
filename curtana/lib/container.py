class TupleA(tuple):
    def __call__(self, x):
        return TupleA(self + (x,))

class StringA():
    def __init__(self, string=""):
        self.string = string
    def __call__(self, other):
        return StringA(self.string + other)
    def __radd__(self, other):
        if isinstance(other, StringA):
            return other.string + self.string
        else:
            return other + self.string
    def __hash__(self):
        return hash(self.string)
    def __cmp__(self, other):
        if isinstance(other, StringA):
            return self.x.__cmp__(other.string)
        else:
            return self.x.__cmp__(other)
    def __len__(self):
        return len(self.string)
    def __str__(self):
        return str(self.string)
    def __unicode__(self):
        return unicode(self.string)
    def __repr__(self):
        return repr(self.string)