import functools
import itertools

map = itertools.imap
filter = itertools.ifilter

par = functools.partial
compose = lambda f: lambda g: lambda *args: f(g(args))

flip = lambda f: lambda x: lambda y: f(y, x)