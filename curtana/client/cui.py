import readline
import cPickle as pickle

import imp
from curtana import path

def execute(env, user, line, allowdefault=True):
    for component in user.CLIENT_COMPONENTS:
        action = component.parser.parse(line)
        if action:
            component.run(env, user, action[0])
            break
    else:
        if allowdefault:
            execute(env, user, user.DEFAULT_ACTION(line), False)
        else:
            print "Error: There is an infinite recursion in default action"

def main():
    env = pickle.load(open(path.ENV, "r"))
    user = imp.load_source("settings", path.SETTINGS)

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
            break
    
        execute(env, user, line)

    for component in user.CLIENT_COMPONENTS:
        component.terminate(env, user)
    
    pickle.dump(env, open(path.ENV, "w"))

if __name__ == "__main__":
    main()