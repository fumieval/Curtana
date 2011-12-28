
from urlparse import parse_qsl
import shelve
import oauth2 as oauth
from curtana import path

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
ACCESS_TOKEN_URL  = "https://api.twitter.com/oauth/access_token"
AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"

CONSUMER_KEY = "jBpVb6iFCawuxnXPRsw"
CONSUMER_SECRET = "NS0oAAhaRGgd931Hqak8HtqvGf8pgvryS693HmnF1I"

def get_and_register(name):
    db = shelve.open(path.USERDB)
    if name not in db:
        db[name] = auth()[1]
    return db[name]

def auth():
    "Authenticate to twitter and get access token."

    #signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY,
                                    secret=CONSUMER_SECRET)
    oauth_client = oauth.Client(oauth_consumer)
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
    
        oauth_client  = oauth.Client(oauth_consumer, token)
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

