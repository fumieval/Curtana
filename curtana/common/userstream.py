"""
Functions and classes for manipulating User Streams
"""

import urllib, urllib2

from curtana.lib import oauth

from curtana.lib.prelude import *
from curtana.lib.stream import *

from curtana.common.twitterlib import get_or_register, CONSUMER_KEY, CONSUMER_SECRET

import json

USER_STREAMS_URL = "https://userstream.twitter.com/2/user.json"

def streamopen(name, url=USER_STREAMS_URL):
    param = {}
    headers = {}
    token = oauth.OAuthToken(*get_or_register(name))
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    request = oauth.OAuthRequest.from_consumer_and_token(
        oauth_consumer=consumer, http_url=url, http_method="POST",
        token=token, parameters=param)
    
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    headers.update(request.to_header())
    return urllib2.urlopen(urllib2.Request(url, headers=headers),
                           urllib.urlencode(param))

def iterstream(stream):
    return (SplitBy("\n".__eq__)
            >> Map("".join) >> Map(flip(str.strip)("\r"))
            >> Filter("".__ne__)
            >> Map(json.loads))(iterate(lambda: stream.read(1)))
