
from urlparse import parse_qsl
import shelve
import oauth2 as oauth
from curtana import path
import os

import twython
from curtana.lib.container import TupleA
import curtana.lib.parser_aliases as P

import httplib2

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
ACCESS_TOKEN_URL  = "https://api.twitter.com/oauth/access_token"
AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"

CONSUMER_KEY = "jBpVb6iFCawuxnXPRsw"
CONSUMER_SECRET = "NS0oAAhaRGgd931Hqak8HtqvGf8pgvryS693HmnF1I"

PROXY_PARSER = TupleA() ** (P.S("http://") >> P.D(P.C(":"))) * P.D(P.C("/"))

def get_or_register(name):
    db = shelve.open(path.USERDB)
    if name not in db:
        db[name] = auth()[1]
    return db[name]

def register(name):
    shelve.open(path.USERDB)[name] = auth()[1]
    
def get_proxy_info():
    if "http_proxy" in os.environ:
        proxy = PROXY_PARSER(os.environ["http_proxy"])
        if proxy:
            return oauth.httplib2.ProxyInfo(oauth.httplib2.socks.PROXY_TYPE_HTTP, proxy[0], int(proxy[1]))


def auth():
    "Authenticate to twitter and get access token."

    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY,
                                    secret=CONSUMER_SECRET)
    
    proxy_info = get_proxy_info()

    oauth_client = oauth.Client(oauth_consumer, proxy_info=proxy_info)
    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')
    
    if resp['status'] == '200':
        request_token = dict(parse_qsl(content))
        print('Please get the PIN Code from the following URL.')
        print('%s?oauth_token=%s' % (AUTHORIZATION_URL,
                                     request_token['oauth_token']))
        try:
            pincode = raw_input('PIN Code:')
        except NameError:
            pincode = input('PIN Code:')
    
        print('Getting Access Token...')
        token = oauth.Token(request_token['oauth_token'],
                            request_token['oauth_token_secret'])
        token.set_verifier(pincode)
    
        oauth_client  = oauth.Client(oauth_consumer, token, proxy_info=proxy_info)
        resp, content = oauth_client.request(ACCESS_TOKEN_URL,
                                             method='POST',
                                             body='oauth_verifier=%s' % pincode)
        
        access_token  = dict(parse_qsl(content))
        
        if resp['status'] == '200':
            print("Authenticated successfully: @%s." % access_token['screen_name'])
            return access_token['screen_name'], (access_token['oauth_token'],
                                                 access_token['oauth_token_secret'])
        else:
            print("Couldn't get the token: status %s" % resp['status'])
            return None
    else:
        print('There was no response from twitter: status %s' % resp['status'])
        return None

class ApiMod(twython.Twython):
    @staticmethod
    def from_name(name):
        proxies = dict((x, y) for x, y in [("http", ":".join(PROXY_PARSER(os.environ["http_proxy"]))),
                        ("https", ":".join(PROXY_PARSER(os.environ["https_proxy"])))] if y)
        
        access_token, access_token_secret = get_or_register(name)
        return ApiMod(CONSUMER_KEY, CONSUMER_SECRET,
                      access_token, access_token_secret,
                      proxies=proxies)
