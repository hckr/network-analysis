import sys
from operator import itemgetter
from os import makedirs
from os.path import dirname, join
from pprint import pprint
from random import randrange
from typing import List

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph

matplotlib.use('agg')  # headless matplotlib

CURRENT_DIR = dirname(__file__)
RESULTS_OUTPUT_DIR = join(CURRENT_DIR, 'output', 'results')


def main():
    input_graph_ws = nx.read_gml(join(CURRENT_DIR, 'output', 'ws.gml'))
    input_graph_ws_small = nx.read_gml(join(CURRENT_DIR, 'output', 'ws_small.gml'))

    experiments = [
        ('ws_small_seed_5_threshold_10',
         input_graph_ws_small,
         {
             'seed': 5,
             'threshold': 10
         }),
        ('ws_small_seed_5_threshold_30',
         input_graph_ws_small,
         {
             'seed': 5,
             'threshold': 30
         }),
        ('ws_small_seed_10_threshold_10',
         input_graph_ws_small,
         {
             'seed': 10,
             'threshold': 10
         }),
        ('ws_small_seed_10_threshold_30',
         input_graph_ws_small,
         {
             'seed': 10,
             'threshold': 30
         }),
        ('ws_seed_5_threshold_10',
         input_graph_ws,
         {
             'seed': 5,
             'threshold': 10
         }),
        ('ws_seed_5_threshold_30',
         input_graph_ws,
         {
             'seed': 5,
             'threshold': 30
         }),
        ('ws_seed_10_threshold_10',
         input_graph_ws,
         {
             'seed': 10,
             'threshold': 10
         }),
        ('ws_seed_10_threshold_30',
         input_graph_ws,
         {
             'seed': 10,
             'threshold': 30
         }),
    ]

    for experiment_name, input_graph, values in experiments:

        print(f'Running experiment {experiment_name}... ', file=sys.stderr, end='', flush=True)

        graph = initial_seed(input_graph, values['seed'])

        save_graph(graph, experiment_name, 'initial_seeded')

        iteration = 0
        active_counts = [count_active(graph)]

        save_graph_image(graph, experiment_name, iteration)

        while True:
            iteration += 1

            new_graph, changes = update_step(graph, values['threshold'])

            graph = new_graph

            active_counts.append(count_active(graph))

            save_graph_image(graph, experiment_name, iteration)

            if not changes:
                break

        save_counts_plot(active_counts, experiment_name)
        save_counts_file(active_counts, experiment_name)

        print(f'done.', file=sys.stderr)


def initial_seed(graph: Graph, seed_percent: int):
    new_graph = graph.copy()
    seeded = 0
    nodes_count = new_graph.number_of_nodes()
    seed_target = int(nodes_count * seed_percent / 100)
    while seeded < seed_target:
        n = str(randrange(nodes_count))
        node = new_graph.nodes[n]
        if node.get('active', False) is False:
            node['active'] = True
            seeded += 1
    return new_graph


def update_step(graph: Graph, linear_threshold_percent: int):
    changes = False

    new_graph = graph.copy()
    for n in graph.nodes:
        if graph.nodes[n].get('active', False) is False:
            neighbors = list(graph.neighbors(n))
            active_neighbors = list(
                filter(lambda n: graph.nodes[n].get('active', False), neighbors))
            if len(active_neighbors) / len(neighbors) >= linear_threshold_percent / 100:
                new_graph.nodes[n]['active'] = True
                changes = True

    return new_graph, changes


def get_colors(graph: Graph):
    return [('red' if graph.nodes[n].get('active', False) else 'blue')
            for n in graph.nodes]


def count_active(graph: Graph):
    return len(list(map(itemgetter(0), filter(itemgetter(1), graph.nodes(data='active')))))


def save_graph(graph: Graph, experiment_name: str, name: str):
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    nx.write_gml(graph, join(output_dir, f'{name}.gml'))


def save_graph_image(graph: Graph, experiment_name: str, step: int):
    plt.figure(figsize=(12, 12))
    nx.draw_shell(graph, with_labels=True, font_size=8, node_color=get_colors(graph))
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name, 'steps')
    makedirs(output_dir, exist_ok=True)
    plt.savefig(join(output_dir, f'step_{step}.svg'), format='SVG')
    plt.close()


def save_counts_plot(counts: List[int], experiment_name: str):
    plt.figure(figsize=(7, 7))
    plt.plot(counts)
    plt.xlabel('Iteration')
    plt.xticks(list(range(len(counts))))
    plt.ylabel('Active nodes')
    plt.grid(True, which='both')
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    plt.savefig(join(output_dir, f'counts.svg'), format='SVG')
    plt.close()


def save_counts_file(counts: List[int], experiment_name: str):
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    with open(join(output_dir, 'counts.csv'), 'w') as f:
        f.write('i,count\n')
        for i, count in enumerate(counts):
            f.write(f'{i},{count}\n')


if __name__ == '__main__':
    main()
