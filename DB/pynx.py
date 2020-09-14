import networkx as nx
import unicodedata
import logging
import json
import re
import os

from . import generic
from . import utils

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
    for i, t in enumerate(tags):
        n = normalize(t)
        add_node(G, n)
        for u in tags[i:]:
            u = normalize(u)
            add_node(G, u)
            add_edge(G, t, u)
    return tags

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

        self.type = filename.split(".")[-1] or "gexf"
        if self.type == 'pynx': # this is for test handeling
            self.type = "gexf"
            filename.replace('pynx', 'gexf')

        self.filename = filename
        
        self.open()
        
    def open(self):
        self._user_graph = "user-%s" % self.filename
        self._hash_graph = "hash-%s" % self.filename
        self._twit_graph = "twit-%s" % self.filename
        
        self._write = getattr(nx, "write_%s" % self.type)
        self._read = getattr(nx, "read_%s" % self.type)

        self.U = self._open_graph(self._user_graph)
        self.H = self._open_graph(self._hash_graph)
        self.T = self._open_graph(self._twit_graph)
        
        logging.info(f"graphs opened {self.U.nodes()} {self.H.nodes()} {self.T.nodes()}")

    def _WIPE(self):
        self.close()
        
        os.remove(self._user_graph)
        os.remove(self._hash_graph)
        os.remove(self._twit_graph)

        self.open()
        
    def _open_graph(self, filename):
        try:
            return self._read(filename)
        except IOError:
            return nx.Graph()

    def getTweets(self):
        return [n for n in self.U.nodes()]

#    def getAuthor(self, screen_name):
#        u = normalize("@%s" % screen_name)
#        return self.U.neighbors(u)
    
    def markDeleted(self, id):
        nx.set_node_attributes(self.U, {id: {"deleted": True}})

    def _write_all(self):
        self._write(self.H, self._hash_graph)
        self._write(self.U, self._user_graph)
        self._write(self.T, self._twit_graph)

    def close(self):
        self._write_all()

    def saveTweet(self, status):
        text = utils.extract_text(status)

        add_tags(self.H, text)
        add_users(self.U, text, status)
        
        logging.info(f"H, {self.H.nodes()}")
        self._write_all()

    def saveAuthor(self, user):
        u = normalize("@%s" % user.screen_name)
        add_node(self.U, u)
        nx.set_node_attributes(self.U, {u: {'id': user.id, 'created_at': user.created_at.isoformat()}})

        self._write_all()

if __name__ == "__main__":
    G = nx.Graph()
    add_users(G, "RT @test blah blah #gnu @other", {})
