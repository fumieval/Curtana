import curtana.lib.parser as P

class Expr:
    def __init__(self, code):
        self.code = code
    def __repr__(self):
        return "Expr(%r)" % self.code
    def __call__(self, env, user):
        return eval(self.code, dict(env.items() + user.items()))

text_parser = ~("".join ** +P.NotChar("`") |
    P.Char("`") >> Expr ** "".join **
        +(P.Char("\\") >> P.Char("`") | P.NotChar('`')) << P.Char("`"))

def expand(env, user, text):
    return "".join((str(i(env, user.additions)) if isinstance(i, Expr) else i) for i in text_parser.parse(text)[0])
    