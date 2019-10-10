from . import geometry
from . import orderedTSP

np = geometry.np

# Walking speed in m/s
WALKSPEED = 2
# Seconds it takes to communicate link completion
# Agents should report their consecutive links simultaneously
COMMTIME = 60
# Seconds to create a link
LINKTIME = 15


def condense_order(order):
    """
    order is a list of integers
    returns (s,mult)
        where
    mult[i] is the multiplicity of a sequence of repeated s[i]'s in order

    EXAMPLE:
        condense_order( [0,5,5,5,2,2,3,0] )
            returns
        ( [0,5,2,3,0] , [1,3,2,1,1] )
    """
    s = []
    mult = []

    cur = order[0]
    count = 0
    for i in order:
        if i == cur:
            # Count the cur's in a row
            count += 1
        else:
            # Add cur and its count to the lists
            s.append(cur)
            mult.append(count)

            # Start counting the new entry
            cur = i
            count = 1

    # The last sequence never entered the else
    s.append(cur)
    mult.append(count)

    return s, mult


def expand_order(s, mult):
    """
    returns a list with s[i] appearing multi[i] times (in place)

    This is the inverse of condense_order

    EXAMPLE:
        expand_order( [0,5,2,3,0] , [1,3,2,1,1] )
            returns
        [0,5,5,5,2,2,3,0]

    """
    m = len(s)
    n = sum(mult)
    order = [None] * n

    writeat = 0
    for i in range(m):
        count = mult[i]
        # Put in count occurences of s[i]
        order[writeat:writeat + count] = [s[i]] * count
        writeat += count

    return order


def get_agent_order(a, nagents, orderedEdges):
    """
    returns visits
    visits[i] = j means agent j should make edge i

    ALSO creates time attributes in a:

    Time that must be spent just walking
        a.walktime
    Time it takes to communicate completion of a sequence of links
        a.commtime
    Time spent navigating linking menu
        a.linktime
    """
    geo = np.array([a.node[i]['geo'] for i in range(a.order())])
    d = geometry.sphereDist(geo, geo)
    #    print(d)
    order = [e[0] for e in orderedEdges]

    # Reduce sequences of links made from same portal to single entry
    condensed, mult = condense_order(order)

    link2agent, times = orderedTSP.get_visits(d, condensed, nagents)

    # Expand links made from same portal to original count
    link2agent = expand_order(link2agent, mult)

    # If agents communicate sequential completions all at once, we avoid waiting for multiple messages
    # To find out how many communications will be sent, we count the number of same-agent link sequences
    condensed, mult = condense_order(link2agent)
    numCOMMs = len(condensed)

    # Time that must be spent just walking
    a.walktime = times[-1] / WALKSPEED
    # Waiting for link completion messages to be sent
    a.commtime = numCOMMs * COMMTIME
    # Time spent navigating linking menu
    a.linktime = a.size() * LINKTIME

    movements = [None] * nagents

    for i in range(len(link2agent)):
        try:
            movements[link2agent[i]].append(i)
        except:
            movements[link2agent[i]] = [i]

    return movements


#    m = a.size()
#
#    # link2agent[j] is the agent who makes link j
#    link2agent = [-1]*m
#    for i in range(nagents):
#        for j in movements[i]:
#            link2agent[j] = i
#
#    bestT = completionTime(a,movements)
#
#    sinceImprove = 0
#    i=0
#    while sinceImprove < m:
#        agent = link2agent[i]
#        
#        # for each of the other agents
#        for alt in range(agent-nagents+1,agent):
#
#            alt %= nagents
#            # see what happens if agent 'alt' makes the link
#            link2agent[i] = alt
#
#            T = completionTime(a,link2agent)
#
#            if T < bestT:
#                bestT = T
#                sinceImprove = 0
#                break
#        else:
#            # The loop exited normally, so no improvement was found
#            link2agent[i] = agent # restore the original plan
#            sinceImprove += 1
#
#        i = (i+1)%m
#
#    return movements
#
#
def improve_edge_order(a):
    """
    Edges that do not complete any fields can be made earlier
    This method alters the graph a such that
        The relative order of edges that complete fields is unchanged
        Edges that do not complete fields may only be completed earlier
        Where possible, non-completing edges are made immediately before another edge with same origin
    """
    m = a.size()
    # If link i is e then orderedEdges[i]=e
    ordered_edges = [-1] * m

    for p, q in a.edges_iter():
        ordered_edges[a.edge[p][q]['order']] = (p, q)

    for j in range(1, m):
        p, q = ordered_edges[j]
        # Only move those that don't complete fields
        if len(a.edge[p][q]['fields']) > 0:
            continue

        #        print j,p,q,a.edge[p][q]['fields']

        origin = ordered_edges[j][0]
        # The first time this portal is used as an origin
        i = 0
        while ordered_edges[i][0] != origin:
            i += 1

        if i < j:
            # Move link j to be just before link i
            ordered_edges = ordered_edges[:i] + \
                           [ordered_edges[j]] + \
                           ordered_edges[i:j] + \
                           ordered_edges[j + 1:]
            # TODO else: choose the closest earlier portal

    for i in range(m):
        p, q = ordered_edges[i]
        a.edge[p][q]['order'] = i


# print()

if __name__ == '__main__':
    order = [0, 5, 5, 5, 2, 2, 1, 0]  # what is this, what is it based on and how do we clarify
    s, mult = condense_order(order)
    print(s)
    print(mult)
    print(order)
    print(expand_order(s, mult))
'''
== Jonathan: maxfield $ python makePlan.py 4 almere/lastPlan.pkl almere/
Total time: 1357.37352334
== Jonathan: maxfield $ python makePlan.py 5 almere/lastPlan.pkl almere/
Total time: 995.599917771
== Jonathan: maxfield $ python makePlan.py 6 almere/lastPlan.pkl almere/
Total time: 890.389138077
== Jonathan: maxfield $ python makePlan.py 7 almere/lastPlan.pkl almere/
Total time: 764.127789228
== Jonathan: maxfield $ python makePlan.py 8 almere/lastPlan.pkl almere/
Total time: 770.827639967
'''
