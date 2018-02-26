from collections import defaultdict
import re


def getwords(doc):
    splitter = re.compile(r'\W+')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]

    # Return the unique set of words only
    return {w: 1 for w in words}


def sampletrain(cl):
    cl.train('Noboday owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


class Classifier:
    def __init__(self, getfeatures=getwords, filename=None):
        # Counts of feature/category combinations
        self.fc = defaultdict(lambda: defaultdict(int))
        # Counts of documents in each category
        self.cc = defaultdict(int)
        self.getfeatures = getfeatures

    # Increase the count of a feature/category pair
    def incf(self, f, cat):
        self.fc[f][cat] += 1

    # Increase the count of a category
    def incc(self, cat):
        self.cc[cat] += 1

    # The number of times a feature has appeared in a category
    def fcount(self, f, cat):
        return self.fc[f][cat]

    # The number of times in a category
    def catcount(self, cat):
        return self.cc[cat]

    # The total number of items
    def totalcount(self):
        return sum(self.cc.values())

    # The list of all categories
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getfeatures(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # Increment the count for this category
        self.incc(cat)

    def fprob(self, f, cat):
        if self.catcount(cat) == 0:
            return 0

        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # Calculate current probability
        basicprob = prf(f, cat)

        # Count the number of times this feature has appeared
        # in all categories
        totals = sum(self.fcount(f,c) for c in self.categories())

        # Calculate the weighted average
        return  (weight*ap + totals*basicprob)/(weight+totals)


class Naivebayes(Classifier):
    def __init__(self, getfeatures=getwords):
        super().__init__(getfeatures)
        self.thresholds = defaultdict(lambda: 1.0)

    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # Multiply the probabilities of all the features together
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)

        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)

        return docprob * catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}

        # Find the category with the highest probability
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat == best:
                continue
            if probs[cat] * self.getthreshold(best) > probs[best]:
                return default

        return best

