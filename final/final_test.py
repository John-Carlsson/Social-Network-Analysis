import networkx as nx
import random
from lesson5 import randomG
from final_mockup import SocNetMec

"""
Method reads file and creating a graph
:param: fileName = name of the file
:return: graph
"""
def read_graph(fileName):
    G = nx.Graph()
    with open(fileName, 'r') as f:
        for s in f.readlines():
            G.add_edge(s.split()[0], s.split()[1])
    return G

def input_data():
    G = read_graph('net_3')
    numbers_of_nodes = G.number_of_nodes()
    k = random.randint(numbers_of_nodes * 0.005, numbers_of_nodes * 0.05)
    T = 10000

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

"""
Counting the revenue from allocation and payment
@:param allocation = that is a dictionary that has as keys the strings identifying each of the bidders
that submitted a bid, and as value a boolean True if this bidder is allocated one of the items,
and False otherwise.
@:param payment = that is a dictionary that has as keys the strings identifying each of the bidders that
submitted a bid, and as value the price that she pays. Here, a positive price means that the
bidder is paying to the seller, while a negative price means that the seller is paying to the
bidder.
@:return revenue
"""
def getRevenue(allocation, payment):
    revenue = 0
    for key in allocation:
        if allocation[key]:
            revenue += payment[key]
    return revenue

if __name__ == '__main__':
    G, k, T, val, p = input_data()
    snm = SocNetMec(G, k, T)
    revenue = 0
    snm.sorted_by_centrality()
    for step in range(T):
        allocation, payment = snm.run(step, prob, valf)
        revenue += getRevenue(allocation, payment)
    print("Total revenue: " + str(revenue))
    print("Average revenue: " + str(revenue/T))

