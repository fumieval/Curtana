from curtana.client.component import call
from curtana.lib.parser import ApplyN
from curtana.lib.parser_aliases import A, AC, C, S, D, R
from curtana.extension import Extension
import cPickle as pickle
import MeCab
import copy
from curtana.lib import naivebayes

class FaceExprExtension(Extension):
    def initialize(self, client, env, user):
        client.add_syntax(C("/") >> S("faceexpr_enable") >> call(start(client)))
        client.add_syntax(C("/") >> S("faceexpr_enable ") >> call(start(client)) * A)
        client.add_syntax(C("/") >> S("faceexpr_disable") >> call(stop(client)))
    
    def terminate(self, client, env, user):
        if client.faceexpr_path:
            pickle.dump(client.faceexpr_classifier, open(client.faceexpr_path, "w"))

def start(client):
    def f(env, user, path=None):
        if path:
            try:
                client.faceexpr_classifier = pickle.load(open(path, "r"))
            except IOError:
                print "No such file"
        else:
            client.faceexpr_classifier = naivebayes.NaiveBayes()
        
        client.faceexpr_path = path
    
        client.parser_backup = copy.copy(client.tweet_parser)
        
        client.add_syntax(C("/") >> S("faceexpr_train ") >> call(train(client)) * AC * A)
        
        client.add_syntax(C("/") >> S("faceexpr_save") >> call(save(client)))
        client.add_syntax(C("/") >> S("faceexpr_save ") >> call(save(client)) * A)

        client.tweet_parser = (C("!") >> ApplyN(train_and_change_icon(client, user), AC, A)
                               | ApplyN(train_and_change_icon(client, user), R(None), A))

    return f

def stop(client):
    def f(env, user):
        client.parser = client.parser_backup
        client.faceexpr_classifier = None

def wakati(x):
    return MeCab.Tagger(str("-Owakati")).parse(x).decode("utf-8").strip("\n").split(" ")

def save(client):
    def f(env, user, path=None):
        if path is None:
            path = client.faceexpr_path
        if path:
            pickle.dump(client.faceexpr_classifier, open(path, "w"))
        else:
            print "Please specify a path to save."
    return f

def train(client):
    def f(env, user, expression, text):
        client.faceexpr_classifier.train([(expression, wakati(text))])
    return f

def train_and_change_icon(client, user):
    def f(expression, text):
        def _():
            e = expression
            if e:
                client.faceexpr_classifier.train([(e, wakati(text))])
            else:
                e = client.faceexpr_classifier.classify(wakati(text))
            
            if expression:
                client.api.updateProfileImage(user.FACEEXPR_ICON_PATH[e])
            
            return text
        return _
    return f
