import networkx as nx

def count_connected_components(pot_rel_methods, all_methods):
    # Create a graph where each set(aka key) is represented by a vertex, and two vertices are connected by an edge if their corresponding sets have at least one common element.
    G = nx.Graph()
    keys = list(pot_rel_methods.keys())
    G.add_nodes_from(keys)

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            # If they have at least one common element or the element is a class-level method
            if len(pot_rel_methods[keys[i]] & pot_rel_methods[keys[j]]) > 0 or keys[i] in all_methods:
                G.add_edge(keys[i], keys[j])

    # for comp in nx.connected_components(G):
    #     print("CONNECTED COMP", comp)
    return nx.number_connected_components(G)

# To find completely disconnected elements, which are automatically non-related 
def find_non_related_methods(all_methods, pot_rel_methods):
    pot_rel_m = set(pot_rel_methods.keys())
    all_m = set(all_methods)
    return all_m.difference(pot_rel_m)

def put_in_dict(key, value, dict):
    if key not in dict.keys():
        dict[key]= set()
    dict[key].add(value)