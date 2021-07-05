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
    input_graph_ws_seeded = initial_seed(set_all_as_susceptible(input_graph_ws), 5, 5)

    experiments = [
        ('ws_inf1_0.1_inf2_0.1',
         input_graph_ws_seeded,
         {
             'infection_1': 0.1,
             'infection_2': 0.1,
             'removal': 0.5
         }),
        ('ws_inf1_0.1_inf2_0.2',
         input_graph_ws_seeded,
         {
             'infection_1': 0.1,
             'infection_2': 0.2,
             'removal': 0.5
         }),
        ('ws_inf1_0.2_inf2_0.1',
         input_graph_ws_seeded,
         {
             'infection_1': 0.2,
             'infection_2': 0.1,
             'removal': 0.5
         }),
        ('ws_inf1_0.2_inf2_0.2',
         input_graph_ws_seeded,
         {
             'infection_1': 0.2,
             'infection_2': 0.2,
             'removal': 0.5
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

            graph = update_step(graph, 'i1', values['infection_1'], values['removal'])
            graph = update_step(graph, 'i2', values['infection_2'], values['removal'])

            sirs.append(count_sir(graph))

            s, i1, i2, r = sirs[-1]
            print(f'\rstep:{iteration} S:{s} I1:{i1} I2:{i2} R:{r}   ', file=sys.stderr, end='', flush=True)
            if iteration >= 300 or i1 == 0 or i2 == 0 or r == graph.number_of_nodes():
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


def initial_seed(graph: Graph, seed_1_percent: int, seed_2_percent: int):
    nodes_count = graph.number_of_nodes()
    seed_1_target = int(nodes_count * seed_1_percent / 100)
    seed_2_target = int(nodes_count * seed_2_percent / 100)
    new_graph = initial_seed_type(graph, 'i1', seed_1_target)
    new_graph = initial_seed_type(new_graph, 'i2', seed_2_target)
    return new_graph


def initial_seed_type(graph: Graph, ix: str, count: int):
    new_graph = graph.copy()
    seeded = 0
    while seeded < count:
        n = str(randrange(new_graph.number_of_nodes()))
        node = new_graph.nodes[n]
        if not node['state'].startswith('i'):
            node['state'] = ix
            seeded += 1
    return new_graph


def update_step(graph: Graph, ix: str, infection_probability: float, removal_probability: float):
    new_graph = graph.copy()

    for n in graph.nodes:
        if graph.nodes[n]['state'] == ix:
            for neighbor in graph.neighbors(n):
                if graph.nodes[neighbor]['state'] in ('s', 'r') and random.uniform(0, 1) < infection_probability:
                    new_graph.nodes[neighbor]['state'] = ix

    for n in graph.nodes:
        if graph.nodes[n]['state'] == ix:
            if random.uniform(0, 1) < removal_probability:
                new_graph.nodes[n]['state'] = 'r'

    return new_graph


def get_colors(graph: Graph):
    return [get_color(graph.nodes[n]['state']) for n in graph.nodes]


def get_color(state: str):
    if state == 's':
        return 'blue'
    if state == 'i1':
        return 'red'
    if state == 'i2':
        return 'magenta'
    if state == 'r':
        return 'yellow'
    raise RuntimeError('Should not happen')


def count_sir(graph: Graph):
    node_states = graph.nodes(data='state')
    s = len(list(filter(lambda ns: ns[1] == 's', node_states)))
    i1 = len(list(filter(lambda ns: ns[1] == 'i1', node_states)))
    i2 = len(list(filter(lambda ns: ns[1] == 'i2', node_states)))
    r = len(list(filter(lambda ns: ns[1] == 'r', node_states)))
    return s, i1, i2, r


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


def save_sir_plot(sirs: List[Tuple[int, int, int, int]], experiment_name: str):
    s_vals = list(map(itemgetter(0), sirs))
    i1_vals = list(map(itemgetter(1), sirs))
    i2_vals = list(map(itemgetter(2), sirs))
    r_vals = list(map(itemgetter(3), sirs))

    plt.figure(figsize=(7, 7))
    plt.plot(s_vals, label='s')
    plt.plot(i1_vals, label='i1')
    plt.plot(i2_vals, label='i2')
    plt.plot(r_vals, label='r')
    plt.xlabel('Iteration')
    plt.ylabel('Node count')
    plt.grid(True)
    plt.legend()
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    plt.savefig(join(output_dir, f'sir.svg'), format='SVG')
    plt.close()


def save_sir_file(sirs: List[Tuple[int, int, int, int]], experiment_name: str):
    output_dir = join(RESULTS_OUTPUT_DIR, experiment_name)
    makedirs(output_dir, exist_ok=True)
    with open(join(output_dir, 'sir.csv'), 'w') as f:
        f.write('step,s,i1,i2,r\n')
        for step, sir in enumerate(sirs):
            s, i1, i2, r = sir
            f.write(f'{step},{s},{i1},{i2},{r}\n')


if __name__ == '__main__':
    main()
