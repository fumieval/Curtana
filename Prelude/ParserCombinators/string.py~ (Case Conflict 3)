from Prelude.mixin import *
from Prelude.ParserCombinators.Prim import Parser

class Optional(Parser, Single()):
    def parse(self, string):
        string_ = string.tee
        result = self.x.parse(string)
        if result:
            return result
        else:
            return "", string_

class Null(Parser, Void):
    """Matches empty string.
    type: Parser string
    """
    def parse(self, string):
        if string.eos:
            return ("", string)

class Sat(Parser, Single("predicate")):
    """Matches a character satisfying the predicate.
    type: (char -> bool) -> Parser char
    """
    def parse(self, string):
        try:
            char = next(string)
        except StopIteration:
            return None
        return self.predicate(char) and (char, string) or None

class Char(Sat, Single("_y")):
    """Matches specified character.
    type: char -> Parser char
    """
    def __init__(self, char):
        Sat.__init__(self, lambda x: x == char)
        Single("_y").__init__(self, char)
    __repr__ = Single("_y").__repr__

class NotChar(Sat, Single("_y")):
    """Matches a character expecting specified character.
    type: char -> Parser char
    """
    def __init__(self, char):
        Sat.__init__(self, lambda x: x != char)
        Single("_y").__init__(self, char)
    __repr__ = Single("_x").__repr__

class AnyChar(Sat, Void):
    """Matches any character.
    type: Parser char
    """
    def __init__(self): Sat.__init__(self, lambda x: True)
    __repr__ = Void.__repr__

class String(Parser, Single("_x")):
    """Matches specified string.
    type: string -> Parser string
    """
    def parse(self, string):
        s = ""
        for char in self._x:
            try:
                c = next(string)
            except StopIteration:
                return None
            if char != c:
                return None
            s += c
        return s, string

class Until(Parser, Single("_x")):
    """Delimits by the parser.
    type: parser -> Parser string
    """
    def parse(self, string):
        s = ""
        while True:
            r = self._x.parse(string.tee)
            if r:
                return s, string
            try:
                s += next(string)
            except StopIteration:
                break
        return s, string

class Delimit(Parser, Single("_x")):
    """Delimits by the parser.
    type: parser -> Parser string
    """
    def parse(self, string):
        s = ""
        while True:
            r = self._x.parse(string.tee)
            if r:
                return s, r[1]
            try:
                s += next(string)
            except StopIteration:
                break
        return s, string

class Find(Parser, Single("_x")):
    def parse(self, string):
        while True:
            r = self._x.parse(string.tee)
            if r:
                return r
            try:
                next(string)
            except StopIteration:
                break

class Regex(Parser, Single("_x")):
    def __init__(self, x):
        import re
        Single("_x").__init__(self, x)
        self.re = re.compile(x)
    def parse(self, string):
        result = self.re.search(string.remaining)
        return result and (result.group(), string.remaining[result.end():])

