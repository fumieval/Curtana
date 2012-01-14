from collections import defaultdict
import math

class NaiveBayes:
    def __init__(self):
        self.vocabularies = set()
        self.wordcount = {}
        self.categories = {}
        self.denominator = {}
                
    def train(self, data):
        for cat, doc in data:
            if not cat in self.categories:
                self.categories[cat] = 0
                self.wordcount[cat] = defaultdict(int)
            
            self.categories[cat] += 1
            for word in doc:
                self.vocabularies.add(word)
                self.wordcount[cat][word] += 1
        for cat in self.categories:
            self.denominator[cat] = sum(self.wordcount[cat].itervalues()) + len(self.vocabularies)
    
    def classify(self, doc):
        result = [(cat, self.score(doc, cat)) for cat in self.categories]
        if result:
            best = max(b for _, b in result)
            return next(cat for cat, score in result if score == best)
    
    def wordProb(self, word, cat):
        return float(self.wordcount[cat][word] + 1) / float(self.denominator[cat])
    
    def score(self, doc, cat):
        total = sum(self.categories.itervalues())
        return math.log(float(self.categories[cat]) / total) + \
            sum(math.log(self.wordProb(word, cat)) for word in doc)
    