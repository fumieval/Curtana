import urllib2
from urllib2 import *

class OpenerDirector(urllib2.OpenerDirector):
    def __init__(self):
        urllib2.OpenerDirector.__init__(self)
        self.add_handler(urllib2.ProxyHandler())