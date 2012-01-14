from urllib2 import *

import urllib2

class OpenerDirector(urllib2.OpenerDirector):
    def __init__(self):
        urllib2.OpenerDirector.__init__(self)
        self.add_handler(urllib2.ProxyHandler())