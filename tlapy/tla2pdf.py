#!/usr/bin/env python3
"""Typeset TLA+ specifications using `tla2tex.TLA`."""
# Copyright 2017 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
import argparse
import datetime
import logging
import os
import subprocess


AUX_DIR = '__tlacache__/.aux'
TLA2TEX = 'tla2tex'
log = logging.getLogger(__name__)


def typeset_tla_files(files, tla2tex_options):
    """Typeset TLA+ files in `dirpath` as PDFs."""
    for tlafile in files:
        call_tla2tex(tlafile, tla2tex_options)


def call_tla2tex(tlafile, options):
    """Typeset `tlafile` using `TLA2TEX`."""
    base, ext = os.path.splitext(tlafile)
    assert ext == '.tla', tlafile
    pdf = base + '.pdf'
    if _is_newer(pdf, tlafile):
        print((
            'Skip "{tla}", because PDF file "{pdf}" '
            'is newer.').format(
                pdf=pdf, tla=tlafile))
        return
    if not os.path.isdir(AUX_DIR):
        os.makedirs(AUX_DIR)
    print('\nTypesetting file "{f}"'.format(f=tlafile))
    cmd = [TLA2TEX, '-shade', *options, tlafile]
    r = subprocess.call(cmd)
    assert r == 0, r


def _is_newer(target, source):
    """Return `True` if `target` newer than `source` file."""
    assert os.path.isfile(source), source
    if not os.path.isfile(target):
        return False
    t_src = os.stat(source)[8]
    t_tgt = os.stat(target)[8]
    _print_dates(source, target, t_src, t_tgt)
    return t_src < t_tgt


def _print_dates(source, target, t_src, t_tgt):
    s = _format_time(t_src)
    t = _format_time(t_tgt)
    log.info((
        'last modification dates:\n'
        '    Source ({source}): {s}\n'
        '    Target ({target}): {t}').format(
            source=source, target=target,
            s=s, t=t))


def _format_time(t):
    """Return time readable by humans."""
    return datetime.datetime.fromtimestamp(t)


def _parse_args():
    """Return input file names and options for `tla2tex.TeX`."""
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', nargs='+', type=str, required=True,
    help='''input `*.tla` files. Additional arguments are passed
        to `tla2tex.TLA`, for example:

    tla2pdf.py \
		-style $HOME/path/tlatex.sty \
		-i *.tla
    ''')
    args, unknown = p.parse_known_args()
    files = args.input
    tla2tex_options = unknown  # assume `tla2tex` knows other args
    log.info('input files: {fs}'.format(fs=files))
    log.info('options for `tla2tex.TeX`: {opt}'.format(
        opt=tla2tex_options))
    return files, tla2tex_options


if __name__ == '__main__':
    # log.addHandler(logging.StreamHandler())
    # log.setLevel(logging.DEBUG)
    files, tla2tex_options = _parse_args()
    typeset_tla_files(files, tla2tex_options)
