
import sys
import curtana.lib.parser_aliases as P
import curtana.lib.parser_entities as E
from curtana.lib.container import StringA
import curtana.reader.condition as C
from curtana.common import userstream

def is_hashtag_char(c):
    return c == "_" or c.isalnum() or 12353 <= ord(c) <= 12534 or 20124 <= ord(c) <= 40657

SCREEN_NAME = StringA() ** P.C("@") * "".join ** +(E.alnum | P.C("_"))
HASHTAG = StringA() ** P.C("#") * "".join ** +P.P(is_hashtag_char)

def arrangetext():
    return P.N | withcolor(35) ** HASHTAG | \
        StringA() ** (P.C("&") >> (P.S("gt;") >> P.R(">")
                                   | P.S("lt;") >> P.R("<"))
                       | withcolor(36) ** SCREEN_NAME
                       | StringA() ** P.C(" ") * withcolor(35) ** HASHTAG
                       | P.AC
                       ) * P.Z(arrangetext)

def withcolor(color):
    return lambda text: u'\033[1;%dm%s\033[1;m' % (color, text)

def isfavs(data):
    return "event" in data and data["event"] in ["favorite", "unfavorite"]

def isstatus(data):
    return "user" in data and "id" in data

def block(index, name, time, text, addition=""):
    print withcolor(33)(index), time.split(" ")[3], name, addition
    print text
    print

def showstatus(i, data):
    name = data["user"]["screen_name"]
    if "retweeted_status" in data:
        st = data["retweeted_status"]
        block(i, withcolor(32)(st["user"]["screen_name"]), data["created_at"],
              unicode(arrangetext()(st["text"])),
              "retweeted by " + withcolor(34)(name))
    else:
        block(i, withcolor(34)(name), data["created_at"],
              unicode(arrangetext()(data["text"])))

def listen_timeline(identifier, condition=C.Return(True)):
    client = userstream.Client(identifier)
    print "Client index:", client.index
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
        if isstatus(data) and condition.check(data):
            showstatus(i, data)
        
if __name__ == "__main__":
    if sys.argv[1] == "server":
        userstream.serve()
    if sys.argv[1] == "timeline":
        listen_timeline(sys.argv[2])
    if sys.argv[1] == "close":
        s = userstream.Client(sys.argv[2])
        s.index = sys.argv[3]
        s.close()