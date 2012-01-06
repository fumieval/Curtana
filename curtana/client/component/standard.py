
import readline
from curtana.client import syntax

from curtana.client.component import call, Component

class Standard(Component):
    def __init__(self):
        from curtana.lib.parser_aliases import A, C, D
        delimited = D(C(":"))
        self.parser = (
              C("%") >> call(self.set_env) * delimited * A
            | C(">") >> call(self.prompt) * delimited * A
            | C(",") >> call(self.expand_text) * A
            | C("!help") >> call(self.show_help)
            | C(".") >> call(self.echo_text) * A
            | C("'") >> call(self.command_quote) * A
            )
    
    def command(self, env, user, text):
        for component in user.CLIENT_COMPONENTS:
            action = component.parser(text)
            if action:
                component.run(env, user, action)
    
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