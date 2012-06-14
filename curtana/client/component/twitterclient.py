
import threading

import sys

from curtana.client import component
from curtana.common import streaming

import curtana.common.twitterlib as T
import twython

class TwitterClient(component.Component):
    def __init__(self, extensions):
        from curtana.lib.parser_aliases import A, C, S, AC, D, Z
        
        self.tweet_parser = A
        self.parser = (
            C("/") >> (
                  S("login ") >> component.call(self.twitter_auth) * A
                | S("connect ") >> component.call(self.listen_timeline) * A
                | S("disconnect ") >> component.call(self.terminate)
                | S("reply ") >> component.call(self.post_reply) * D(C(":")) * Z(lambda: self.tweet_parser)
                )
            | C("\\") >> component.call(self.post_tweet) * Z(lambda: self.tweet_parser)
            | C(":") >> component.call(self.respond) * AC * A)
        
        self.respond_parser = \
            (C("@") >> component.call(self.reply) * Z(lambda: self.tweet_parser)
             | C("`") >> component.call(self.unofficialRT) * Z(lambda: self.tweet_parser)
             | C("r") >> component.call(self.retweet)
             | C("f") >> component.call(self.favorite)
             | component.call(self.reply) * Z(lambda: self.tweet_parser))
    
        component.Component.__init__(self, extensions, multithread=True)

    def add_respond_syntax(self, parser):
        self.respond_parser = parser | self.respond_parser
    
    def initialize(self, env, user):
        env["NAME"] = ""
        self.api = None
        self.map = {}
        self.listener = None
        component.Component.initialize(self, env, user)
    
    def terminate(self, env, user):
        print "Terminating."
        if self.listener:
            self.listener.disconnect()
        component.Component.terminate(self, env, user)
        
    def set_header(self, env, user, text):
        env["HEADER"] = text
    
    def set_footer(self, env, user, text):
        env["FOOTER"] = text

    def post_tweet(self, env, user, text):
        try:
            self.api.updateStatus(status=env["HEADER"] + text() + env["FOOTER"])
        except twython.twython.TwythonError:
            print >> sys.stderr, sys.exc_info()[1]

    def post_reply(self, env, user, in_reply_to_status_id, text):
        try:
            self.api.updateStatus(status=env["HEADER"] + text() + env["FOOTER"],
                                  in_reply_to_status_id=in_reply_to_status_id)
        except twython.twython.TwythonError:
            print >> sys.stderr, sys.exc_info()[1]


    def twitter_auth(self, env, user, name):
        env["NAME"] = name
        self.api = T.ApiMod.from_name(name)

    def respond(self, env, user, target, text):
        action = self.respond_parser(text().decode("utf-8"))
        if action:
            if target in self.map:
                action[0](env, user, self.map[target], *action[1:])
            else:
                print >> sys.stderr, "No such target %s" % target
    
    def reply(self, env, user, target, text):
        self.api.updateStatus(status="@%s %s" % (target[1], text), in_reply_to_status_id=target[0])
    
    def unofficialRT(self, env, user, target, text):
        self.api.updateStatus(status="%s RT @%s: %s" % (text, target[1], target[2]))
    
    def favorite(self, env, user, target):
        self.api.CreateFavorite(id=target[0])
    
    def retweet(self, env, user, target):
        self.api.reTweet(id=target[0])
        
    def listen_timeline(self, env, user, text):
        self.listener = TimelineListener(self, env, text)
        self.listener.start()

class TimelineListener(threading.Thread):
    def __init__(self, component, env, identifier):
        threading.Thread.__init__(self)
        self.daemon = True
        self.env = env
        self.map = component.map
        self.identifier = identifier
        self.server = streaming.Client(identifier)

    def run(self):
        for i, data in self.server:
            if data is None:
                print "Stream Stopped."
                print >> sys.stdin
                break
            if "user" in data and "id" in data:
                self.map[i] = (data["id"], data["user"]["screen_name"], data["text"], data["in_reply_to_status_id"])

    def disconnect(self):
        self.server.close()
