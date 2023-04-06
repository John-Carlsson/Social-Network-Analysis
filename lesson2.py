import networkx as nx
from queue import PriorityQueue
import random
from scipy.sparse import linalg

def hierarchical(G):
    # Create a priority queue with each pair of nodes indexed by distance
    pq = PriorityQueue()
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                if (u, v) in G.edges() or (v, u) in G.edges():
                    pq.add(frozenset([frozenset(u), frozenset(v)]), 0)
                else:
                    pq.add(frozenset([frozenset(u), frozenset(v)]), 1)

    # Start with a cluster for each node
    clusters = set(frozenset(u) for u in G.nodes())

    done = False
    while not done:
        # Merge closest clusters
        s = list(pq.pop())
        clusters.remove(s[0])
        clusters.remove(s[1])

        # Update the distance of other clusters from the merged cluster
        for w in clusters:
            e1 = pq.remove(frozenset([s[0], w]))
            e2 = pq.remove(frozenset([s[1], w]))
            if e1 == 0 or e2 == 0:
                pq.add(frozenset([s[0] | s[1], w]), 0)
            else:
                pq.add(frozenset([s[0] | s[1], w]), 1)

        clusters.add(s[0] | s[1])

        print(clusters)
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True


def two_means(G):
    n=G.number_of_nodes()
    # Choose two clusters represented by vertices that are not neighbors
    u = random.choice(list(G.nodes()))
    v = random.choice(list(nx.non_neighbors(G, u)))
    cluster0 = {u}
    cluster1 = {v}
    added = 2

    while added < n:
        # Choose a node that is not yet in a cluster and add it to the closest cluster
        x = random.choice([el for el in G.nodes() if el not in cluster0|cluster1 and (len(
            set(G.neighbors(el)).intersection(cluster0)) != 0 or len(set(G.neighbors(el)).intersection(cluster1)) != 0)])
        if len(set(G.neighbors(x)).intersection(cluster0)) != 0:
            cluster0.add(x)
            added+=1
        elif len(set(G.neighbors(x)).intersection(cluster1)) != 0:
            cluster1.add(x)
            added+=1

    return cluster0, cluster1

# Computes edge and vertex betweenness of the graph in input
def betweenness(G):
    edge_btw={frozenset(e):0 for e in G.edges()}
    node_btw={i:0 for i in G.nodes()}

    for s in G.nodes():
        # Compute the number of shortest paths from s to every other node
        tree = [] #it lists the nodes in the order in which they are visited
        spnum = {i:0 for i in G.nodes()} #it saves the number of shortest paths from s to i
        parents = {i:[] for i in G.nodes()} #it saves the parents of i in each of the shortest paths from s to i
        distance = {i:-1 for i in G.nodes()} #the number of shortest paths starting from s that use the edge e
        eflow = {frozenset(e):0 for e in G.edges()} #the number of shortest paths starting from s that use the edge e
        vflow = {i:1 for i in G.nodes()} #the number of shortest paths starting from s that use the vertex i. It is initialized to 1 because the shortest path from s to i is assumed to uses that vertex once.

        #BFS
        queue = [s]
        spnum[s] = 1
        distance[s] = 0
        while queue != []:
            c = queue.pop(0)
            tree.append(c)
            for i in G[c]:
                if distance[i] == -1: #if vertex i has not been visited
                    queue.append(i)
                    distance[i] = distance[c] + 1
                if distance[i] == distance[c] + 1: #if we have just found another shortest path from s to i
                    spnum[i] += 1
                    parents[i].append(c)

        # BOTTOM-UP PHASE
        while tree != []:
            c = tree.pop()
            for i in parents[c]:
                eflow[frozenset({c,i})] += vflow[c] * (spnum[i]/spnum[c]) #the number of shortest paths using vertex c is split among the edges towards its parents proportionally to the number of shortest paths that the parents contributes
                vflow[i] += eflow[frozenset({c,i})] #each shortest path that use an edge (i,c) where i is closest to s than c must use also vertex i
                edge_btw[frozenset({c, i})] += eflow[frozenset({c,i})] #betweenness of an edge is the sum over all s of the number of shortest paths from s to other nodes using that edge
            if c != s:
                node_btw[c] += vflow[c]  #betweenness of a vertex is the sum over all s of the number of shortest paths from s to other nodes using that vertex
    return edge_btw,node_btw
#The algorithm is quite time-consuming. Indeed, its computational complexity is O(nm).
# optimizations: parallelization, considering only a sample of starting nodes

# Clusters are computed by iteratively removing edges of largest betweenness
def girman_newman(G):
    graph=G.copy() #We make a copy of the graph. In this way we will modify the copy, but not the original graph
    done = False
    while not done:
        # After each edge removal we will recompute betweenness:
        # indeed, edges with lower betweenness may have increased their importance,
        # since shortest path that previously went through on deleted edges, now may be routed on this new edge;
        # similarly, edges with high betweenness may have decreased their importance,
        # since most of the shortest paths previously going through them disappeared because the graph has been disconnected.
        # However, complexity arising from recomputing betweenness at each iteration is huge.
        # An optimization in this case would be to compute betweenness only once
        # and to remove edges in decreasing order of computed betweenness.
        eb, nb = betweenness(graph)
        #Finding the edge with highest betweenness
        edge = None
        bet = -1
        for i in eb.keys():
            if eb[i] > bet:
                edge = i
                bet = eb[i]
        graph.remove_edge(*(list(edge)))

        #Deciding whether to stop the clustering procedure
        #To automatize this decision, we can use some measure of performance of the clustering.
        #An example of this measure is the function nx.algorithms.community.partition_quality(G, list(nx.connected_components(graph))).
        #See networx documentation for more details.
        #Given one such measure, one may continue iteration of the algorithm as long as the newly achieved clustering
        #has performance that are not worse than the previous clustering or above a given threshold.
        print(list(nx.connected_components(graph)))
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True

    return list(nx.connected_components(graph))

#Spectral clustering algorithm
def spectral(G):
    n=G.number_of_nodes()
    nodes = sorted(G.nodes())
    # Laplacian of a graph is a matrix, with diagonal entries being the degree of the corresponding node
    # and off-diagonal entries being -1 if an edge between the corresponding nodes exists and 0 otherwise
    L=nx.laplacian_matrix(G, nodes).asfptype()
    # print(L) #To see the laplacian of G uncomment this line
    # The following command computes eigenvalues and eigenvectors of the Laplacian matrix.
    # Recall that these are scalar numbers w_1, ..., w_k and vectors v_1, ..., v_k such that Lv_i=w_iv_i.
    # The first output is the array of eigenvalues in increasing order.
    # The second output contains the matrix of eigenvectors:
    # specifically, the eigenvector of the k-th eigenvalue is given by the k-th column of v
    w, v = linalg.eigsh(L,n-1)
    # print(w) #Print the list of eigenvalues
    # print(v) #Print the matrix of eigenvectors
    # print(v[:,0]) #Print the eigenvector corresponding to the first returned eigenvalue

    # Partition in clusters based on the corresponding eigenvector value being positive or negative
    # This is known to return (an approximation of) the sparset cut of the graph
    # That is, the cut with each of the clusters having many edges, and with few edge among clusters
    # Note that this is not the minimum cut (that only requires few edge among clusters,
    # but it does not require many edge within clusters)
    c1= set()
    c2=set()
    for i in range(n):
        if v[i,0] < 0:
            c1.add(nodes[i])
        else:
            c2.add(nodes[i])
    return (c1, c2)
# How to achieve more than two clusters? Two options:
# (i) for each subgraph corresponding to one of the clusters, we can split this subgraph by running the spectral algorithm on it;
# (ii) we can use further eigenvectors. For example, we can partition nodes in four clusters by using the first two eigenvectors,
#     so that the first (second, respectively) cluster contains those nodes i such that v[i,0] and v[i,1] are both negative (both non-negative, resp.)
#     while the third (fourth, respectively) cluster contains those nodes i such that only v[i,0] (only v[i,1], resp.) is negative.

#CENTRALITY MEASURES
#Returns the top k nodes of G according to the centrality measure "measure"
def top(G,measure,k):
    pq = PriorityQueue()
    cen=measure(G)
    for u in G.nodes():
        pq.put(u, -cen[u])  # We use negative value because PriorityQueue returns first values whose priority value is lower
    out=[]
    for i in range(k):
        out.append(pq.get())
    return out

#The measure associated to each node is exactly its degree
def degree(G):
    cen=dict()
    for i in G.nodes():
        cen[i] = G.degree(i)
    return cen

#The measure associated to each node is the sum of the (shortest) distances of this node from each remaining node
#It is not exavtly the closeness measure, but it returns the same ranking on vertices
def closeness(G):
    cen=dict()

    for u in G.nodes():
        visited=set()
        visited.add(u)
        queue = [u]
        dist = dict()
        dist[u]  = 0
        while queue != []:
            v = queue.pop(0)
            for w in G[v]:
                if w not in visited:
                    queue.append(w)
                    visited.add(w)
                    dist[w] = dist[v] + 1
        cen[u] = sum(dist.values())
    return cen

#The measure associated to each node is its betweenness value
def btw(G):
    return betweenness(G)[1]

if __name__ == '__main__':
    G = nx.Graph()
    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('B', 'C')
    G.add_edge('B', 'D')
    G.add_edge('D', 'E')
    G.add_edge('D', 'F')
    G.add_edge('D', 'G')
    G.add_edge('E', 'F')
    G.add_edge('F', 'G')
    print("CLUSTERING")
    print("Hierarchical")
    hierarchical(G)
    print("Two Means")
    two_means(G)
    print("Girman-Newmann")
    print(girman_newman(G))
    print("Spectral")
    print(spectral(G))
    print("CENTRALITY")
    print("degree")
    print(top(G,degree,3))
    print("closeness")
    print(top(G,closeness,3))
    print("betweenness")
    print(top(G,btw,3))

