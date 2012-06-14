from curtana import path
from curtana.client.component import standard, twitterclient

PROMPT_FORMAT = "%(NAME)s^%(HEADER)s$%(FOOTER)s> "

CLIENT_COMPONENTS = [standard.Standard(), twitterclient.TwitterClient()]

DEFAULT_ACTION = lambda x: "\\" + x
