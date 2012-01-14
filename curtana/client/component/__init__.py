import cPickle as pickle
from curtana.lib.container import TupleA
from curtana.lib.parser import Return, Failure
import threading

def call(f):
    return TupleA() ** Return(f)

class Component():
    parser = Failure()
    def __init__(self, extensions, multithread=False):
        self.extensions = extensions
        self.multithread=multithread
    def initialize(self, env, user):
        for ext in self.extensions:
            ext.initialize(self, env, user)
    def terminate(self, env, user):
        for ext in self.extensions:
            ext.terminate(self, env, user)
    def run(self, env, user, action):
        if self.multithread:
            ThreadingRun(env, user, action).start()
        else:
            action[0](env, user, *action[1:])
    def add_syntax(self, parser):
        self.parser = parser | self.parser

class ThreadingRun(threading.Thread):
    def __init__(self, env, user, action):
        threading.Thread.__init__(self)
        self.env = env
        self.user = user
        self.action = action
        self.daemon = True

    def run(self):
        self.action[0](self.env, self.user, *self.action[1:])