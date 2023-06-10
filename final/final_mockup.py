import itertools
from queue import Queue
from typing import Dict

import networkx as nx
import random

class SocNetMec:
    PAYING_FOR_REPORT = 5
    
    def __init__(self, G, T, k):
        self.G = G
        self.T = T
        self.k = k
        self.SortedArray = []

    def __mock_auction(self, k, seller_net, reports, bids):
        allocation = dict()
        payment = dict()
        count = 0
        # allocation
        sorted_bidders = dict(sorted(bids.items(), key=lambda x: x[1], reverse=True))
        sorted_bidders = list(sorted_bidders.items())
        if len(bids) == 0:
            return allocation, payment
        if k < len(bids):
            for i in range(k):
                key, value = sorted_bidders[i]
                allocation[key] = True
                payment[key] = value
        else:
            for i in range(len(bids)):
                key, value = sorted_bidders[i]
                allocation[key] = True
                payment[key] = value
        for i in bids.keys():
            if count < k:
                allocation[i] = True
            else:
                allocation[i] = False
            payment[i] = 0

        return allocation, payment

    """
    Method returns random vertex of the graph and random auction model
    @:param t = time stamp
    @:return u = random vertex
    @:return auction = random type of the auction
    """
    def __init(self, t):
        u = self.SortedArray[t]
        auction = self.choose_auction_format(t)
        return u, auction

    """
    Method sort nodes by its degree
    """
    def sorted_by_degree(self):
        degrees = dict(self.G.degree())

        # Sort nodes based on degree in descending order
        sorted_nodes = sorted(degrees, key=degrees.get, reverse=True)
        self.SortedArray = sorted_nodes

    """
    Method sort nodes by its centrality
    """
    def sorted_by_centrality(self):
        # Calculate the degree centrality of each node
        degree_centrality = nx.degree_centrality(self.G)

        # Sort nodes based on degree centrality in descending order
        sorted_nodes = sorted(degree_centrality, key=degree_centrality.get, reverse=True)
        self.SortedArray = sorted_nodes

    """
    Method sort nodes by its degree and centrality
    """
    def sorted_by_degree_and_centrality(self):
        centrality = nx.degree_centrality(self.G)
        degrees = dict(self.G.degree())
        degree_and_centrality = dict()
        for key in centrality:
            degree_and_centrality[key] = centrality[key] * degrees[key]

        sorted_degree_and_centrality = {k: v for k, v in sorted(degree_and_centrality.items(), key=lambda item: item[1], reverse=True)}
        self.SortedArray = list(sorted_degree_and_centrality.keys())


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
            return False, False

    """
    Method starts the auction in timestamp t and returns revenue of the auction
    @:param t = timestamp
    @:param prob = probability function
    @:param val = value function
    """
    def run(self, t, prob, val):
        bids = {}
        reports: Dict[str, list] = {}
        neighbors = {}
        seller_net = list()
        start_node, auction = self.__init(t)
        start_node_neighbors = self.G.neighbors(start_node)
        neighbors[start_node] = self.G.neighbors(start_node)
        reports[start_node] = []
        #start node inviting
        for start_node_neighbor in start_node_neighbors:
            bv, Sv = self.__invite(t, start_node, start_node_neighbor, auction, prob, val)
            if bv != False:
                reports[start_node].append(start_node_neighbor)
                bids[start_node_neighbor] = bv
                neighbors[start_node_neighbor] = Sv
                seller_net.append(start_node_neighbor)
        #bidders invites others
        for seller in seller_net:
            seller_reports = neighbors[seller]
            reports[seller] = []
            for report in seller_reports:
                if report not in seller_net:
                    bv, Sv = self.__invite(t, seller, report, auction, prob, val)
                    if bv != False:
                        reports[seller].append(report)
                        bids[report] = bv
                        neighbors[report] = Sv
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

    """
    Run the VCG auction algorithm
    :param k: is the number of item to sell
    :param seller_net: is a set of strings each identifying a different bidder
    :param reports: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are sets of strings representing the set of bidders to which the bidder identified by the
    key reports the information about the auction
    :param bids: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are numbers defining the bid of the bidder identified by that key
    :return: allocation = true if bidder has product false if not and payment = the value of the revenue from the buyer
    """
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

        # bfs - measuring distance
        start = next(iter(reports))
        distance = {}
        for seller in seller_net:
            distance[seller] = -1
        queue = Queue()
        distance[start] = 0
        queue.put(start)
        while len(queue.queue) > 0:
            vertex = queue.get()
            link = reports[vertex]
            for l in link:
                if distance[l] == -1:
                    distance[l] = distance[vertex] + 1
                    queue.put(l)

        for payment in payments:
            payments[payment] = payments[payment] - distance[payment] * self.PAYING_FOR_REPORT

        return allocation, payments

    """
    Run the MUDAN auction algorithm.
    :param k: is the number of item to sell
    :param seller_net: is a set of strings each identifying a different bidder
    :param reports: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are sets of strings representing the set of bidders to which the bidder identified by the
    key reports the information about the auction
    :param bids: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are numbers defining the bid of the bidder identified by that key
    :return: allocation = true if bidder has product false if not and payment = the value of the revenue from the buyer
    """
    def mudan_auction(self, k, seller_net, reports, bids):

        payments = {}
        allocation = {}
        for seller in seller_net:
            allocation[seller] = False
            payments[seller] = 0

        sorted_bidders = sorted(bids.items(), key=lambda x: x[1], reverse=True)

        if len(bids) == 0:
            return allocation, payments
        if k < len(bids):
            winning_bidders = sorted_bidders[:k]
        else:
            winning_bidders = sorted_bidders[:len(bids)]

        clearing_price = winning_bidders[-1][1]

        for key in winning_bidders:
            allocation[key[0]] = True
            payments[key[0]] = clearing_price

        return allocation, payments

    """
    The mudar - Multi-Unit Double Auction for Real-Time trading auction implementation
    :param k: is the number of item to sell
    :param seller_net: is a set of strings each identifying a different bidder
    :param reports: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are sets of strings representing the set of bidders to which the bidder identified by the
    key reports the information about the auction
    :param bids: is a dictionary whose keys are strings each identifying a different bidder and whose
    values are numbers defining the bid of the bidder identified by that key 
    :return: allocation = true if bidder has product false if not and payment = the value of the revenue from the buyer
    """
    def mudar_auction(self, k, seller_net, reports, bids):
        # Step 1: Find the k highest bidders
        highest_bidders = sorted(bids, key=bids.get, reverse=True)[:k]

        # Step 2: Calculate the clearing price
        if len(highest_bidders) > 0:
            clearing_price = bids[highest_bidders[-1]]
        else:
            clearing_price = 0

        # Step 3: Allocate items and calculate payments
        allocation = {bidder: bidder in highest_bidders for bidder in bids}
        payments = {bidder: bids[bidder] - clearing_price if bidder in highest_bidders else 0 for bidder in bids}

        return allocation, payments
