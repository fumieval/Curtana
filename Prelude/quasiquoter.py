from curtana.lib import parser
from curtana.lib.parser_entities import *

identifier = alpha + -(alnum | parser.Char("_"))

class Var(Parser.Parser):
    def __init__(self, scope):
        self.scope = scope
    def parse(self, text):
        result = identifier.parse(text)
        return result and self.scope[result]