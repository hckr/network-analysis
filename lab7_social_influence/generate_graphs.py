from os.path import dirname, join
import sys
import networkx as nx

OUTPUT_DIR = join(dirname(__file__), 'output')


def main():
    generate_big()
    generate_small()


def generate_big():
    graph = nx.watts_strogatz_graph(1000, 10, 0.2)
    nx.write_gml(graph, join(OUTPUT_DIR, 'ws.gml'))


def generate_small():
    graph = nx.watts_strogatz_graph(20, 5, 0.2)
    nx.write_gml(graph, join(OUTPUT_DIR, 'ws_small.gml'))


if __name__ == '__main__':
    main()
