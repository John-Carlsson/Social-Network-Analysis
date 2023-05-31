import networkx as nx
import random
from lesson5 import randomG
from final_mockup import SocNetMec


def input_data():
    n = 100
    G = randomG(n, 0.3) #This will be updated to the network model of net_x
    k = 5
    T = 5000

    #for the oracle val
    val = dict()
    for t in range(T):
        val[t] = dict()
        for u in G.nodes():
            val[t][u] = random.randint(1, 100)
    
    #for the oracle prob
    p = dict()
    for u in G.nodes():
        p[u] = dict()
    for u in G.nodes():
        for v in G[u]:
            if v not in p[u]:
                t=min(0.25, 2/max(G.degree(u), G.degree(v)))
                p[u][v] = p[v][u] = random.uniform(0, t)
            
    return G, k, T, val, p

def prob(u, v):
    r = random.random()
    if r <= p[u][v]:
        return True
    return False

def valf(t, u):
    return val[t][u]

if __name__ == '__main__':
    G, k, T, val, p = input_data()
    snm = SocNetMec(G, k, T)
    revenue = 0
    for step in range(T):
        revenue = revenue + snm.run(step, prob, valf)

    print(revenue)

