from Prelude.ParserCombinators.Entities import *
from Prelude.ParserCombinators.String import *
from Prelude import cons, curry

#http://www.python.jp/doc/release/reference/expressions.html
expression_list = lambda x: curry(cons) ** x * -(Char(",") >> x) << Optional(Char(","))

identifier = (alpha | Char("_")) + "".join ** -(alnum | Char("_"))

parens = lambda x: Char("(") >> x << Char(")")
brackets = lambda x: Char("[") >> x << Char("]")

escapeseq       =  Char("\\") >> ascii
stringprefix    =  reduce(Parser.__or__, map(Char, ["r", "u", "ur", "R", "U", "UR", "Ur", "uR", "b", "B", "br", "Br", "bR", "BR"]))

shortstringchar =  lambda quote: Sat(lambda c: c != "\\" and c != "\n" and c != quote)
shortstringitem =  lambda quote: shortstringchar(quote) | escapeseq
shortstring     =  Char("'") + "".join ** -shortstringitem("'") + Char("'") | Char('"') + "".join ** -shortstringitem('"') + Char('"')
stringliteral   =  eval ^ Optional(stringprefix) + shortstring

"""
longstring      =  String("'''") >> -longstringitem << String("'''") | String('\"\""') >> -longstringitem << String('\""\"')
longstringchar  =  Sat("\\".__ne__)
longstringitem  =  longstringchar | escapeseq
"""

nonzerodigit   =  Sat(lambda c: "0" < c <= "9")
octdigit       =  Sat(lambda c: "0" <= c <= "7")
bindigit       =  Char("0") | Char("1")
hexdigit       =  digit | Sat(lambda c: "a" <= c <= "f" or "A" <= c <= "F")
octinteger     =  Char("0") + (Char("o") | Char("O")) + "".join ** +octdigit | Char("0") + "".join ** +octdigit
hexinteger     =  Char("0") + (Char("x") | Char("X")) + "".join ** +hexdigit
bininteger     =  Char("0") + (Char("b") | Char("B")) + "".join ** +bindigit
decimalinteger =  nonzerodigit + "".join ** -digit | Char("0")
integer        =  eval ^ (octinteger | hexinteger | bininteger | decimalinteger) + Optional(Char("l") | Char("L"))

intpart       =  +digit
fraction      =  Char(".") + "".join ** +digit
pointfloat    =  Optional(intpart) + fraction | intpart << Char(".")
exponent      =  (Char("e") | Char("E")) + (Char("+") | Char("-")) + "".join ** +digit
exponentfloat =  (intpart | pointfloat) + exponent
floatnumber   =  eval ^ (pointfloat | exponentfloat)

literal = stringliteral | integer | floatnumber
