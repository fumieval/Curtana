from curtana.lib import parser

__all__ = ["A", "AC", "F", "N", "Z", "R", "P", "C", "NC", "D", "U", "S", "T", "RE"]

#instances
A = parser.Any()
AC = parser.AnyChar()
F = parser.Failure()
N = parser.Null()

#classes
Z = parser.Delay
R = parser.Return
P = parser.Sat
C = parser.Char
NC = parser.NotChar
D = parser.Delimit
U = parser.Until
T = parser.Find
S = parser.String

RE = parser.Regex