import sys
import curtana.lib.parser as P
from curtana import userstream

def is_hashtag_char(c):
    return c == "_" or c.isalnum() or 12353 <= ord(c) <= 12534 or 20124 <= ord(c) <= 40657

SCREEN_NAME = P.StringA ** P.Char("@") * P.join ** +(P.alnum | P.Char("_"))
HASHTAG = P.StringA ** P.Char("#") * P.join ** +P.Sat(is_hashtag_char)

def arrangetext():
    return P.Null() | withcolor(35) ** HASHTAG | \
        P.StringA ** (P.Char("&") >> (P.String("gt;") >> P.Return(">")
                                       | P.String("lt;") >> P.Return("<"))
                       | withcolor(36) ** SCREEN_NAME
                       | P.StringA * P.Char(" ") * withcolor(35) ** HASHTAG
                       | P.AnyChar()
                       ) * P.Delay(arrangetext)

def withcolor(color):
    return lambda text: '\033[1;%dm%s\033[1;m' % (color, text)

def isfavs(data):
    return "event" in data and data["event"] in ["favorite", "unfavorite"]

def isstatus(data):
    return "user" in data and "id" in data

def showstatus(i, data):
    if isstatus(data):
        name = data["user"]["screen_name"]
        if "retweeted_status" in data:
            st = data["retweeted_status"]
            print " ".join([withcolor(33)(i),
                            withcolor(32)(st["user"]["screen_name"]) + ":",
                            arrangetext()(st["text"])[0],
                            "--" + withcolor(34)(name)])
        else:
            print " ".join([withcolor(33)(i),
                            withcolor(34)(name) + ":",
                            arrangetext()(data["text"])[0]])

def listen_timeline(identifier):
    client = userstream.Client(identifier)
    it = iter(client)
    while True:
        try:
            i, data = next(it)
        except KeyboardInterrupt:
            print "Aborted."
            break
        if data is None:
            print "Stream stopped."
            break
        showstatus(i, data)
        
if __name__ == "__main__":
    if sys.argv[1] == "server":
        userstream.serve()
    if sys.argv[1] == "timeline":
        listen_timeline(sys.argv[2])