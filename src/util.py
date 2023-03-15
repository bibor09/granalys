import networkx as nx

def find_clusters(dic, all_methods):
    # Create a graph where each set(aka key) is represented by a vertex, and two vertices are connected by an edge if their corresponding sets have at least one common element.
    G = nx.Graph()
    keys = list(dic.keys())
    G.add_nodes_from(keys)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            # If they have at least one common element
            # Or if the element is a class-level method
            if len(dic[keys[i]] & dic[keys[j]]) > 0 or keys[i] in all_methods:
                G.add_edge(keys[i], keys[j])

    print(G.edges)

    for comp in nx.connected_components(G):
        print(comp)
    print(nx.number_connected_components(G))

# To find completely disconnected elements
def find(elements, dic):
    all = set.union(*list(dic.values()))
    print(elements.difference(all))

def put_in_dict(key, value, dict):
    if key not in dict.keys():
        dict[key]= set()
    dict[key].add(value)