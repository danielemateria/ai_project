# Progetto Artificial Intelligence - Daniele Materia
import utilities as utl
import networkx as nx
import random
import pandas as pd
import time
import sys
import math
GEN_NUM = 250

fitness_evaluations = 0  # Variabile globale per contare le valutazioni della funzione obiettivo
fitness_cache = {} # Cache per memorizzare le fitness degli individui

def initialize_population(G: nx.Graph, pop_size):
    population = []
    nodes = tuple(G.nodes)
    
    for _ in range(pop_size):
        remaining_nodes = set(nodes)
        removed_nodes = set()

        while True:
            subgraph = G.subgraph(remaining_nodes)
            try:
                cycle_edges = nx.find_cycle(subgraph)
                cycle_nodes = [u for (u, _) in cycle_edges]
                # rimuovo un nodo casuale dal ciclo
                node_to_remove = random.choice(cycle_nodes)

                remaining_nodes.remove(node_to_remove)
                removed_nodes.add(node_to_remove)
            except nx.NetworkXNoCycle: # se scatta l'eccezione, allora non ci sono più cicli nel grafo ed esci dal loop
                break
        
        population.append(removed_nodes)
    return population

def fitness(G: nx.Graph, individual, node_weights): # funzione di fitness, assegno una penalità dinamica in base al numero di cicli presenti nel grafo G - individual
    global fitness_evaluations
    key = frozenset(individual)
    if key in fitness_cache: # se il valore di fitness per un determinato individuo è già presente in cache, lo ritorno direttamente senza ricalcolarlo 
        return fitness_cache[key]
    
    fitness_evaluations += 1
    num_cycles = len(nx.cycle_basis(G.subgraph(G.nodes - individual))) # conto il numero di cicli nel grafo G - individual
    value = sum(node_weights[v] for v in individual) + (10**4) * num_cycles # il valore di fitness è dato dalla somma dei pesi dei nodi della soluzione + l'eventuale penalità
    fitness_cache[key] = value # salvo il valore in cache per non doverlo ricalcolare in futuro per lo stesso individuo
    return value

def selection(pop_with_fitness, k=5, p=0.7):
    candidates = random.sample(pop_with_fitness, k)
    candidates.sort(key=lambda x: x[1])  # Ordino i candidati per valore di fitness
    if random.random() < p:
        return candidates[0][0]  # Migliore individuo tra i 5
    else:
        return candidates[random.randint(1, len(candidates)-1)][0]  # Un altro individuo con probabilità (1-p)

def crossover(parent1: set, parent2: set):
    common = parent1.intersection(parent2) # intersezione dei vertici dei genitori
    diff = list(parent1.symmetric_difference(parent2)) # differenza simmetrica dei vertici dei genitori
    return common.union(set(diff[:len(diff)//2])) # restituisco l'unione tra common e la prima metà di diff

def flip_node(node_to_flip, individual: set):
    if node_to_flip in individual:
        individual.remove(node_to_flip)
    else:
        individual.add(node_to_flip)
    return individual

def mutation(child, G: nx.Graph, mutation_rate):
    # rimuovo o aggiungo un vertice scelto in maniera casuale, con probabilità mutation_rate
    if random.random() < mutation_rate:
        node = random.choice(tuple(G.nodes))
        child = flip_node(node, child)
    return child

def tabu_search(G: nx.Graph, individual, node_weights, max_iterations=10):
    tabu_list_size = max(5, math.ceil(len(G.nodes) ** 0.4))  # dimensione tabu list variabile, cresce all'aumentare del numero di vertici del grafo
    current_individual = individual.copy()  # soluzione corrente
    best_individual = current_individual.copy()  # migliore soluzione trovata
    best_fitness = fitness(G, best_individual, node_weights) # fitness della migliore soluzione trovata
    tabu_list = []

    initial_graph_nodes = tuple(G.nodes)
    
    for _ in range(max_iterations):
        best_candidate = None # migliore candidato
        best_candidate_fitness = float('inf') # fitness del migliore candidato

        # scelgo un vicinato casuale di dimensione uguale al 5% dei nodi del grafo
        neighborhood = random.sample(initial_graph_nodes, math.ceil(len(G.nodes) * 0.05))
        for node_to_flip in neighborhood:
            if current_individual is None:
                break
            new_candidate = flip_node(node_to_flip, current_individual.copy()) # flip del nodo
            if new_candidate in tabu_list: # se la mossa è tabù, la salto
                continue
            
            new_fitness = fitness(G, new_candidate, node_weights) # calcolo la fitness del nuovo individuo
            if new_fitness < best_candidate_fitness: # se la fitness è la migliore trovata finora (nel vicinato), aggiorno il miglior candidato
                best_candidate = new_candidate
                best_candidate_fitness = new_fitness

        # Se non ho trovato nessun miglior candidato, esco dal ciclo
        if best_candidate is None:
            break

        current_individual = best_candidate

        # se il miglior candidato ha una fitness migliore della migliore soluzione trovata finora, aggiorno la migliore soluzione
        if best_candidate_fitness < best_fitness:
            best_individual, best_fitness = best_candidate, best_candidate_fitness

        # aggiornamento della tabu list
        tabu_list.append(best_candidate)
        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)  # rimuovo il primo elemento inserito nella tabu list per mantenere la dimensione costante
    
    return best_individual, best_fitness

def hga(G: nx.Graph, node_weights, pop_size=25, generations=GEN_NUM):
    global fitness_evaluations
    fitness_evaluations = 0
    population = initialize_population(G, pop_size)
    mutation_rate = 0.005
    # array di appoggio che servono a plottare l'andamento della fitness e a calcolare la media delle chiamate alla fitness function
    fitness_history = []
    evaluation_counts = []

    # calcolo la fitness per tutti gli individui della popolazione
    pop_with_fitness = [(ind, fitness(G, ind, node_weights)) for ind in population]

    for gen in range(generations):
        print(f"Generation: {gen + 1}/{generations}", end="\r")
        new_population = []
        for _ in range(pop_size):
            # seleziono i due parent
            parent1, parent2 = selection(pop_with_fitness), selection(pop_with_fitness)
            # creo il child tramite crossover, lo faccio mutare e ne miglioro la qualità con tabu search
            child = crossover(parent1, parent2)
            child = mutation(child, G, mutation_rate)
            child, child_fitness = tabu_search(G, child, node_weights)
            new_population.append((child, child_fitness))
        
        # estendo la popolazione coi nuovi individui
        pop_with_fitness.extend(new_population)
        # rioridno la popolazione in base alla fitness e tengo solo i migliori pop_size individui
        pop_with_fitness.sort(key=lambda x: x[1])
        pop_with_fitness = pop_with_fitness[:pop_size]

        best_fitness_gen = pop_with_fitness[0][1]
        fitness_history.append(best_fitness_gen)
        evaluation_counts.append(fitness_evaluations)

    # ritorno il miglior individuo, la sua fitness e l'andamento della fitness durante le generazioni
    best_solution, best_fitness = pop_with_fitness[0]
    avg_evaluations = int(sum(evaluation_counts) / len(evaluation_counts))
    return best_solution, best_fitness, fitness_history, avg_evaluations

if __name__ == "__main__":
    instances_file_path = sys.argv[1] # percorso file cartella istanze
    save_results = sys.argv[2] # se vale "y" salva i risultati

    G, node_weights, name = utl.parse_instance(instances_file_path)
    start_time = time.perf_counter() # conta il tempo di esecuzione
    best_solution, best_fitness, fitness_history, evaluations = hga(G, node_weights)
    execution_time = time.perf_counter() - start_time
    G.remove_nodes_from(best_solution)

    print("Best Solution:", best_solution)
    print("Best Fitness:", best_fitness)
    print(f"Execution time: {execution_time:.2f} seconds")

    if save_results == "y":
        results_file_path = "./results.csv"
        data = pd.read_csv(results_file_path)
        data = pd.concat([
            data,
            pd.DataFrame({
                "instance_name": [name],
                "best_fitness": [best_fitness],
                "fitness_evaluations": [evaluations],
                "generations": [GEN_NUM],
                "execution_time": [execution_time]
            })
        ], ignore_index=True)
        last_id_data = data.index[-1]
        data.to_csv(results_file_path, index=False)
        # Salva il plot dell'andamento della fitness durante le generazioni
        utl.plot_convergence_over_generations(fitness_history, best_fitness, name)
        plot_file_name = "./plots/" + f"{last_id_data}_{name}_convergence.png"
        utl.save_convergence_graph(plot_file_name)
    else:
        # Visualizzazione del grafo con la soluzione migliore trovata
        utl.visualize_graph(G, node_weights, f"{name} - Grafo Aciclico Trovato")

        # Mostra il grafico della convergenza
        utl.visualize_convergence_over_generations(fitness_history, best_fitness, name)