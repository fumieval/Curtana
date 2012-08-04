from Prelude.ParserCombinators import *
from Prelude.ParserCombinators.String import *

spaces = Sat(lambda x: x.isspace())
digit = Sat(lambda x: x.isdigit())
alpha = Sat(lambda x: x.isalpha())
alnum = Sat(lambda x: x.isalnum())
ascii = Sat(lambda x: " " <= x <= "~")

integer = int ^ Optional(Char("+") | Char("-")) + "".join ** +digit
floating = float ^ "".join ** +digit + Char(".") + "".join ** +digit