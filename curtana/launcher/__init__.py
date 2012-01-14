from curtana.launcher.trigger import Trigger
from curtana.launcher.action import Action

import datetime
import time
import cPickle as pickle
import sys
from itertools import ifilter

RUN_INTERVAL = 0.2

def nowf():
    """formated current time."""
    return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def newstate(env, trigger, state, action):
    """do action and return state."""
    if trigger(env):
        if state:
            return True
        else:
            result = action(env)
            print "%s\t%r -> [%r] => %r" % (nowf(), trigger, action, result)
            return bool(result)
    else:
        return False

class Daemon():
    
    """
    Daemon class.
    Do actions if trigger is effected.
    """
    
    def __init__(self, env={}):
        self.env = env
        self.env["daemon"] = self
        self.env["flag"] = {}
        self.trigger = {}
        self.state = {}
        self.queue = []
        self.hooks = []
        self.debug = False

    def push(self, trigger, action):
        """Put trigger and action"""
        self.queue.append((trigger, action))

    def __len__(self):
        return len(self.trigger)

    def reset(self):
        """reset trigger state."""
        for key in self.trigger:
            self.state[key] = False

    def dump(self, filename):
        """dump trigger state."""
        pickle.dump(self.state, filename)

    def load(self, filename):
        """load trigger state."""
        for key, value in ifilter(lambda x: x[0] in self.trigger,
                                  pickle.load(filename).iteritems()):
            self.state[key] = value

    def setflag(self, name, value):
        self.env["flag"][name] = value
    
    def getflag(self, name):
        return self.env["flag"][name]
    
    def run(self):
        """run daemon."""
        if self.debug:
            print("%s\tDaemon Start." % nowf())
        
        for hook in self.hooks:
            hook(self.env)
        
        while True:
            for key in self.trigger:
                self.state[key] = newstate(self.env, key,
                                           self.state[key],
                                           self.trigger[key])
            self.queue = [(t, a) for t, a in self.queue \
                          if not (t(self.env) and a(self.env))]
            sys.stdout.flush()
            time.sleep(RUN_INTERVAL)

class Flag(Trigger):
    """This trigger gets flag."""
    def __init__(self, name):
        Trigger.__init__(self)
        self.name = name
    def __call__(self, env):
        return env.flag[self.name]
    def __repr__(self):
        return "Flag(%r)" % self.name
        
class SetFlag(Action):
    """This action sets the flag to specified value."""
    def __init__(self, env, name, value):
        def f():
            env.flag[name] = value
        Action.__init__(self, f)