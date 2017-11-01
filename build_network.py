# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 15:53:30 2017

@author: fmoret
"""

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

G.add_nodes_from(range(10))

edges = [(0,5),(1,6),(2,7),(3,8),(4,9)]
G.add_edges_from(edges)

nx.draw(G)
#nx.draw_random(G)
#nx.draw_circular(G)
#nx.draw_spectral(G)

plt.show()