import matplotlib.pyplot as plt
import networkx as nx
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} graphML")
else:
    G = nx.read_graphml(sys.argv[1])

    labelVs = nx.get_node_attributes(G, "labelV")
    labels = {key: [value] for key, value in labelVs.items()}
    ids = nx.get_node_attributes(G, "id")
    depth = nx.get_node_attributes(G, "depth")
    values = nx.get_node_attributes(G, "value")

    for key, value in labelVs.items():
        if key in ids.keys():
            labels[key].append(ids[key])
        if key in values.keys():
            labels[key].append(values[key])
        if key in depth.keys():
            labels[key].append(depth[key])
            
    plt.figure(figsize=(100,100))
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    nx.draw(G, pos=pos, node_color="#ffaa00",node_size=4000,labels=labels,font_size=9)
    plt.show()