
import string
import json

import urllib
import urllib2
import threading
import xmlrpclib
import SimpleXMLRPCServer
import Queue

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9450
DEFAULT_INDEX_CHARS = string.digits + string.lowercase

def genindex(length=1, chars=DEFAULT_INDEX_CHARS):
    """
    generate unique indices.
    """
    state = [0] * length
    N = len(chars)
    while True:
        state[0] += 1
        for i in xrange(N - 1):
            if state[i] == N:
                state[i + 1] += 1
        yield "".join(map(state.__getitem__, state))

class StreamBranch(threading.Thread):
    
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.daemon = True
        
        self.url = url
        self.queues = {}
        self.stream = izip(genindex(), iterstream(url))
    
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
                del self.queues[self.index]
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
        return self.stream[name].queues[index].get()

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