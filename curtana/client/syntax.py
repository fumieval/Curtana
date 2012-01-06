import curtana.lib.parser as P

class Expr:
    def __init__(self, code):
        self.code = code
    def __repr__(self):
        return "Expr(%r)" % self.code
    def __call__(self, env, user):
        return eval(self.code, dict(env.items() + user.items()))

text_parser = -(P.join ** +P.NotChar("`") |
    P.Char("`") >> Expr ** P.join **
        +(P.Char("\\") >> P.Char("`") | P.NotChar('`')) << P.Char("`"))

def expand(env, user, text):
    result = []
    for token in text_parser(text)[0]:
        if isinstance(token, Expr):
            result.append(str(token(env, user.additions)))
        else:
            result.append(token)
    return "".join(result)