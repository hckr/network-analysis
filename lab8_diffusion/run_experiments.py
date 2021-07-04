import sys
from operator import itemgetter
from os import makedirs
from os.path import dirname, join
from random import randrange
from typing import List, Tuple
import random

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph

matplotlib.use('agg')  # headless matplotlib

CURRENT_DIR = dirname(__file__)
INPUT_DIR = join(CURRENT_DIR, '..', 'input')
RESULTS_OUTPUT_DIR = join(CURRENT_DIR, 'output', 'results')


def main():
    input_graph_ws = nx.read_gml(join(INPUT_DIR, 'ws.gml'))
    input_graph_ws_seeded = initial_seed(set_all_as_susceptible(input_graph_ws), 10)

    experiments = [
        ('ws_b_0.01_m_0.05',
         input_graph_ws_seeded,
         {
             'infection': 0.01,
             'removal': 0.05
         }),
        ('ws_b_0.01_m_0.1',
         input_graph_ws_seeded,
         {
             'infection': 0.01,
             'removal': 0.1
         }),
        ('ws_b_0.05_m_0.05',
         input_graph_ws_seeded,
         {
             'infection': 0.05,
             'removal': 0.05
         }),
        ('ws_b_0.05_m_0.1',
         input_graph_ws_seeded,
         {
             'infection': 0.05,
             'removal': 0.1
         }),
    ]

    for experiment_name, graph, values in experiments:

        print(f'Running experiment {experiment_name}... ', file=sys.stderr)

        save_graph(graph, experiment_name, 'initial_seeded')

        iteration = 0
        sirs = [count_sir(graph)]

        save_graph_image(graph, experiment_name, iteration)

        while True:
            iteration += 1

            graph = update_step(graph, values['infection'], values['removal'])

            sirs.append(count_sir(graph))

            s, i, r = sirs[-1]
            print(f'\rstep:{iteration} S:{s} I:{i} R:{r}   ', file=sys.stderr, end='', flush=True)
            if i == 0 or r == graph.number_of_nodes():
                save_graph_image(graph, experiment_name, iteration)
                break

            if iteration % 10 == 0:
                save_graph_image(graph, experiment_name, iteration)

        save_sir_plot(sirs, experiment_name)
        save_sir_file(sirs, experiment_name)

        print(f'\nDone.', file=sys.stderr)


def set_all_as_susceptible(graph: Graph):
    new_graph = graph.copy()
    for n in graph.nodes:
        new_graph.nodes[n]['state'] = 's'
    return new_graph


def initial_seed(graph: Graph, seed_percent: int):
    new_graph = graph.copy()
    seeded = 0
    nodes_count = new_graph.number_of_nodes()
    seed_target = int(nodes_count * seed_percent / 100)
    while seeded < seed_target:
        n = str(randrange(nodes_count))
        node = new_graph.nodes[n]
        if node['state'] != 'i':
            node['state'] = 'i'
            seeded += 1
    return new_graph


def update_step(graph: Graph, infection_probability: float, removal_probability: float):
    new_graph = graph.copy()

    for n in graph.nodes:
        if graph.nodes[n]['state'] == 'i':
            for neighbor in graph.neighbors(n):
                if graph.nodes[neighbor]['state'] == 's' and random.uniform(0, 1) < infection_probability:
                    new_graph.nodes[neighbor]['state'] = 'i'

    for n in graph.nodes:
        if graph.nodes[n]['state'] == 'i':
            if random.uniform(0, 1) < removal_probability:
                new_graph.nodes[n]['state'] = 'r'

    return new_graph


def get_colors(graph: Graph):
    return [get_color(graph.nodes[n]['state']) for n in graph.nodes]


def get_color(state: str):
    if state == 's':
        return 'blue'
    if state == 'i':
        return 'red'
    if state == 'r':
        return 'yellow'
    raise RuntimeError('Should not happen')


def count_sir(graph: Graph):
    node_states = graph.nodes(data='state')
    s = len(list(filter(lambda ns: ns[1] == 's', node_states)))
    i = len(list(filter(lambda ns: ns[1] == 'i', node_states)))
    r = len(list(filter(lambda ns: ns[1] == 'r', node_states)))
    return s, i, r


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


def save_sir_plot(sirs: List[Tuple[int, int, int]], experiment_name: str):
    s_vals = list(map(itemgetter(0), sirs))
    i_vals = list(map(itemgetter(1), sirs))
    r_vals = list(map(itemgetter(2), sirs))

    plt.figure(figsize=(7, 7))
    plt.plot(s_vals, label='s')
    plt.plot(i_vals, label='i')
    plt.plot(r_vals, label='r')
    plt.xlabel('Iteration')
    plt.ylabel('Node count')
    plt.grid(True)
    plt.legend()
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    plt.savefig(join(output_dir, f'sir.svg'), format='SVG')
    plt.close()


def save_sir_file(sirs: List[Tuple[int, int, int]], experiment_name: str):
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    with open(join(output_dir, 'sir.csv'), 'w') as f:
        f.write('step,s,i,r\n')
        for step, sir in enumerate(sirs):
            s, i, r = sir
            f.write(f'{step},{s},{i},{r}\n')


if __name__ == '__main__':
    main()
