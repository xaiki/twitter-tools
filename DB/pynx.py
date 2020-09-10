import networkx as nx
import unicodedata
import logging
import json
import re

from . import generic

hashre = re.compile(r"(#\w+)")
userre = re.compile(r"(@\w+)")


def normalize(input_str):
    return unicodedata.normalize("NFKD", input_str).encode("ASCII", "ignore").lower()


def add_node(G, node, attr={}):
    try:
        G[node]["weight"] += 1
    except KeyError:
        G.add_node(node, weight=1)


def add_edge(G, n, p):
    try:
        G.edges[n, p]["weight"] += 1
    except KeyError:
        G.add_edge(n, p, weight=1)


def add_tags(G, text):
    tags = hashre.findall(text)
    while len(tags) > 1:
        t = normalize(tags.pop())
        add_node(G, t)
        for u in tags:
            u = normalize(u)
            add_node(G, u)
            add_edge(G, t, u)
    return G


def add_users(G, text, status):
    users = set(userre.findall(text))
    if status.in_reply_to_screen_name:
        users.add("@%s" % status.in_reply_to_screen_name)
    try:
        users.append("@%s" % status.retweeted_status.user.screen_name)
    except AttributeError:
        pass
    u = normalize("@%s" % status.user.screen_name)
    add_node(G, u)
    for v in users:
        add_edge(G, u, normalize(v))


class Driver(generic.DB):
    def __init__(self, filename="graph.gexf"):
        generic.DB.__init__(self)

        self.name = "NetworkX DB Driver"
        self.filename = filename
        self.type = filename.split(".")[-1] or "gexf"
        
        self._user_graph = "user-%s" % filename
        self._hash_graph = "hash-%s" % filename
        self._twit_graph = "twit-%s" % filename
        
        self._write = getattr(nx, "write_%s" % self.type)
        self._read = getattr(nx, "read_%s" % self.type)

        self.U = self._open_graph(self._user_graph)
        self.H = self._open_graph(self._hash_graph)
        self.T = self._open_graph(self._twit_graph)
        
        logging.info(f"graphs opened {self.U.nodes()} {self.H.nodes()} {self.T.nodes()}")

    def _open_graph(self, filename):
        try:
            return self._read(filename)
        except IOError:
            return nx.Graph()

    def getTweets(self):
        return [n for n in self.U.nodes()]

    def markDeleted(self, id):
        self.U.nodes[id]["deleted"] = True

    def writeSuccess(self, path):
        logging.warning("NOT IMPLEMENTED")

    def getLogs(self):
        logging.warning("NOT IMPLEMENTED")

    def _write_all(self):
        self._write(self.H, self._hash_graph)
        self._write(self.U, self._user_graph)

    def close(self):
        self._write_all()

    def saveTweet(self, url, status):
        try:
            text = status.extended_tweet.text
        except AttributeError:
            text = status.text

        add_tags(self.H, text)
        add_users(self.U, text, status)
        logging.info(f"H, {self.H.nodes()}")
        self._write_all()


if __name__ == "__main__":
    G = nx.Graph()
    add_users(G, "RT @test blah blah #gnu @other", {})
