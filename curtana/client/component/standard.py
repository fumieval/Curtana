import curtana.lib.parser as P
import readline
from curtana.client import syntax

from curtana.client.component import Component

def call(f):
    return P.TupleA() ** P.Return(f)

class Standard(Component):
    def __init__(self):
        self.parser = (
              P.Char("%") >> call(self.set_env) * P.join ** -P.NotChar(":") * P.Any()
            | P.Char(">") >> call(self.prompt) * P.join ** -P.NotChar(":") * P.Any()
            | P.Char(",") >> call(self.expand_text) * P.Any()
            | P.Char("?") >> call(self.show_help)
            | P.Char(".") >> call(self.echo_text) * P.Any()
            | P.Char("'") >> call(self.command_quote) * P.Any()
            )
    
    def command(self, env, user, text):
        for component in user.CLIENT_COMPONENTS:
            action = component.parser(text)
            if action:
                component.run(env, user, action[0])
    
    def command_fromfile(self, env, user, path):
        for line in open(path, "r"):
            self.command(env, user, line.strip())
    
    def command_quote(self, env, user, text):
        self.command(env, user, syntax.expand(env, user, text))

    def expand_text(self, env, user, text):
        readline.set_startup_hook(lambda: readline.insert_text(syntax.expand(env, user, text)))
        
    def set_env(self, env, user, name, value):
        env[name] = value
    
    def show_help(self):
        pass
    
    def prompt(self, env, user, name, msg):
        env[name] = raw_input(syntax.expand(env, user, msg))
    
    def echo_text(self, env, user, text):
        print syntax.expand(env, user, text)