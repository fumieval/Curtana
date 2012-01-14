
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

def get_and_register(name):
    db = shelve.open(path.USERDB)
    if name not in db:
        db[name] = auth()[1]
    return db[name]

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
    
    def __init__(self, twitter_token = None, twitter_secret = None, oauth_token = None, oauth_token_secret = None, headers=None, callback_url=None, client_args={}):
        """setup(self, oauth_token = None, headers = None)

            Instantiates an instance of Twython. Takes optional parameters for authentication and such (see below).

            Parameters:
                twitter_token - Given to you when you register your application with Twitter.
                twitter_secret - Given to you when you register your application with Twitter.
                oauth_token - If you've gone through the authentication process and have a token for this user,
                    pass it in and it'll be used for all requests going forward.
                oauth_token_secret - see oauth_token; it's the other half.
                headers - User agent header, dictionary style ala {'User-Agent': 'Bert'}
                client_args - additional arguments for HTTP client (see httplib2.Http.__init__), e.g. {'timeout': 10.0}

                ** Note: versioning is not currently used by search.twitter functions; when Twitter moves their junk, it'll be supported.
        """
        # Needed for hitting that there API.
        self.request_token_url = 'http://twitter.com/oauth/request_token'
        self.access_token_url = 'http://twitter.com/oauth/access_token'
        self.authorize_url = 'http://twitter.com/oauth/authorize'
        self.authenticate_url = 'http://twitter.com/oauth/authenticate'
        self.twitter_token = twitter_token
        self.twitter_secret = twitter_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_token_secret
        self.callback_url = callback_url

        proxy_info = get_proxy_info()

        # If there's headers, set them, otherwise be an embarassing parent for their own good.
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Curtana powered by Twython Python Twitter Library v1.3'}

        self.consumer = None
        self.token = None

        if self.twitter_token is not None and self.twitter_secret is not None:
            self.consumer = oauth.Consumer(self.twitter_token, self.twitter_secret)

        if self.oauth_token is not None and self.oauth_secret is not None:
            self.token = oauth.Token(oauth_token, oauth_token_secret)

        # Filter down through the possibilities here - if they have a token, if they're first stage, etc.
        if self.consumer is not None and self.token is not None:
            self.client = oauth.Client(self.consumer, self.token, proxy_info=proxy_info, **client_args)
        elif self.consumer is not None:
            self.client = oauth.Client(self.consumer, proxy_info=proxy_info, **client_args)
        else:
            # If they don't do authentication, but still want to request unprotected resources, we need an opener.
            self.client = httplib2.Http(proxy_info=proxy_info, **client_args)

    @staticmethod
    def from_name(name):
        access_token, access_token_secret = get_and_register(name)
        return ApiMod(CONSUMER_KEY, CONSUMER_SECRET,
                      access_token, access_token_secret)

    def updateProfileImage(self, filename, version = 1):
        import urllib2
        """ updateProfileImage(filename)

            Updates the authenticating user's profile image (avatar).

            Parameters:
                image - Required. Must be a valid GIF, JPG, or PNG image of less than 700 kilobytes in size. Images with width larger than 500 pixels will be scaled down.
                version (number) - Optional. API version to request. Entire Twython class defaults to 1, but you can override on a function-by-function or class basis - (version=2), etc.
        """
        try:
            files = [("image", filename, open(filename, 'rb').read())]
            fields = []
            content_type, body = twython.twython.Twython.encode_multipart_formdata(fields, files)
            headers = {'Content-Type': content_type, 'Content-Length': str(len(body))}
            resp, content = self.client.request("http://api.twitter.com/%d/account/update_profile_image.json" % version, method='POST', body=body, headers=headers)
            return twython.twython.simplejson.loads(content.decode('utf-8'))
        except urllib2.HTTPError, e:
            print e
            raise twython.twython.TwythonError("updateProfileImage() failed with a %d error code." % e.code, e.code)
        