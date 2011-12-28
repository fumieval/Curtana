import cPickle as pickle
from curtana.lib.parser import Failure

class Component():
    parser = Failure()
    def initialize(self, env, user):
        pass
    def terminate(self, env, user):
        pass
    def run(self, env, user, action):
        action[0](env, user, *action[1:])