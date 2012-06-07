import readline
import cPickle as pickle
from curtana.client import syntax

import imp
from curtana import path

def execute(env, user, line, allowdefault=True):
    for component in user.CLIENT_COMPONENTS:
        action = component.parser(syntax.expand(env, user, line))
        if action:
            component.run(env, user, action)
            break
    else:
        if allowdefault:
            execute(env, user, user.DEFAULT_ACTION(line), False)
        else:
            print "Error: Cannot recurse default actions"

def main():
    env = pickle.load(open(path.ENV, "r"))
    user = imp.load_source("settings", path.SETTINGS)

    readline.read_history_file(path.HISTORY)
    
    for component in user.CLIENT_COMPONENTS:
        component.initialize(env, user)
    
    for line in open(path.RC, "r"):
        execute(env, user, line.strip())
            
    while True:
        try:
            line = raw_input(user.PROMPT_FORMAT % env)
            readline.set_startup_hook(None)
            if not line:
                continue

        except EOFError:
            print
            readline.write_history_file(path.HISTORY)
            break
    
        execute(env, user, line)

    for component in user.CLIENT_COMPONENTS:
        component.terminate(env, user)
    
    pickle.dump(env, open(path.ENV, "w"))

if __name__ == "__main__":
    main()
