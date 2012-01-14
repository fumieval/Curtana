
import readline
from curtana.client import syntax
from curtana.client.component import call, Component

class Standard(Component):
    def __init__(self, extensions=[]):
        from curtana.lib.parser_aliases import A, C, D
        delimited = D(C(":"))
        self.parser = (
              C("%") >> call(self.set_env) * delimited * A
            | C(">") >> call(self.prompt) * delimited * A
            | C(",") >> call(self.expand_text) * A
            | C(".") >> call(self.echo_text) * A
            | C("'") >> call(self.command) * A
            )
        Component.__init__(self, extensions)
    
    def command(self, env, user, text):
        for component in user.CLIENT_COMPONENTS:
            action = component.parser(syntax.expand(env, user, text))
            if action:
                component.run(env, user, action)
    
    def command_fromfile(self, env, user, path):
        for line in open(path, "r"):
            self.command(env, user, line.strip())
    

    def expand_text(self, env, user, text):
        readline.set_startup_hook(lambda: readline.insert_text(text))
        
    def set_env(self, env, user, name, value):
        env[name] = value
    
    def prompt(self, env, user, name, msg):
        env[name] = raw_input(msg)
    
    def echo_text(self, env, user, text):
        print text