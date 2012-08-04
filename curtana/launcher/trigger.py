"""
Trigger definitions
"""
import random
import datetime
from Prelude import mixin

DT = datetime.timedelta

def dailysection(hour=0, minute=0, second=0, microsecond=0):
    """section with daily cycle."""
    return datetime.datetime(datetime.MINYEAR,
                             month=1, day=1,
                             hour=hour, minute=minute, second=second,
                             microsecond=microsecond)

def yearlysection(month=1, day=1, hour=0, minute=0, second=0):
    """section with yearly cycle."""
    return datetime.datetime(datetime.MINYEAR,
                             month=month, day=day,
                             hour=hour, minute=minute, second=second)
    
class Trigger():
    """Trigger class."""
    def __call__(self, env): raise NotImplementedError
    def __and__(self, other): return TriggerAnd(self, other)
    def __xor__(self, other): return TriggerXor(self, other)
    def __or__(self, other): return TriggerOr(self, other)
    def __invert__(self): return TriggerInvert(self)
    def __cmp__(self, other): return cmp(repr(self), repr(other)) 
    def __hash__(self): return repr(self).__hash__()

class TriggerAnd(Trigger, mixin.Infix()):
    """Intersection between triggers."""
    op = "&"
    def __call__(self, env):
        return self.left(env) and self.right(env)

class TriggerXor(Trigger, mixin.Infix()):
    """Exclusive intersection between triggers."""
    op = "^"
    def __call__(self, env):
        return self.left(env) ^ self.right(env)

class TriggerOr(Trigger, mixin.Infix()):
    """Disjunction between triggers."""
    op = "|"
    def __call__(self, env):
        return self.left(env) or self.right(env)

class TriggerInvert(Trigger, mixin.Unary()):
    """Negation of the trigger."""
    op = "~"
    def __call__(self, env):
        return not self.term(env)

class FunctionTrigger(Trigger, mixin.Single("function")):
    """Use a function as a trigger."""
    def __call__(self, env):
        return self.function(env)
    
class Time(Trigger, mixin.Single("time")):
    """Time trigger."""
    def __call__(self, env):
        return datetime.datetime.today() >= self.time

class Delay(Time):
    """Delay trigger."""
    def __init__(self, offset=datetime.timedelta()):
        Trigger.__init__(self)
        self.time = datetime.datetime.today() + offset

class Regular(Trigger, mixin.Multi("span", "offset")):
    """Trigger affects at regular intervals."""
    def __call__(self, env):
        target = datetime.datetime.today() - self.offset
        return ((target.hour * 60 + target.minute) * 60 +
                target.second) % self.span == 0

class Hourly(Trigger, mixin.Single("offset")):
    """Trigger affects hourly."""
    def __call__(self, env):
        return (datetime.datetime.today() - self.offset).minute == 0

class Daily(Trigger, mixin.Single("offset")):
    """Trigger affects daily."""
    def __call__(self, env):
        return (datetime.datetime.today() - self.offset).hour == 0

class Weekly(Trigger, mixin.Single("offset")):
    """Trigger affects weekly."""
    def __call__(self, env):
        return (datetime.datetime.today() - self.offset).weekday() == 0

class Monthly(Trigger, mixin.Multi("day", "offset")):
    """Trigger affects monthly."""
    def __call__(self, env):
        return (datetime.datetime.today() - self.offset).day == self.day

class Yearly(Trigger, mixin.Multi("month", "offset")):
    """Trigger affects yearly."""
    def __call__(self, env):
        return (datetime.datetime.today() - self.offset).month == self.month

class InDailyPeriod(Trigger):
    """Trigger affects between specified section."""
    def __init__(self, begin, end):
        Trigger.__init__(self)
        self.begin = begin.replace(year=datetime.MINYEAR, month=1, day=1)
        self.end = end.replace(year=datetime.MINYEAR, month=1, day=1)
    def __call__(self, env):
        now = datetime.datetime.today().replace(year=datetime.MINYEAR,
                                                month=1, day=1)
        return (self.begin == None or self.begin <= now) and \
               (self.end == None or self.end >= now)
    def __repr__(self):
        return "InDailySection(%r, %r)" % (self.begin, self.end)

class InYearlyPeriod(Trigger):
    """Trigger affects between specified section."""
    def __init__(self, begin, end):
        Trigger.__init__(self)
        self.begin = begin.replace(year=datetime.MINYEAR)
        self.end = end.replace(year=datetime.MINYEAR)
    def __call__(self, env):
        now = datetime.datetime.today().replace(year=datetime.MINYEAR)
        return (self.begin == None or self.begin <= now) and \
               (self.end == None or self.end >= now)
    def __repr__(self):
        return "InDailySection(%r, %r)" % (self.begin, self.end)

class Randomly(Trigger, mixin.Single("probability")):
    """Trigger affects randomly."""
    def __call__(self, env):
        return random.random() < self.probability
