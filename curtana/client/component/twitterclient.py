
import threading

import sys

import twitter

import curtana.lib.urllib
from curtana.client import component, syntax
from curtana import userstream

import curtana.common.twitter as T

class TwitterClient(component.Component):
    def __init__(self):
        from curtana.lib.parser_aliases import A, C, S, AC
        self.parser = (
            C("/") >> (
                  S("login ") >> component.call(self.twitter_auth) * A
                | S("connect ") >> component.call(self.listen_timeline) * A
                | S("disconnect ") >> component.call(self.terminate)
                | component.call(self.message("No such command"))
                )
            | C("\\") >> component.call(self.post_tweet) * A
            | C(":") >> component.call(self.respond) * AC * A)
        
        self.respond_parser = \
            (C("@") >> component.call(self.reply) * A
             | C("`") >> component.call(self.unofficialRT) * A
             | C("r") >> component.call(self.retweet)
             | C("f") >> component.call(self.favorite)
             | component.call(self.reply) * A)
    
    def message(self, text):
        def _(env, user):
            print "component.twitterclient:", text
        return _
    
    def initialize(self, env, user):
        env["NAME"] = ""
        self.api = None
        self.map = {}
        self.listener = None
    
    def terminate(self, env, user):
        print "Terminating."
        if self.listener:
            self.listener.disconnect()
        
    def set_header(self, env, user, text):
        env["HEADER"] = syntax.expand(env, user, text)
    
    def set_footer(self, env, user, text):
        env["FOOTER"] = syntax.expand(env, user, text)

    def post_tweet(self, env, user, text):
        try:
            self.api.PostUpdate(env["HEADER"] + syntax.expand(env, user, text) + env["FOOTER"])
        except twitter.TwitterError:
            print >> sys.stderr, sys.exc_info()[1]

    def twitter_auth(self, env, user, name):
        access_token, access_token_secret = T.get_and_register(name)
        env["NAME"] = name
        self.api = ApiMod(consumer_key=T.CONSUMER_KEY,
                          consumer_secret=T.CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)

    def respond(self, env, user, target, text):
        action = self.respond_parser(text.decode("utf-8"))
        if action:
            if target in self.map:
                action[0](env, user, self.map[target], *action[1:])
            else:
                print >> sys.stderr, "No such target %s" % target
    
    def reply(self, env, user, target, text):
        self.api.PostUpdate("@%s %s" % (target[1], text), target[0])
    
    def unofficialRT(self, env, user, target, text):
        self.api.PostUpdate("%s RT @%s: %s" % (text, target[1], target[2]))
    
    def favorite(self, env, user, target):
        self.api.CreateFavorite(twitter.Status(id=target[0]))
    
    def retweet(self, env, user, target):
        self.api.Retweet(twitter.Status(id=target[0]))
        
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
        self.server = userstream.Client(identifier)

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

class ApiMod(twitter.Api):
    
    def __init__(self, *args, **kwargs):
        twitter.Api.__init__(self, *args, **kwargs)
        self._urllib = curtana.lib.urllib

    def Retweet(self, status):
        url  = '%s/statuses/retweet/%s.json' % (self.base_url, status.id)
        json = self._FetchUrl(url, post_data={'id': status.id})
        data = self._ParseAndCheckTwitter(json)
        return twitter.Status.NewFromJsonDict(data)
