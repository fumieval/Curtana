import cPickle as pickle
from curtana.lib.container import TupleA
from curtana.lib.parser import Return, Failure

def call(f):
    return TupleA() ** Return(f)

class Component():
    parser = Failure()
    def initialize(self, env, user):
        pass
    def terminate(self, env, user):
        pass
    def run(self, env, user, action):
        action[0](env, user, *action[1:])