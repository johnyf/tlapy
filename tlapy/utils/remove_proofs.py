#!/usr/bin/env python
"""Remove proofs from a TLA+ file to create a "header"."""
# Copyright 2017 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
from __future__ import division
import argparse
import math
import logging
import os
import re


PROOF_SUFFIX = '_proofs'
HEADER_SUFFIX = '_header'
log = logging.getLogger(__name__)


def main():
    """Entry point."""
    files, outdir = _parse_args()
    for fname in files:
        _remove_proofs(fname, outdir)


def _remove_proofs(fname, outdir):
    """Remove proofs from `fname` and dump result."""
    base, ext = os.path.splitext(fname)
    assert ext == '.tla', ext
    assert base.endswith(PROOF_SUFFIX), base
    with open(fname, 'r') as f:
        lines = f.readlines()
    new_lines = list()
    inside_proof = False
    last_indent = 0
    for line in lines:
        assert '\t' not in line, line
        s = line.lstrip()
        indent = len(line) - len(s)
        is_dedent = indent <= last_indent
        if is_dedent:
            inside_proof = False
        if re.match('<\d+>', s) is None:
            if inside_proof:
                continue
            new_lines.append(line)
            continue
        inside_proof = True  # omit lines
    # rename module by removing "_proofs"
    line = new_lines[0]
    assert 'MODULE' in line, line
    assert base in line, line
    new_module = base.replace(PROOF_SUFFIX, HEADER_SUFFIX)
    old_len = len(base) - len(PROOF_SUFFIX) + len(HEADER_SUFFIX)
    assert len(new_module) == old_len, (new_module, base)
    new_ln = line.replace(base, new_module)
    # add dashes
    missing_dashes = len(base) - len(new_module)
    half = missing_dashes / 2
    n = int(math.floor(half))
    m = int(math.ceil(half))
    assert n + m == missing_dashes, (n, m, missing_dashes)
    new_ln = n * '-' + new_ln[:-1] + m * '-' + '\n'
    assert len(new_ln) == len(line), (new_ln, line)
    new_lines[0] = new_ln
    # add notice that header has been auto-generated
    text = (
        '(* This file was automatically generated '
        'from the file:\n')
    line = (text + '    "{f}"\n*)\n').format(f=fname)
    new_lines.insert(0, line)
    # avoid overwriting source files
    header_fname = new_module + '.tla'
    header_path = os.path.join(outdir, header_fname)
    if os.path.isfile(header_path):
        with open(header_path, 'r') as f:
            line = f.readline()
        assert line.startswith(text), (line, text)
    # dump header
    print('Dump header to file "{h}"'.format(h=header_path))
    content = ''.join(new_lines)
    with open(header_path, 'w') as f:
        f.write(content)


def _parse_args():
    """Return input file names and output directory."""
    p = argparse.ArgumentParser()
    p.add_argument('input', nargs='+', type=str,
                   help="input `*.tla` files")
    p.add_argument('-o', '--outdir', type=str, default='.',
                   help='output directory')
    args = p.parse_args()
    files = args.input
    outdir = args.outdir
    log.info('input files: {fs}'.format(fs=files))
    log.info('output directory: {d}'.format(d=outdir))
    return files, outdir


if __name__ == '__main__':
    main()
