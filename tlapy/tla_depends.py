#!/usr/bin/env python
"""Plot a graph of module dependencies."""
# Copyright 2018 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
import argparse
import os
import re

import networkx as nx


def dump_dependency_graph(fname):
    g = dependency_graph(fname)
    pd = nx.drawing.nx_pydot.to_pydot(g)
    pd.write_pdf('dependency_graph.pdf')


def dependency_graph(fname):
    module, ext = os.path.splitext(fname)
    assert ext == '.tla', ext
    stack = [module]
    g = nx.DiGraph()
    while stack:
        module = stack.pop()
        modules = find_dependencies(module)
        if modules is None:
            continue
        gen = ((module, v) for v in modules)
        g.add_edges_from(gen)
        stack.extend(modules)
    return g


def find_dependencies(module):
    fname = module + '.tla'
    if not os.path.isfile(fname):
        print('Cannot find file: {fname}'.format(fname=fname))
        return
    with open(fname, 'r') as f:
        lines = f.readlines()
    line, *_ = lines
    m = re.match('-* MODULE ([a-zA-Z0-9]*) -*', line)
    module_name, = m.groups()
    extends_modules = list()
    for line in lines:
        if not line.startswith('EXTENDS'):
            continue
        line = line.lstrip()
        s = line.split('EXTENDS', 1)[1]
        modules = comma_to_list(s)
        extends_modules.extend(modules)
    return extends_modules


def comma_to_list(s):
    r = s.split(',')
    r = [t.strip() for t in r]
    return r


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
        help='Root TLA+ module file name')
    args = parser.parse_args()
    return args.fname


if __name__ == '__main__':
    fname = parse_args()
    dump_dependency_graph(fname)
