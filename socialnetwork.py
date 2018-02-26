import math
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

people = ['Charlie', 'Augustus', 'Veruca', 
          'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']
links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe'),
        ]

domain = [(10,770)] * (len(people)*2)

def crosscount(v):
    # Convert the number list into a dictionary of person:(x,y)
    loc = {people[i]: (v[i*2], v[i*2+1]) for i in range(len(people))}

    total = 0
    # Loop through every pair of links
    for i in range(len(links)):
        for j in range(i+1, len(links)):
            (x1,y1), (x2,y2) = loc[links[i][0]], loc[links[i][1]]
            (x3,y3), (x4,y4) = loc[links[j][0]], loc[links[j][1]]

            den = (y4-y3)*(x2-x1) + (x4-x3)*(y2-y1)

            # den == 0 fi the lines are parallel
            if den == 0: 
                continue

            # Otherwise ua and ub are the fraction of the
            # line where they cross
            ua = ((x4-x4)*(y1-y3)-(y4-y3)*(x1-x3))/den
            ub = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den

            # If the fraction is between 0 and 1 for both lines
            # then they cross each other
            if 0<ua<1 and 0<ub<1:
                total += 1

    for i in range(len(people)):
        for j in range(i+1, len(people)):
            # Get the locations of the two nodes
            (x1,y1), (x2,y2) = loc[people[i]], loc[people[j]]

            # Find the distance between them
            dist = math.sqrt((x1-x2) ** 2 +(y1-y2) ** 2)
            if dist < 50:
                total += (1.0-(dist/50))
    
    return total


def drawnetwork(sol):
    def drawline(ax, posa, posb, color='black'):
        line = [posa, posb]
        (xs, ys) = zip(*line)

        ax.add_line(Line2D(xs, ys, linewidth=1, color=color))

    figure, ax = plt.subplots()
    ax.set_xlim(left=0,right=800)
    ax.set_ylim(bottom=0, top=800)

    # Create the position dict
    pos = {people[i]: (sol[i*2], sol[i*2+1]) for i in range(len(people))}

    for a,b in links:
        drawline(ax, pos[a], pos[b], color='red')

    # Draw people
    for n, p in pos.items():
        plt.text(*p, n, size=14)

    plt.plot()
    plt.show()

