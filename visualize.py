import matplotlib.pyplot as plt
import networkx as nx
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} graphML")
else:
    G = nx.read_graphml(sys.argv[1])

    names = nx.get_node_attributes(G, "name")
    labels = {key: [value] for key, value in names.items()}
    ids = nx.get_node_attributes(G, "id")
    # depth = nx.get_node_attributes(G, "depth")
    values = nx.get_node_attributes(G, "value")
    linenos = nx.get_node_attributes(G, "lineno")

    for key, value in names.items():
        if key in ids.keys():
            labels[key].append(ids[key])
        if key in values.keys():
            labels[key].append(values[key])
        # if key in depth.keys():
        #     labels[key].append(depth[key])
        # if key in linenos.keys():
        #     labels[key].append(linenos[key])
            
    plt.figure(figsize=(200,200))
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    nx.draw(G, pos=pos, node_color="#ffaa00",labels=labels, with_labels=True, node_size=1000,font_size=5)
    plt.show()