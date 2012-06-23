import curtana.lib.parser as P
from itertools import chain

class Expr:
    def __init__(self, code):
        self.code = code
    def __repr__(self):
        return "Expr(%r)" % self.code
    def __call__(self, env, user):
        return eval(self.code, dict(chain(env.iteritems(), user.iteritems())))

text_parser = -("".join ** +(P.Char("\\") >> P.Char("`") | P.NotChar("`"))
            | P.Char("`") >> Expr ** "".join ** +(P.Char("\\") >> P.Char("`") | P.NotChar("`")) << P.Char("`")
            )

def expand(env, user, text):
    result = []
    for token in text_parser(text):
        if isinstance(token, Expr):
            result.append(str(token(env, user.additions)))
        else:
            result.append(token)
    return "".join(result)

class Token:
    pass
