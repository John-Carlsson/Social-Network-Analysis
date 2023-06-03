from queue import Queue

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
        u = random.choice(list(self.G.nodes()))
        auction = self.choose_auction_format(t)
        return u, auction

    """
    Getting random auction type
    @:param t = time stamp
    @:return auction type
    """
    def choose_auction_format(self, t):
        if t % 1 == 0:
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
            return False, False

    """
    Method starts the auction in timestamp t and returns revenue of the auction
    @:param t = timestamp
    @:param prob = probability function
    @:param val = value function
    """
    def run(self, t, prob, val):
        bids = {}
        reports = {}
        seller_net = list()
        start_node, auction = self.__init(t)
        start_node_neighbors = self.G.neighbors(start_node)
        reports[start_node] = self.G.neighbors(start_node)
        #start node inviting
        for start_node_neighbor in start_node_neighbors:
            bv, Sv = self.__invite(t, start_node, start_node_neighbor, auction, prob, val)
            if bv != False:
                bids[start_node_neighbor] = bv
                reports[start_node_neighbor] = Sv
                seller_net.append(start_node_neighbor)
        #bidders invites others
        for seller in seller_net:
            seller_reports = reports[seller]
            for report in seller_reports:
                if report not in seller_net:
                    bv, Sv = self.__invite(t, seller, report, auction, prob, val)
                    if bv != False:
                        bids[report] = bv
                        reports[report] = Sv
                        seller_net.append(report)
        return auction(self.k, seller_net, reports, bids)

    """
    Method returns neighbors of vertex v
    @:param v = vertex v
    @:param truthful_reporting = true if reporting is truthful, false if not
    @:return list of neighbors what knows about auction
    """
    def get_neighbors(self, v, truthful_reporting):
        neighbors = list(self.G.neighbors(v))
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
        payments = {}
        allocation = {}
        for seller in seller_net:
            allocation[seller] = False
            payments[seller] = 0

        # allocation
        sorted_bidders = dict(sorted(bids.items(), key=lambda x: x[1], reverse=True))
        sorted_bidders = list(sorted_bidders.items())
        if len(bids) == 0:
            return allocation, payments
        if k < len(bids):
            for i in range(k):
                key, value = sorted_bidders[i]
                allocation[key] = True
                payments[key] = value
        else:
            for i in range(len(bids)):
                key, value = sorted_bidders[i]
                allocation[key] = True
                payments[key] = value

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
