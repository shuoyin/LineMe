#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:53
import json
import random
from collections import Counter

import networkx as nx
from django.db.models import Count, Q

from friendnet.models import GroupMember
from friendnet.models import Link


class Graph:
    def __init__(self, user, group):
        self.G = nx.Graph()
        self.user = user
        self.group = group
        self.me = self.myself()

    def myself(self):
        return GroupMember.objects.get(
            group=self.group,
            user=self.user,
            is_joined=True
        )

    def ego_builder(self):

        links = Link.objects.filter(
            group=self.group,
            creator=self.user
        )

        self.G.add_node(self.me, creator=True, group=0)

        for link in links:
            self.G.add_edge(link.source_member,
                            link.target_member,
                            id=link.id,
                            status=link.status,
                            weight=1)

        for node in self.G.nodes():
            if node != self.me:
                self.G.node[node]['group'] = random.randint(1, 4)

        return self

    def global_builder(self, color=False):

        links = Link.objects.filter(
            group=self.group,
            status=3
        )

        members = GroupMember.objects.filter(group=self.group).exclude(user=self.user)

        self.G.add_node(self.me, creator=True)
        for member in members:
            self.G.add_node(member, creator=False, group=random.randint(1, 4))

        for link in links:
            if not self.G.has_edge(link.source_member, link.target_member):
                if link.creator == self.user:
                    self.G.add_edge(link.source_member, link.target_member, id=link.id, weight=1, status=True)
                else:
                    self.G.add_edge(link.source_member, link.target_member, id=link.id, weight=1, status=False)
            else:
                if link.creator == self.user:
                    self.G[link.source_member][link.target_member]['weight'] += 1
                    self.G[link.source_member][link.target_member]['status'] = True
                else:
                    self.G[link.source_member][link.target_member]['weight'] += 1

        if color:
            group_color = GraphAnalyzer(self.G).graph_communities()
            for node in self.G.nodes():
                if node in group_color:
                    self.G.node[node]['group'] = group_color[node]
                else:
                    self.G.node[node]['group'] = 9

        return self

    def bingo(self):
        return self.G

    def dictify(self):

        nodes, links = [], []

        nodes.append({'id': self.me.id,
                      'userid': self.user.id,
                      'name': self.me.member_name,
                      'self': True,
                      'group': 0})

        for node, d in self.G.nodes(data='group'):
            if node != self.me:
                nodes.append({'id': node.id,
                              'userid': (-1 if node.user is None else node.user.id),
                              'name': node.member_name,
                              'self': False,
                              'group': d['group']})

        for (s, t, d) in self.G.edges(data=True):
            links.append({'id': d['id'],
                          'source': s.id,
                          'target': t.id,
                          'status': d['status'],
                          'value': d['weight']})

        return {"nodes": nodes, "links": links}

    def jsonify(self):
        return json.dumps(self.dictify())


class GraphAnalyzer:
    def __init__(self, G):
        self.G = G

    def graph_communities(self):
        communities = nx.k_clique_communities(self.G, 3)
        communities_index = {}
        for i, group in enumerate(communities):
            for member in group:
                communities_index[member] = i + 1

        return communities_index


def create_global_graph(nodes, links, user):
    G = nx.Graph()

    # Todo: all members are calculated as nodes or only linked member are nodes
    for node in nodes:
        G.add_node(node)

    for link in links:
        if not G.has_edge(link.source_member, link.target_member):
            if link.creator == user:
                G.add_edge(link.source_member, link.target_member, weight=1, created=True)
            else:
                G.add_edge(link.source_member, link.target_member, weight=1)
        else:
            if link.creator == user:
                G[link.source_member][link.target_member]['weight'] += 1
                G[link.source_member][link.target_member]['created'] = True
            else:
                G[link.source_member][link.target_member]['weight'] += 1

    return G


# def graph_communities(G):
#     a = nx.k_clique_communities(G, 3)
#     group_index = {}
#     for i, g in enumerate(a):
#         for m in g:
#             group_index[m] = i + 1
#
#     return group_index


# Todo: link status should be 3
# Todo: most contributor ? get most credits
def graph_analyzer(user, groupid):
    nodes = GroupMember.objects.filter(group__id=groupid)
    links = Link.objects.filter(group__id=groupid, status=3)
    my_member = nodes.get(user=user)

    G = create_global_graph(nodes, links, user)

    # print my_member

    # print G.edges(data=True)

    distribution = {k: v / float(G.number_of_nodes()) for k, v in dict(Counter(G.degree().values())).items()}

    # print distribution, dict(Counter(G.degree().values()))

    # distribution = {str(k): v for k, v in nx.degree_centrality(G)}

    top = sorted(G.degree().items(), key=lambda x: x[1], reverse=True)
    top3 = top[0:3]

    myRank = top.index((my_member, G.degree(my_member))) + 1

    # print top3, myRank

    myGraph = links.filter(creator=user).count()

    cover = myGraph / float(G.number_of_edges()) if not G.number_of_edges() == 0 else 0

    # print cover

    # Todo: fix 0.00 ??
    average_degree = 2.0 * G.number_of_edges() / G.number_of_nodes()

    # If the network is not connected,
    # return -1

    # Todo: warning, when the net is big, maybe slow
    if nx.is_connected(G) and G.number_of_nodes() > 1:
        average_distance = nx.average_shortest_path_length(G)
    else:
        average_distance = -1

    # print average_degree, average_distance

    friends = G.neighbors(my_member)
    friends = [(friend, G[friend][my_member]['weight']) for friend in friends]
    friends = sorted(friends, key=lambda x: x[1], reverse=True)

    # print friends
    # print friends[0][0].id
    if len(friends) > 0:
        bestfriend = friends[0][0]
        bf_ratio = friends[0][1] / float(G.number_of_nodes())
    else:
        bestfriend = None
        bf_ratio = 0

    # Todo: ratio not correct fixed...
    links_of_me = links\
        .filter(Q(source_member=my_member) | Q(target_member=my_member), group__id=groupid)\
        .exclude(creator=user) \
        .values('creator').annotate(count=Count('pk')).order_by('-count')

    # print links_of_me
    if len(links_of_me) != 0:
        heart = GroupMember.objects.get(user__id=links_of_me[0]['creator'], group__id=groupid)
        heart_count = links_of_me[0]['count']
    else:
        heart = None
        heart_count = None

    return {'distribution': json.dumps(distribution),
            'top3': top3,
            'my_rank': myRank,
            'average_degree': average_degree,
            'average_distance': average_distance,
            'cover': round(cover*100, 2),
            'bestfriend': bestfriend,
            'bf_ratio': round(bf_ratio*100, 2),
            'heart': heart,
            'heart_count': heart_count}
