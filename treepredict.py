
from collections import defaultdict, Counter
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt


my_data = [['slashdot',    'USA',         'yes', 18,  'None'],
           ['google',      'France',      'yes', 23,  'Premium'],
           ['digg',        'USA',         'yes', 24,  'Basic'],
           ['kiwitobes',   'France',      'yes', 23,  'Basic'],
           ['google',      'UK',          'no',  21,  'Premium'],
           ['(direct)',    'New Zealand', 'no',  12,  'None'],
           ['(direct)',    'UK',          'no',  21,  'Basic'],
           ['google',      'USA',         'no',  24,  'Premium'],
           ['slashdot',    'France',      'yes', 19,  'None'],
           ['digg',        'USA',         'no',  18,  'None'],
           ['google',      'UK',          'no',  18,  'None'],
           ['kiwitobes',   'UK',          'no',  19,  'None'],
           ['digg',        'New Zealand', 'yes', 12,  'Basic'],
           ['slashdot',    'UK',          'no',  21,  'None'],
           ['google',      'UK',          'yes', 18,  'Basic'],
           ['kiwitobes',   'France',      'yes', 19,  'Basic']]


class DecisionNode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb

# Divides a set on a specific column. Can handle numeric
# or nominal values
def divideset(rows, column, value):
    # Make a function that tells us if a row is in
    # the first group (true) or the second group (false)
    if isinstance(value, (int, float)):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    # Divide the rows into two sets and return them
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]

    return set1, set2


def uniquecounts(rows):
    return Counter(row[-1] for row in rows)

# Probability that a randomly placed item will
# be in the wrong category
def giniimpurity(rows):
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = counts[k1] / total
        for k2 in counts:
            if k1 != k2:
                p2 = counts[k2] / total
                imp += p1*p2

    return imp


# Entropy is the sum of p(x)log(p(x)) across all
# the different possible results
def entropy(rows):
    from math import log
    log2 = lambda x: log(x) / log(2)

    results = uniquecounts(rows)

    # Now calculate the entropy
    ent = 0
    for c in results.values():
        p = c / len(rows)
        ent -= p*log2(p)

    return ent


def buildtree(rows, scoref=entropy):
    if not rows:
        return DecisionNode()

    current_score = scoref(rows)

    # Setup some variables to track the best criteria
    best_gain = 0
    best_criteria = None
    best_sets = None

    for col in range(len(rows[0]) - 1):
        # Generate the list of different values in this column
        column_values = set(row[col] for row in rows)

        # Now try dividing the rows up for each value in this column
        for value in column_values:
            (set1, set2) = divideset(rows, col, value)

            # Information gain
            p = len(set1) / len(rows)
            gain = current_score - p*scoref(set1) - (1-p)*scoref(set2)
            if gain > best_gain and set1 and set2:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    # Create the subbranches
    if best_gain > 0:
        trueBranch = buildtree(best_sets[0])
        falseBranch = buildtree(best_sets[1])
        return DecisionNode(col=best_criteria[0], value=best_criteria[1],
                            tb=trueBranch, fb=falseBranch)
    else:
        return DecisionNode(results=uniquecounts(rows))


def printtree(tree, indent='  '):
    # Is this a leaf node?
    if tree.results:
        print(tree.results)
    else:
        # Print the criteria
        print(str(tree.col) + ':' + str(tree.value) + '?')

        # Print the branches
        print(indent + 'T->', end=' ')
        printtree(tree.tb, indent + '   ')
        print(indent + 'F->', end=' ')
        printtree(tree.fb, indent + '   ')

def getwidth(tree):
    if tree.tb is None and tree.fb is None:
        return 1
    return getwidth(tree.tb) + getwidth(tree.fb)


def getdepth(tree):
    if tree.tb is None and tree.tb is None:
        return 0
    return max(getdepth(tree.tb), getdepth(tree.fb)) + 1


def drawtree(tree):
    w = getwidth(tree) * 100
    h = getdepth(tree) * 100 + 120

    _, ax = plt.subplots()
    ax.set_xlim(left=0, right=w)
    ax.set_ylim(bottom=0, top=h)

    drawnode(ax, tree, w/2, 20)

    plt.plot()
    plt.show()


def drawline(ax, posa, posb, color='black'):
    line = [posa, posb]
    (xs, ys) = zip(*line)
    ax.add_line(Line2D(xs, ys, color=color))


def drawnode(ax, tree, x, y):

    if tree.results is None:
        # Get the width of each branch
        w1 = getwidth(tree.fb) * 100
        w2 = getwidth(tree.tb) * 100

        # Determine the total space required by this node
        left = x-(w1+w2)/2
        right = x+(w1+w2)/2

        # Draw the conditiona string
        plt.text(x-20, y-10, str(tree.col) + ':' + str(tree.value) + '?')

        # Draw lines to the branches
        drawline(ax, (x,y), (left+w1/2, y+100), color='blue')
        drawline(ax, (x,y), (right-w2/2, y+100), color='blue')

        #Draw the branch nodes
        drawnode(ax, tree.fb, left+w1/2,  y+100)
        drawnode(ax, tree.tb, right-w2/2, y+100)
    else:
        txt = '\n'.join('%s:%d' % v for v in tree.results.items())
        plt.text(x-20, y, txt)


def classify(observation, tree):
    if tree.results is not None:
        return tree.results

    v = observation[tree.col]
    branch = None
    if isinstance(v, (int, float)):
        branch = tree.tb if v >= tree.value else tree.fb
    else:
        branch = tree.tb if v == tree.value else tree.fb

    return classify(observation, branch)
