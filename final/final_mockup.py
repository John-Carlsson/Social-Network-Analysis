import networkx as nx
import random

class SocNetMec:
    
    def __init__(self, G, T, k):
        self.G = G
        self.T = T
        self.k = k

    #MOCK-UP IMPLEMENTATION: It assigns the item to the first k bidders and assigns payment 0 to every node
    def __mock_auction(self, k, seller_net, reports, bids):
        allocation = dict()
        payment = dict()
        count = 0
        for i in bids.keys():
            if count < k:
                allocation[i] = True
            else:
                allocation[i] = False
            payment[i] = 0

    """
    Method returns random vertex of the graph and random auction model
    @:param t = time stamp
    @:return u = random vertex
    @:return auction = random type of the auction
    """
    def __init(self, t):
        u = random.choice(list(G.nodes()))
        auction = self.choose_auction_format(t)
        return u, auction

    """
    Getting random auction type
    @:param t = time stamp
    @:return auction type
    """
    def choose_auction_format(self, t):
        if t % 3 == 0:
            return self.vcg_auction
        elif t % 3 == 1:
            return self.mudan_auction
        else:
            return self.mudar_auction

    """
    Method invites next vertex, if vertex is invited then returns the bid and neighbors
    @:param t = timestamp
    @:param u = vertex u
    @:param v = vertex v
    @:param auction = auction type 
    @:param prob = probability method of connection
    @:param val = valuation method generating the bid
    @:return bv = bit of v
    @:return Sv = neighbors of v who knows about auction
    """
    def __invite(self, t, u, v, auction, prob, val):
        if prob(u,v):
            truthful_val = val(t, v)
            bv = truthful_val if auction == self.vcg_auction else random.uniform(2 / 3 * truthful_val, truthful_val)
            Sv = self.get_neighbors(v, auction == self.vcg_auction)
            return bv, Sv
        else:
            return False

    #NOT IMPLEMENTED. It simply adds to the revenue a random integer
    def run(self, t, prob, val):
        return random.randint(1, 10)

    """
    Method returns neighbors of vertex v
    @:param v = vertex v
    @:param truthful_reporting = true if reporting is truthful, false if not
    @:return list of neighbors what knows about auction
    """
    def get_neighbors(self, v, truthful_reporting):
        neighbors = list(G.neighbors(v))
        if truthful_reporting:
            return neighbors
        else:
            reports = list()
            for neighbor in neighbors:
                if self.random_boolean(0.15):
                    reports.append(neighbor)
        return reports
    """
    Method returns true or false with probability
    @:param probability = probability of true
    @:return true or false
    """
    def random_boolean(self, probability):
        return random.choices([True, False], [probability, 1 - probability])

    def vcg_auction(self, k, seller_net, reports, bids):
        # Step 1: Calculate Payments
        payments = {}
        externalities = {}
        for bidder in seller_net:
            bids_except_bidder = {key: bids[key] for key in bids if key != bidder}
            sorted_bids_except_bidder = sorted(bids_except_bidder, key=bids_except_bidder.get, reverse=True)
            if bidder in sorted_bids_except_bidder[:k]:
                allocated_bidder = sorted_bids_except_bidder[:k].index(bidder)
                payment = sum(bids_except_bidder[key] for key in sorted_bids_except_bidder[:k]) - allocated_bidder
                payments[bidder] = payment
                externalities[bidder] = sum(bids_except_bidder[key] for key in sorted_bids_except_bidder[k:]) - k

        # Step 2: Calculate Allocation
        allocation = {bidder: bidder in sorted_bids_except_bidder[:k] for bidder in seller_net}

        # Step 3: Apply Neighbor Externalities
        for bidder, neighbor_bidders in reports.items():
            for neighbor_bidder in neighbor_bidders:
                if neighbor_bidder in externalities:
                    payments[bidder] += externalities[neighbor_bidder]

        return allocation, payments

    def mudan_auction(self, k, seller_net, reports, bids):
        # Step 1: Calculate Payments
        payments = {}
        externalities = {}
        for bidder in seller_net:
            bids_except_bidder = {key: bids[key] for key in bids if key != bidder}
            sorted_bids_except_bidder = sorted(bids_except_bidder, key=bids_except_bidder.get, reverse=True)
            if bidder in sorted_bids_except_bidder[:k]:
                payment = sum(bids_except_bidder[key] for key in sorted_bids_except_bidder[:k])
                payments[bidder] = payment
                externalities[bidder] = sum(bids_except_bidder[key] for key in sorted_bids_except_bidder[k:]) - k

        # Step 2: Calculate Allocation
        allocation = {bidder: bidder in sorted_bids_except_bidder[:k] for bidder in seller_net}

        # Step 3: Apply Neighbor Externalities
        for bidder, neighbor_bidders in reports.items():
            for neighbor_bidder in neighbor_bidders:
                if neighbor_bidder in externalities:
                    payments[bidder] += externalities[neighbor_bidder]

        return allocation, payments

    def mudar_auction(self, k, seller_net, reports, bids):
        # Step 1: Calculate Random Allocation
        allocation = {bidder: False for bidder in seller_net}
        allocated_bidders = random.sample(seller_net, min(k, len(seller_net)))
        for bidder in allocated_bidders:
            allocation[bidder] = True

        # Step 2: Calculate Random Payments
        payments = {bidder: -bids[bidder] if allocation[bidder] else 0 for bidder in seller_net}

        # Step 3: Apply Neighbor Externalities

        return allocation, payments

"""
Loading of graph
:param: file is name of the file
"""
def load_graph(file):
    G = nx.Graph()
    with open(file, 'r') as f:
        for s in f.readlines():
            G.add_edge(s.split()[0], s.split()[1])
    return G



if __name__ == '__main__':
    G = load_graph('net_3')
    print(G)
    print(len(G.nodes))
