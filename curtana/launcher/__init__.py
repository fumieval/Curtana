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
    
    def __init__(self):
        self.trigger = {}
        self.state = {}
        self.queue = []
    
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

        