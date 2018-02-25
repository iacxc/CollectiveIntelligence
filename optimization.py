
import math
from random import random, randint
import time

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

# LaGuardia airport in New York
destination = 'LGA'

flights = {}

for line in open('schedule.csv'):
    origin,dest,depart,arrive,price = line.strip().split(',')
    # Add details to the list of possible flights
    flights.setdefault((origin,dest), []).append((depart,arrive,int(price)))


def city_name(code):
    return {'BOS': 'Boston',
            'DAL': 'Dallas',
            'CAK': 'Akron',
            'MIA': 'Miama',
            'ORD': 'Chicago',
            'OMA': 'Omaha',
            }.get(code)


def random_sched(domain):
    return [randint(d[0], d[1]) for d in domain]


def getminutes(t):
    x = time.strptime(t, '%H:%M')
    minutes = x[3]*60 + x[4]
    return minutes


def printschedule(r):
    for d in range(len(r) // 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin,destination)][r[2*d]]
        ret = flights[(destination,origin)][r[2*d+1]]
        print('{:>10}{:>10} {:>5}-{:>5} ${:3} {:>5}-{:>5} ${:3}'.format(
                  name, city_name(origin),
                  out[0],out[1],out[2],ret[0],ret[1],ret[2]))


def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24*60

    for d in range(len(sol) // 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][sol[2*d]]
        returnf  = flights[(destination, origin)][sol[2*d+1]]

        # Total price is the price of all outbound and return flights
        totalprice += outbound[2] + returnf[2]

        # Track the latest arrival and earliest departure
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):
            earliestdep = getminutes(returnf[0])

    # Every person must wait at the airport until the latest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait = 0
    for d in range(len(sol) // 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][sol[2*d]]
        returnf  = flights[(destination, origin)][sol[2*d+1]]
        
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # Does this solution require an extra day of car rental? That'll be $50!
    if latestarrival > earliestdep:
        totalprice += 50

    cost = totalprice + totalwait
#    print('Totalprice:', totalprice, ', Totalwait:', totalwait, ', Cost:', cost)
    return cost


def randomoptimize(domain, costf=schedulecost):
    best = 999999999
    bestr = None

    for _ in range(1000):
        # Create a random solution
        r = random_sched(domain)

        # Get the cost
        cost = costf(r)

        # Compare it to the best on so far
        if cost < best:
            best = cost
            bestr = r

    return bestr


def hillclimb(domain, costf=schedulecost):
    # Create a random solution
    sol = random_sched(domain)

    # Main loop
    while True:
        # Create list of neighboring solutions
        neighbors = []
        for j in range(len(domain)):
            # One away in each direction
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j]-1] + sol[j+1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j]+1] + sol[j+1:])

        # See what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        for s in neighbors:
            cost = costf(s)
            if cost < best:
                best = cost
                sol = s

            # If there's no improvement, then we've reached the top
        if best == current:
            break

    return sol


def annealingoptimize(domain, costf=schedulecost, T=10000, cool=0.95, step=1):
    # Initialize the values randomly
    vec = random_sched(domain)

    while T>0.1:
        # Choose one of the indices
        i = randint(0, len(domain)-1)

        # Choose a direction to change it
        dir = randint(-step, step)

        # Create a new list with one of the values changed
        # Make sure the new value still within the domain[i]
        vecb = vec[:]
        vecb[i] = min(max(vecb[i]+dir, domain[i][0]), domain[i][1])

        # Calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (-eb-ea)/T)

        # Is it better, or does it make the probability cutoff?
        if eb < ea or random() < p:
            vec = vecb

        # Decrease the temperature
        T *= cool

    return vec


def geneticoptimize(domain, costf=schedulecost, popsize=50, step=1,
                    mutprob=0.2, elite=0.2, maxiter=100):
    # Mutation Operation
    def mutate(vec):
        i = randint(0, len(domain)-1)
        if random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i]-step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i]+step] + vec[i+1:]

    # Crossover Operation
    def crossover(r1, r2):
        i = randint(1, len(domain)-2)
        return r1[0:i] + r2[i:]

    # Build the initial population
    pop = [random_sched(domain) for _ in range(popsize)]

    # How many winners from each generation?
    topelite = int(elite * popsize)

    # Main loop
    for i in range(maxiter):
#        print('Pop:', pop)
        scores = list(sorted((costf(v), v) for v in pop if v is not None))
        ranked = [v for _,v in scores]

        # Start with the pure winners
        pop = ranked[0:topelite]

        # Add mutated and bred forms of the winners
        while len(pop) < popsize:
            if random() < mutprob:
                # Mutation
                c = randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                # Crossover
                c1 = randint(0, topelite)
                c2 = randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        # Print current best score
        print(scores[0][0])

    return scores[0][1]


