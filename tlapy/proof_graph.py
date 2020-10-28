"""Convert module theorem proofs to graph."""
# Copyright 2017-2020 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
import logging

import networkx as nx


INDENT = 4 * ' '
log = logging.getLogger(__name__)


def proof_graph(module_tree, nodes):
    """Return dependency graph of proof steps and theorems.

    The attribute `g.module_name` of the returned graph is
    the name of the module.

    @rtype: `networkx.DiGraph`
    """
    module_name = module_tree.name
    theorems = [
        unit for unit in module_tree.body
        if isinstance(unit, nodes.Theorem)]
    g = nx.DiGraph()
    for i, thm in enumerate(theorems):
        thm_name = _name_theorem(thm)
        # proof
        proof = thm.proof
        if not isinstance(proof, nodes.Omitted):
            g.add_node(
                thm_name,
                style='filled', fillcolor='yellow')
        if isinstance(proof, nodes.By):
            depends_on = _parse_by(proof, nodes)
            # no step names defined in this case,
            # only named facts
            for dep_name in depends_on:
                g.add_edge(thm_name, dep_name)
        elif isinstance(proof, nodes.Steps):
            level = 1
            umap = dict()
            qed_nd_id = _traverse_steps(
                proof, level, umap, g, nodes)
            g.add_edge(thm_name, qed_nd_id)
        elif isinstance(proof,
                (nodes.Obvious, nodes.Omitted)):
            pass
        else:
            raise ValueError(proof)
    g.module_name = module_name
    return g


def _name_theorem(theorem):
    """Return name of theorem."""
    thm_name = theorem.name
    if thm_name is None:
        thm_name = 'UnnamedTheorem{i}'.format(i=i)
    log.info('Theorem: {name}'.format(name=thm_name))
    return thm_name


def _traverse_steps(steps, level, umap, g, nodes):
    """Recursively extend proof graph `g` with steps."""
    for step in steps.steps:
        nd_id = _traverse_step(
            step, level, umap, g, nodes)
    qed_nd_id = _traverse_step(
        steps.qed_step, level, umap, g, nodes)
    return qed_nd_id


def _traverse_step(step, level, umap, g, nodes):
    """Recursively extend proof graph `g` with step."""
    nd_id = len(g)  # new node in the graph
    ref_name = _step_number_to_str(
        step, nd_id, nodes)
    umap[ref_name] = nd_id
    # add node to graph `g`
    label = _label_node(ref_name)
    g.add_node(nd_id, label=label)
    # proof
    _traverse_proof(step, nd_id, level, umap, g, nodes)
    _log_proof_level(level, ref_name)
    return nd_id


def _traverse_proof(step, nd_id, level, umap, g, nodes):
    """Recursively extend proof graph `g` with proof."""
    if not hasattr(step, 'proof'):
        return
    proof = step.proof
    if isinstance(proof, nodes.Steps):
        level_ = level + 1
        pf_qed = _traverse_steps(
            proof, level_, umap, g, nodes)
        g.add_edge(nd_id, pf_qed)
    elif isinstance(proof, nodes.By):
        depends_on = _parse_by(proof, nodes)
        for dep_name in depends_on:
            dep_nd_id = umap.get(dep_name, dep_name)
            g.add_edge(nd_id, dep_nd_id)
    elif isinstance(proof,
            (nodes.Obvious, nodes.Omitted)):
        pass
    else:
        raise ValueError(proof)


def _step_number_to_str(step, nd_id, nodes):
    """Return step number as `str`."""
    step_no = step.step_number
    if isinstance(step, nodes.Qed):
        ref_name = '$Qed_{i}'.format(i=nd_id)
    elif isinstance(step_no, nodes.Unnamed):
        ref_name = 'unnamed_step_{i}'.format(
            i=nd_id)
    elif isinstance(step_no, nodes.Named):
        ref_name = step_no.to_str(width=80)
        if ref_name.endswith('.'):
            ref_name = ref_name[:-1]
    else:
        raise ValueError(step, step_no)
    return ref_name


def _label_node(ref_name):
    """Return label for node described by `ref_name`."""
    if ref_name.startswith('$Qed'):
        label = 'QED'
    else:
        label = ref_name
    return label


def _parse_by(by, nodes):
    """Return `list` of names in facts."""
    depends_on = list()
    for fact in by.usable['facts']:
        if isinstance(fact, nodes.Opaque):
            ref_name = fact.name
            depends_on.append(ref_name)
    return depends_on


def _log_proof_level(level, ref_name):
    """Log message about proof graph node."""
    expr = (
        '{indent}{ref} '
        '(at proof level {level})').format(
            indent=level * INDENT,
            ref=ref_name,
            level=level)
    log.info(expr)


def dump_proof_graph(g, filename=None):
    """Dump graph `g` as PDF file.

    @type g: `networkx.DiGraph`
        with attribute `g.module_name`
    @type filename: `str`
    """
    module_name = g.module_name
    if not g:
        log.info('module {name} has no proof steps.'.format(
            name=module_name))
        return
    if filename is None:
        filename = 'proof_graph_{name}.pdf'.format(
            name=module_name)
    pd = nx.drawing.nx_pydot.to_pydot(g)
    pd.write_pdf(filename)
