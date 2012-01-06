from curtana.lib import parser

spaces = -parser.Sat(lambda x: x.isspace())
digit = parser.Sat(lambda x: x.isdigit())
alpha = parser.Sat(lambda x: x.isalpha())
alnum = parser.Sat(lambda x: x.isalnum())

integer = int ^ (parser.Char("+") | parser.Char("-")).opt + "".join ** +digit
floating = float ^ "".join ** +digit + parser.Char(".") + "".join ** +digit