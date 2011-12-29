
import urllib
import urllib2
from curtana.lib import oauth

import json

import threading
import xmlrpclib
import SimpleXMLRPCServer
import Queue

import string
from itertools import imap, count, izip, repeat

from curtana.common.twitter import get_and_register, CONSUMER_KEY, CONSUMER_SECRET

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9450

STREAM_URL = "https://userstream.twitter.com/2/user.json"
DEFAULT_INDEX_CHARS = string.digits + string.lowercase

def streamopen(name):
    param = {}
    token = oauth.OAuthToken(*get_and_register(name))
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    headers = {}
    request = oauth.OAuthRequest.from_consumer_and_token(
        oauth_consumer=consumer, http_url=STREAM_URL, http_method="POST",
        token=token, parameters=param)
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    headers.update(request.to_header())
    req = urllib2.Request(STREAM_URL, headers=headers)
    return urllib2.urlopen(req, urllib.urlencode(param))

def iterstream(stream):
    while True:
        line = ""
        try:
            for c in imap(stream.read, repeat(1)):
                if c == "\n":
                    break
                line += c
        except IOError:
            break
        line = line.strip()
        if line:
            yield line

def makeindex(n, length=1, chars=string.digits + string.lowercase):
    if length == 0:
        return ""
    else:
        q, r = divmod(n, len(chars))
        return chars[r] + makeindex(q, length - 1, chars)

class StreamBranch(threading.Thread):
    
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.daemon = True
        
        self.url = url
        self.queues = {}
        self.stream = izip(imap(makeindex, count()),
                           iterstream(url))
    
    def close(self, index=None):
        if index is None:
            pending = self.queues.keys()
            for i in pending:
                self.queues[i].put(None)
            self.url.close()
        else:
            self.queues[index].put(None)

    def entry(self):
        return StreamLeaf(self.queues)
    
    def run(self):
        for data in self.stream:
            pending = self.queues.keys()
            for i in pending:
                self.queues[i].put(data)
                
        pending = self.queues.keys()
        for i in pending:
            self.queues[i].put(None)

class StreamLeaf():
    def __init__(self, queues):
        self.queues = queues
        for i in count():
            if i not in self.queues:
                self.queues[i] = Queue.Queue()
                self.index = i
                return
    
    def end(self):
        del self.queues[self.index]
    
    def __iter__(self):
        while True:
            data = self.queues[self.index].get()
            if data is None:
                break
            yield data

class StreamServer():
    def __init__(self):
        self.stream = {}
    
    def confirm(self, name):
        return name in self.stream
    
    def register(self, name):
        self.stream[name] = StreamBranch(streamopen(name))
        self.stream[name].start()
        
    def unregister(self, name):
        
        self.stream[name].close()
        del self.stream[name]

    def join(self, name):
        return self.stream[name].entry().index

    def release(self, name, index):
        return self.stream[name].close(index)

    def get(self, name, index):
        data = self.stream[name].queues[index].get()
        if data:
            return data[0], data[1]

def serve(host=DEFAULT_HOST, port=DEFAULT_PORT):
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)
    server.register_instance(StreamServer())
    server.serve_forever()
    
class Client():
    def __init__(self, name, host=DEFAULT_HOST, port=DEFAULT_PORT, join=True):
        self.host = host
        self.port = port
        self.name = name
        self._conn = xmlrpclib.ServerProxy("http://%s:%s/"% (host, port))
        if join:
            if not self._conn.confirm(name):
                self._conn.register(name)
            self.index = self._conn.join(name)

    def close(self):
        conn = xmlrpclib.ServerProxy("http://%s:%s/"% (self.host, self.port))
        conn.release(self.name, self.index)
    
    def __iter__(self):
        while True:
            data = self._conn.get(self.name, self.index)
            if data is None:
                break
            i, d = data
            yield i, json.loads(d)