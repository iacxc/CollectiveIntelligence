

# the dorms, each of which has two available spaces
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# People, along with their first and second choices
prefs = [('Toby', ('Bacchus', 'Hercules')),
         ('Steve', ('Zeus', 'Pluto')),
         ('Andrea', ('Athena', 'Zeus')),
         ('Sarah', ('Zeus', 'Pluto')),
         ('Dave', ('Athena', 'Bacchus')),
         ('Jeff', ('Hercules', 'Pluto')),
         ('Fred', ('Pluto', 'Athena')),
         ('Suzie', ('Bacchus', 'Hercules')),
         ('Laura', ('Bacchus', 'Hercules')),
         ('Neil', ('Hercules', 'Athena'))
        ]

domain = [(0, len(dorms)*2-i-1) for i in range(len(dorms)*2)]

def printsolution(vec):
    slots = []
    # Create two slots for each dorm
    for i in range(len(dorms)):
        slots += [i,i]

    # Loop over each students assignment
    for i,x in enumerate(vec):
        # Choose the slot from the remaining ones
        dorm = dorms[slots[x]]
        # Show the student and assigned dorm
        print(prefs[i][0], dorm)
        # Remove the slot
        del slots[x]


def dormcost(vec):
    slots = []
    # Create two slots for each dorm
    for i in range(len(dorms)):
        slots += [i,i]

    cost = 0
    # Loop over each student
    for i,x in enumerate(vec):
        dorm = dorms[slots[x]]
        pref = prefs[i][1]
#        print(prefs[i][0], pref, dorm, end=' ')
        # First choice costs 0, second choice costs 1, not on the list costs 3
        if pref[0] == dorm:
            cost += 0
#            print()
        elif pref[1] == dorm:
            cost += 1
#            print('+1')
        else:
            cost += 3
#            print('+3')

        del slots[x]

    return cost
