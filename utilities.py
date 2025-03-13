# Progetto Artificial Intelligence - Daniele Materia
# script che contiene le funzioni di utilità per la lettura delle istanze e la visualizzazione dei risultati
import networkx as nx
from matplotlib import pyplot as plt

# funzione di parsing per leggere i file di input delle istanze
def parse_instance(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    node_weights = {}
    adjacency_matrix = []
    reading_weights = False
    reading_matrix = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("NODE_WEIGHT_SECTION"):
            reading_weights = True
            continue
        elif line.startswith("ADIACENT_LOWER_TRIANGULAR_MATRIX"):
            reading_weights = False
            reading_matrix = True
            continue
        elif line.startswith("NAME"):
            name = line.split()[1]
            continue
        elif line == "" or line.startswith("TYPE") or line.startswith("COMMENT"):
            continue
        
        if reading_weights:
            node_and_weight = line.split()
            node_weights[int(node_and_weight[0])] = int(node_and_weight[1])
        elif reading_matrix:
            adjacency_matrix.append([int(x) for x in line.split()])
    
    G = nx.Graph()
    for node, weight in node_weights.items():
        G.add_node(node, weight=weight)
    
    for i, row in enumerate(adjacency_matrix):
        for j, value in enumerate(row):
            if value == 1:
                G.add_edge(i + 1, j + 1)
    
    return G, node_weights, name

# funzione per visualizzare un grafo, colorato in base ai pesi dei nodi
def visualize_graph(G, node_weights, name):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title(f"Graph Visualization - Instance {name}")
    pos = nx.kamada_kawai_layout(G) # utilizzo questo layout per avere una visualizzazione ordinata del grafo
    node_colors = [node_weights[n] for n in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=node_colors, cmap=plt.cm.coolwarm,
            edge_color='gray', node_size=500, font_size=10, ax=ax)
    
    plt.tight_layout()
    plt.show()

# funzione per creare il grafico della convergenza lungo le generazioni
def plot_convergence_over_generations(fitness_history, best_fitness, name):
    plt.figure(figsize=(10, 6))
    plt.plot(fitness_history, color='r')
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.yscale("log")
    plt.title(f"Convergence Plot - Instance: {name}")
    plt.annotate(
        f"Best Fitness: {best_fitness}",
        xy=(len(fitness_history), best_fitness), xycoords='data',
        xytext=(-100, 30), textcoords='offset points',
        arrowprops=dict(facecolor='black', arrowstyle="->"),
        fontsize=12, color='b'
    )
    plt.grid(True)

# funzione per visualizzare il grafico della convergenza
def visualize_convergence_over_generations(fitness_history, best_fitness, name):
    plot_convergence_over_generations(fitness_history, best_fitness, name)
    plt.show()

def save_convergence_graph(file_path):
    plt.savefig(file_path, dpi=300, bbox_inches='tight')